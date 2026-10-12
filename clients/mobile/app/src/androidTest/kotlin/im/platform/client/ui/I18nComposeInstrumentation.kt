package im.platform.client.ui
import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.os.Bundle
import android.view.KeyEvent
import android.view.accessibility.AccessibilityNodeInfo
import im.platform.client.MainActivity
import im.platform.client.ui.i18n.*
import java.io.File
import java.security.MessageDigest
import javax.net.ssl.HttpsURLConnection
import org.json.JSONArray
import org.json.JSONObject

/** Actual MainActivity/Compose/ViewModel/Preferences + controlled real backend. No injected state. */
class I18nComposeInstrumentation:Instrumentation(){
 private var args=Bundle();private var activity:Activity?=null;private var checks=0
 private lateinit var directory:File
 private val captures=JSONArray()
 override fun onCreate(arguments:Bundle?){super.onCreate(arguments);args=arguments?:Bundle();start()}
 private fun verify(ok:Boolean){check(ok){"I18N Compose assertion "+checks+" failed"};checks++}
 private fun await(condition:()->Boolean){val deadline=android.os.SystemClock.elapsedRealtime()+20000;while(!condition()){check(android.os.SystemClock.elapsedRealtime()<deadline){"I18N actual UI/state timeout"};Thread.sleep(100)}}
 private fun root():AccessibilityNodeInfo?{uiAutomation.clearCache();return uiAutomation.rootInActiveWindow}
 private fun find(node:AccessibilityNodeInfo?,text:String):AccessibilityNodeInfo?{
  if(node==null)return null
  if(node.text?.toString()==text||node.contentDescription?.toString()==text)return node
  for(i in 0 until node.childCount)find(node.getChild(i),text)?.let{return it};return null
 }
 private fun clickable(node:AccessibilityNodeInfo?,text:String,parent:AccessibilityNodeInfo?=null):AccessibilityNodeInfo?{
  if(node==null)return null;val current=if(node.isClickable)node else parent
  if((node.text?.toString()?.lineSequence()?.any{it==text}==true||node.contentDescription?.toString()==text)&&current!=null)return current
  for(i in 0 until node.childCount)clickable(node.getChild(i),text,current)?.let{return it};return null
 }
 private fun scroll(node:AccessibilityNodeInfo?):Boolean{
  if(node==null)return false
  if(node.isScrollable&&node.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD))return true
  for(i in 0 until node.childCount)if(scroll(node.getChild(i)))return true;return false
 }
 private fun click(text:String){
  var target:AccessibilityNodeInfo?=null
  repeat(12){if(target==null){target=clickable(root(),text)?.takeIf{it.isEnabled};if(target==null){scroll(root());waitForIdleSync();Thread.sleep(150)}}}
  val node=checkNotNull(target){"Actual clickable UI absent: "+text};verify(node.isEnabled);verify(node.performAction(AccessibilityNodeInfo.ACTION_CLICK));waitForIdleSync();Thread.sleep(200)
 }
 private fun fill(label:String,value:String){
  await{find(root(),label)!=null};var node=find(root(),label)!!
  while(node.actionList.none{it.id==AccessibilityNodeInfo.ACTION_SET_TEXT})node=node.parent?:error("Actual editable UI absent")
  val b=Bundle();b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,value)
  verify(node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,b));waitForIdleSync()
 }
 private fun hideKeyboard(){var shown=false;runOnMainSync{shown=activity?.window?.decorView?.rootWindowInsets?.isVisible(android.view.WindowInsets.Type.ime())==true};if(shown){uiAutomation.injectInputEvent(KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_BACK),true);uiAutomation.injectInputEvent(KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_BACK),true);Thread.sleep(300)}}
 private fun vm():WorkspaceViewModel{val owner=activity as MainActivity;val key=owner.viewModelStore.keys().single{it.endsWith("WorkspaceViewModel")};return androidx.lifecycle.ViewModelProvider(owner)[key,WorkspaceViewModel::class.java]}
 private fun text(key:String)=translate(vm().state.value.language,key)
 private fun launch(){activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));waitForIdleSync();await{(activity as MainActivity).viewModelStore.keys().any{it.endsWith("WorkspaceViewModel")}}}
 private fun close(){activity?.let{runOnMainSync{it.finish()};waitForIdleSync()};activity=null;Thread.sleep(300)}
 private fun hash(file:File):String{val digest=MessageDigest.getInstance("SHA-256");file.inputStream().use{stream->val bytes=ByteArray(8192);while(true){val n=stream.read(bytes);if(n<0)break;digest.update(bytes,0,n)}};return digest.digest().joinToString(""){"%02x".format(it.toInt()and 255)}}
 private fun snapshot(s:WorkspaceState)=JSONObject().put("locale",s.language).put("theme",s.appearance.theme).put("fontSize",s.appearance.fontSize).put("density",s.appearance.density).put("selected",s.selected).put("messageCount",s.messages.size).put("sessionPresent",s.session!=null).put("connection",s.connection).put("sync",s.sync)
 private fun capture(name:String,step:String){
  waitForIdleSync();uiAutomation.waitForIdle(200,5000)
  val image=checkNotNull(uiAutomation.takeScreenshot());val file=File(directory,name+".png");check(!file.exists())
  file.outputStream().use{verify(image.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it))}
  captures.put(snapshot(vm().state.value).put("file",file.name).put("sha256",hash(file)).put("width",image.width).put("height",image.height).put("step",step));image.recycle()
 }
 private fun restore(store:android.content.SharedPreferences,original:Map<String,*>){
  val editor=store.edit().clear()
  for((key,value) in original)when(value){is String->editor.putString(key,value);is Int->editor.putInt(key,value);is Long->editor.putLong(key,value);is Float->editor.putFloat(key,value);is Boolean->editor.putBoolean(key,value);is Set<*>->editor.putStringSet(key,value.filterIsInstance<String>().toSet())}
  check(editor.commit());check(store.all==original)
 }
 override fun onStart(){
  val result=Bundle();var trust:UiRefFixtureTrust?=null
  if(args.getString("ownedFixture")!="i18n-owned-api34"){result.putString("failure","Verified owned API34 fixture required");finish(Activity.RESULT_CANCELED,result);return}
  val appearanceStore=targetContext.getSharedPreferences("appearance",0);val secureStore=targetContext.getSharedPreferences("secure-refresh",0)
  val appearanceOriginal=appearanceStore.all;val secureOriginal=secureStore.all
  try{
   require(args.getString("ownedFixture")=="i18n-owned-api34"){"Verified owned fixture required"};verify(android.os.Build.VERSION.SDK_INT==34)
   val run=checkNotNull(args.getString("stateRun"));require(Regex("[A-Za-z0-9-]{1,80}").matches(run))
   val source=checkNotNull(args.getString("sourceSha"));require(Regex("[a-f0-9]{40}").matches(source))
   val apk=checkNotNull(args.getString("apkSha256"));require(Regex("[a-f0-9]{64}").matches(apk));verify(hash(File(targetContext.applicationInfo.sourceDir))==apk)
   directory=File(targetContext.getExternalFilesDir(null),"i18n/"+run);check(!directory.exists());check(directory.mkdirs())
   args.getString("uiRefCA")?.let{trust=UiRefFixtureTrust.install(it,checkNotNull(args.getString("caSha256")))}
   val probe=java.net.URL("https://localhost:8443/__infra/health").openConnection() as HttpsURLConnection
   try{probe.connectTimeout=10000;probe.readTimeout=10000;probe.instanceFollowRedirects=false;verify(probe.responseCode==200);probe.inputStream.close()}finally{probe.disconnect()}
   val prefs=Preferences(targetContext);prefs.saveLanguage("en");prefs.saveAppearance(Appearance("warm",22,1.2f));launch();await{vm().state.value.language=="en"}
   capture("en-login","Actual MainActivity with real locale/appearance adapters")
   val user=checkNotNull(args.getString("avery"));val peer=checkNotNull(args.getString("peerName"));val expected=checkNotNull(args.getString("expectedConversation"));val history=checkNotNull(args.getString("historyText"))
   fill(text("auth.username"),user);fill(text("auth.password"),"fixture-password-not-a-real-secret");hideKeyboard();click(text("auth.signIn"))
   await{vm().state.value.session!=null&&vm().state.value.connection=="ready"};click(peer);await{vm().state.value.selected==expected&&vm().state.value.messages.any{it[2]==history&&it[3]=="SENT"}}
   val baseline=vm().state.value;val baselineRows=baseline.messages.map{it.toList()};val draft="English 简体中文 日本語 draft";fill(text("chat.message"),draft);hideKeyboard();await{find(root(),draft)!=null}
   for(locale in locales){
    runOnMainSync{vm().language(locale)};await{vm().state.value.language==locale&&prefs.loadLanguage()==locale};await{find(root(),text("chat.message"))!=null};await{find(root(),draft)!=null}
    val observed=vm().state.value;verify(observed.selected==expected);verify(observed.session?.sessionId==baseline.session?.sessionId);verify(observed.appearance==baseline.appearance);verify(observed.messages==baselineRows);verify(find(root(),draft)!=null);verify(find(root(),peer)!=null)
    capture(locale+"-chat-preserved","Actual application language intent while conversation selected; draft/selection/history/session/appearance retained")
   }
   click(text("nav.back"));await{vm().state.value.selected.isEmpty()};click(text("nav.settings"))
   for((index,locale) in locales.withIndex()){
    await{find(root(),languageEntry)!=null};click(languageNames[index]);await{vm().state.value.language==locale&&prefs.loadLanguage()==locale};verify(vm().state.value.session?.sessionId==baseline.session?.sessionId);verify(vm().state.value.appearance==baseline.appearance)
    capture(locale+"-settings","Actual Settings fixed language entry and native preference write")
    for(page in listOf("friends","ai","plugin")){click(text("nav."+page));capture(locale+"-"+page,"Actual Compose navigation");click(text("nav.settings"))}
   }
   click(text("nav.chat"));click(peer);await{vm().state.value.selected==expected};verify(find(root(),draft)!=null);capture("ja-JP-navigation-draft","Settings/navigation did not discard Shell-owned draft")
   close();launch();await{vm().state.value.language=="ja-JP"};verify(prefs.loadLanguage()=="ja-JP");capture("ja-JP-activity-recreated-login","Actual activity/ViewModel recreation loads persisted locale; not process restart claim")
   click(text("auth.resume"));await{vm().state.value.session!=null&&vm().state.value.connection=="ready"};click(peer);await{vm().state.value.selected==expected&&vm().state.value.messages.any{it[2]==history&&it[3]=="SENT"}};capture("ja-JP-resumed-history","Actual secure refresh/Repository/Sync with controlled real backend")
   result.putString("result","PASS actual Compose locale/navigation/draft/selection/native preferences/activity recreation/controlled backend")
   File(directory,"manifest.json").writeText(JSONObject().put("result","CHECKS_PASSED_CLEANUP_PENDING").put("source_sha",source).put("source_is_clean_committed_candidate",args.getString("cleanCandidate")=="1").put("installed_apk_sha256",apk).put("runtime","owned API34 actual MainActivity/Compose; real controlled HTTPS backend").put("captures",captures).toString(2))
  }catch(error:Throwable){if(::directory.isInitialized){uiAutomation.takeScreenshot()?.let{image->File(directory,"failure.png").outputStream().use{image.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it)};image.recycle()};val tree=StringBuilder();fun dump(node:AccessibilityNodeInfo?,depth:Int){if(node==null)return;tree.append(" ".repeat(depth)).append(node.className).append(" enabled=").append(node.isEnabled).append(" clickable=").append(node.isClickable).append(" text=").append(if(node.isPassword)"[masked]" else node.text).append(" description=").append(node.contentDescription).append("\n");for(i in 0 until node.childCount)dump(node.getChild(i),depth+1)};dump(root(),0);File(directory,"failure-tree.txt").writeText(tree.toString())};result.putString("failure",error.stackTraceToString());if(::directory.isInitialized)File(directory,"failure.json").writeText(JSONObject().put("result","FAIL").put("error",error.stackTraceToString()).put("captures",captures).toString(2))}
  finally{
   val cleanupErrors=mutableListOf<String>()
   try{if(activity!=null&&vm().state.value.session!=null){runOnMainSync{vm().logout()};await{vm().state.value.session==null&&!vm().state.value.busy}}}catch(error:Throwable){cleanupErrors.add("logout: "+error.stackTraceToString())}
   try{close()}catch(error:Throwable){cleanupErrors.add("close: "+error.stackTraceToString())}
   try{restore(appearanceStore,appearanceOriginal)}catch(error:Throwable){cleanupErrors.add("appearance: "+error.stackTraceToString())}
   try{restore(secureStore,secureOriginal)}catch(error:Throwable){cleanupErrors.add("credentials: "+error.stackTraceToString())}
   try{trust?.close()}catch(error:Throwable){cleanupErrors.add("TLS: "+error.stackTraceToString())}
   if(cleanupErrors.isNotEmpty())result.putString("failure",(result.getString("failure")?:"")+"; Cleanup failed: "+cleanupErrors.joinToString("\n"))
  }
  if(::directory.isInitialized){File(directory,"result.json").writeText(JSONObject().put("result",if(result.containsKey("failure"))"FAIL" else "PASS").put("assertions",checks).put("cleanupComplete",!result.containsKey("failure")).put("failure",result.getString("failure")).toString(2));val manifest=File(directory,"manifest.json");if(manifest.exists())manifest.writeText(JSONObject(manifest.readText()).put("result",if(result.containsKey("failure"))"FAIL" else "PASS").put("cleanupComplete",!result.containsKey("failure")).toString(2))}
  result.putInt("assertions",checks);finish(if(result.containsKey("failure"))Activity.RESULT_CANCELED else Activity.RESULT_OK,result)
 }
}
