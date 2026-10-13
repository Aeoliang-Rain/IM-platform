package im.platform.client.ui

import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.os.Process
import android.os.SystemClock
import android.view.accessibility.AccessibilityNodeInfo
import im.platform.client.MainActivity
import im.platform.client.ui.i18n.translate
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import org.json.JSONObject

/** Parent force-stops between phases. No session restore/login, DB access, or injected state. */
class I18nRestartInstrumentation : Instrumentation() {
    private var args = Bundle()
    private var activity: MainActivity? = null
    override fun onCreate(arguments: Bundle?) { super.onCreate(arguments); args = arguments ?: Bundle(); start() }
    private fun hash(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val bytes = ByteArray(8192)
            while (true) { val n = input.read(bytes); if (n < 0) break; digest.update(bytes, 0, n) }
        }
        return digest.digest().joinToString("") { "%02x".format(it.toInt() and 255) }
    }
    private fun await(condition: () -> Boolean) {
        val end = SystemClock.elapsedRealtime() + 20000
        while (!condition()) { check(SystemClock.elapsedRealtime() < end); Thread.sleep(100) }
    }
    private fun root(): AccessibilityNodeInfo? { uiAutomation.clearCache(); return uiAutomation.rootInActiveWindow }
    private fun contains(node: AccessibilityNodeInfo?, text: String): Boolean {
        if (node == null) return false
        if (node.text?.toString() == text || node.contentDescription?.toString() == text) return true
        for (i in 0 until node.childCount) if (contains(node.getChild(i), text)) return true
        return false
    }
    private fun vm(): WorkspaceViewModel {
        val owner = checkNotNull(activity)
        val key = owner.viewModelStore.keys().single { it.endsWith("WorkspaceViewModel") }
        return androidx.lifecycle.ViewModelProvider(owner)[key, WorkspaceViewModel::class.java]
    }
    private fun launch(locale: String, appearance: Appearance) {
        activity = startActivitySync(Intent(targetContext, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) as MainActivity
        waitForIdleSync()
        await { activity!!.viewModelStore.keys().any { it.endsWith("WorkspaceViewModel") } }
        await { vm().state.value.language == locale && vm().state.value.appearance == appearance }
        check(Preferences(targetContext).loadLanguage() == locale)
        check(Preferences(targetContext).loadAppearance() == appearance)
        // Fresh unauthenticated MainActivity, actual Compose accessibility, no mock VM/state.
        check(vm().state.value.session == null && vm().state.value.offlineAccount == null)
        await { val node = root(); node?.packageName?.toString() == targetContext.packageName &&
            contains(node, translate(locale, "auth.openTitle")) && contains(node, translate(locale, "auth.username")) }
    }
    private fun close() { activity?.let { runOnMainSync { it.finish() }; waitForIdleSync() }; activity = null }
    private fun atomic(file: File, data: JSONObject) {
        val temporary = File(file.parentFile, file.name + ".pending")
        FileOutputStream(temporary).use { output -> output.write(data.toString(2).toByteArray(Charsets.UTF_8)); output.fd.sync() }
        check(temporary.renameTo(file))
    }
    // Only approved scalar appearance/language keys, with their exact types preserved.
    private fun encode(map: Map<String, *>): JSONObject {
        check(map.keys.all { it in setOf("theme", "fontSize", "density", "language") })
        val result = JSONObject()
        for ((key, value) in map) {
            val type = when (value) { is String -> "String"; is Int -> "Int"; is Float -> "Float"; else -> error("Unsupported owned preference type") }
            result.put(key, JSONObject().put("type", type).put("value", value))
        }
        return result
    }
    private fun decode(data: JSONObject): Map<String, Any> {
        val result = mutableMapOf<String, Any>()
        for (key in data.keys()) {
            check(key in setOf("theme", "fontSize", "density", "language"))
            val entry = data.getJSONObject(key)
            result[key] = when (entry.getString("type")) {
                "String" -> entry.getString("value"); "Int" -> entry.getInt("value"); "Float" -> entry.getDouble("value").toFloat()
                else -> error("Unsupported snapshot type")
            }
        }
        return result
    }
    private fun restore(store: SharedPreferences, original: Map<String, Any>) {
        val editor = store.edit().clear()
        for ((key, value) in original) when (value) { is String -> editor.putString(key, value); is Int -> editor.putInt(key, value); is Float -> editor.putFloat(key, value); else -> error("Unsupported snapshot type") }
        check(editor.commit()); check(store.all == original)
    }
    override fun onStart() {
        val result = Bundle()
        // Reject unowned invocations before reading/writing any preference or test state.
        if (args.getString("ownedFixture") != "i18n-owned-api34" || args.getString("serial") != "emulator-5556" || android.os.Build.VERSION.SDK_INT != 34) {
            result.putString("failure", "OWNED_API34_EMULATOR_5556_REQUIRED"); finish(Activity.RESULT_CANCELED, result); return
        }
        var store: SharedPreferences? = null
        var original: Map<String, Any>? = null
        var state: JSONObject? = null
        var stateFile: File? = null
        var directory: File? = null
        var failure: String? = null
        var cleanupFailure: String? = null
        var cleanupComplete = false
        var step = "arguments"
        val report = JSONObject().put("result", "PENDING").put("pid", Process.myPid()).put("api", 34)
        val phase = args.getString("phase") ?: ""
        try {
            require(phase in listOf("setup", "verify", "invalid", "verify-invalid", "restore"))
            val run = checkNotNull(args.getString("stateRun")); require(Regex("i18n-restart-[a-z0-9-]{1,48}").matches(run))
            val attempt = args.getString("attempt") ?: "first"; require(Regex("[a-z0-9-]{1,24}").matches(attempt))
            val source = checkNotNull(args.getString("sourceSha")); require(Regex("[a-f0-9]{40}").matches(source))
            val tree = checkNotNull(args.getString("sourceTreeSha256")); require(Regex("[a-f0-9]{64}").matches(tree))
            val apk = checkNotNull(args.getString("apkSha256")); require(Regex("[a-f0-9]{64}").matches(apk))
            val testApk = checkNotNull(args.getString("testApkSha256")); require(Regex("[a-f0-9]{64}").matches(testApk))
            val clean = args.getString("cleanCandidate") == "1"
            require(clean != (args.getString("wip") == "1")); require(args.getString("expectedOriginalEmpty") == "1")
            check(targetContext.packageName == "im.platform.client" && context.packageName == "im.platform.client.test")
            check(hash(File(targetContext.applicationInfo.sourceDir)) == apk)
            check(hash(File(context.applicationInfo.sourceDir)) == testApk)
            report.put("phase", phase).put("stateRun", run).put("source_sha", source).put("source_tree_sha256", tree)
                .put("source_is_clean_committed_candidate", clean).put("source_binding", "parent declared; APK bytes checked here")
                .put("installed_apk_sha256", apk).put("installed_test_apk_sha256", testApk).put("serial", "emulator-5556")
                .put("runtime", "actual API34 MainActivity/Compose/WorkspaceViewModel/Preferences; parent force-stop receipts required")
            step = "snapshot"
            val internal = File(targetContext.filesDir, "i18n-restart/" + run)
            stateFile = File(internal, "state.json")
            if (phase != "setup") {
                state = JSONObject(stateFile.readText(Charsets.UTF_8))
                check(state.getString("sourceSha") == source && state.getString("sourceTreeSha256") == tree && state.getString("apkSha256") == apk && state.getString("testApkSha256") == testApk)
                check(state.getBoolean("cleanCandidate") == clean)
                original = decode(state.getJSONObject("original")); check(original.isEmpty())
            }
            val external = checkNotNull(targetContext.getExternalFilesDir(null))
            directory = File(external, "i18n-restart/" + run + "/" + phase + "-" + attempt)
            check(!directory.exists()); check(directory.mkdirs())
            store = targetContext.getSharedPreferences("appearance", 0)
            if (phase == "setup") {
                check(!internal.exists()) // Never replace an existing run or its recovery snapshot.
                check(store.all.isEmpty()) // Exact known factory-owned fixture; unknown keys fail before mutation.
                original = decode(encode(store.all))
                check(internal.mkdirs())
                val appearance = Preferences(targetContext).loadAppearance()
                state = JSONObject().put("original", encode(original)).put("sourceSha", source).put("sourceTreeSha256", tree)
                    .put("apkSha256", apk).put("testApkSha256", testApk).put("cleanCandidate", clean).put("stage", "SNAPSHOTTED")
                    .put("theme", appearance.theme).put("fontSize", appearance.fontSize).put("density", appearance.density)
                atomic(stateFile, state) // Persist recovery before mutating language.
            }
            val saved = checkNotNull(state)
            val appearance = Appearance(saved.getString("theme"), saved.getInt("fontSize"), saved.getDouble("density").toFloat())
            val untouched = checkNotNull(original).filterKeys { it != "language" }
            when (phase) {
                "setup" -> { step = "save-ja-JP"; Preferences(targetContext).saveLanguage("ja-JP"); saved.put("setupPid", Process.myPid()) }
                "verify" -> { step = "fresh-ja-JP-pid"; check(saved.getString("stage") == "SETUP"); check(saved.getInt("setupPid") != Process.myPid()); report.put("previous_pid", saved.getInt("setupPid")); saved.put("verifyPid", Process.myPid()) }
                "invalid" -> { step = "seed-invalid"; check(saved.getString("stage") == "VERIFIED"); check(store.edit().putString("language", "EN").commit()); saved.put("invalidPid", Process.myPid()) }
                "verify-invalid" -> { step = "fresh-en-pid"; check(saved.getString("stage") == "INVALID"); check(saved.getInt("invalidPid") != Process.myPid()); report.put("previous_pid", saved.getInt("invalidPid")); check(store.getString("language", null) == "EN") }
                "restore" -> { step = "restore-original" }
            }
            check(store.all.filterKeys { it != "language" } == untouched)
            if (phase in listOf("setup", "verify", "verify-invalid")) {
                val locale = if (phase == "verify-invalid") "en" else "ja-JP"
                step = "actual-MainActivity-" + locale; launch(locale, appearance)
                check(store.all.filterKeys { it != "language" } == untouched)
                step = "capture-" + locale
                waitForIdleSync(); uiAutomation.waitForIdle(200, 5000)
                val image = checkNotNull(uiAutomation.takeScreenshot())
                try {
                    val png = File(directory, locale + "-login.png")
                    png.outputStream().use { check(image.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, it)) }
                    report.put("capture", JSONObject().put("file", png.name).put("sha256", hash(png)).put("width", image.width).put("height", image.height)
                        .put("locale", vm().state.value.language).put("theme", vm().state.value.appearance.theme).put("fontSize", vm().state.value.appearance.fontSize).put("density", vm().state.value.appearance.density))
                } finally { image.recycle() }
            }
            saved.put("stage", when (phase) { "setup" -> "SETUP"; "verify" -> "VERIFIED"; "invalid" -> "INVALID"; "verify-invalid" -> "INVALID_VERIFIED"; else -> saved.getString("stage") })
            atomic(stateFile, saved)
        } catch (error: Throwable) {
            failure = step + ":" + error.javaClass.simpleName // Fixed stage + type only; no credential/exception prose.
        } finally {
            try { close() } catch (error: Throwable) { cleanupFailure = "activity-close:" + error.javaClass.simpleName }
            if (failure != null || cleanupFailure != null || phase == "restore") {
                try {
                    if (original != null) {
                        val ownedStore = store ?: targetContext.getSharedPreferences("appearance", 0)
                        restore(ownedStore, original); cleanupComplete = true
                        if (state != null && stateFile != null) { state.put("stage", if (failure == null && cleanupFailure == null) "RESTORED" else "FAILED_RESTORED"); atomic(stateFile, state) }
                    } else if (phase != "setup") { cleanupFailure = (cleanupFailure ?: "") + "snapshot-unavailable" }
                } catch (error: Throwable) { cleanupComplete = false; cleanupFailure = (cleanupFailure ?: "") + ";restore:" + error.javaClass.simpleName }
            }
        }
        report.put("result", if (failure != null || cleanupFailure != null) "FAIL" else if (phase == "restore") "RESTORED" else "PHASE_PASSED_CLEANUP_PENDING")
            .put("cleanupComplete", cleanupComplete).put("failure", failure ?: JSONObject.NULL).put("cleanup_failure", cleanupFailure ?: JSONObject.NULL)
        try {
            directory?.let { atomic(File(it, "manifest.json"), report) }
        } catch (error: Throwable) {
            result.putString("evidenceFailure", "manifest:" + error.javaClass.simpleName)
            // Evidence failure after a successful phase must also restore; preserve both failures.
            try { if (original != null) { restore(store ?: targetContext.getSharedPreferences("appearance", 0), original); cleanupComplete = true } }
            catch (cleanup: Throwable) { cleanupComplete = false; result.putString("cleanupFailure", "restore:" + cleanup.javaClass.simpleName) }
        }
        result.putString("phaseResult", report.getString("result")); result.putInt("pid", Process.myPid()); result.putBoolean("cleanupComplete", cleanupComplete)
        failure?.let { result.putString("failure", it) }; cleanupFailure?.let { result.putString("cleanupFailure", it) }
        finish(if (result.containsKey("failure") || result.containsKey("cleanupFailure") || result.containsKey("evidenceFailure")) Activity.RESULT_CANCELED else Activity.RESULT_OK, result)
    }
}
