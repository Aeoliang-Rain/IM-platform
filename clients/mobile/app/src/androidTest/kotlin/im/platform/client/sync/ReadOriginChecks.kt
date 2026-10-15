package im.platform.client.sync

import android.app.Application
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import im.platform.client.send.*
import im.platform.client.storage.Repository
import im.platform.client.ui.WorkspaceViewModel
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import org.json.JSONArray
import org.json.JSONObject
import java.io.*
import java.math.BigInteger
import java.net.URL
import java.security.cert.Certificate
import java.util.UUID
import javax.net.ssl.HttpsURLConnection
import kotlin.coroutines.intrinsics.suspendCoroutineUninterceptedOrReturn

// Runs in the existing actual API34 Sync instrumentation, on owned databases.
internal class ReadOriginChecks(private val context:Context) {
    private var assertions=0
    private fun verify(value:Boolean){check(value);assertions++}
    private suspend fun until(test:()->Boolean){repeat(500){if(test())return;delay(10)};error("read-origin condition timed out")}
    private val dbField=Repository::class.java.getDeclaredField("db").apply {isAccessible=true}
    private fun reopen(repo:Repository,user:String){dbField.set(repo,SQLiteDatabase.openDatabase(context.getDatabasePath("im-$user.sqlite").path,null,SQLiteDatabase.OPEN_READWRITE))}
    private class Response(private val body:()->String):HttpsURLConnection(URL("https://localhost/")) {
        override fun connect(){};override fun disconnect(){};override fun usingProxy()=false
        override fun getCipherSuite()="owned-read-fixture"
        override fun getLocalCertificates():Array<Certificate>?=null
        override fun getServerCertificates():Array<Certificate> = emptyArray()
        override fun getOutputStream()=ByteArrayOutputStream()
        override fun getResponseCode()=200
        override fun getHeaderField(name:String?)=if(name.equals("Cache-Control",true))"no-store"else null
        override fun getContentType()="application/json"
        override fun getInputStream():InputStream=ByteArrayInputStream(body().toByteArray())
    }
    private suspend fun history(vm:WorkspaceViewModel,repo:Repository,g:Long):Unit=suspendCoroutineUninterceptedOrReturn { continuation ->
        val method=WorkspaceViewModel::class.java.getDeclaredMethod("updateList",Repository::class.java,java.lang.Long.TYPE,kotlin.coroutines.Continuation::class.java).apply {isAccessible=true}
        try {method.invoke(vm,repo,g,continuation)}catch(error:java.lang.reflect.InvocationTargetException){throw error.cause!!}
    }
    suspend fun run():Int {
        val user=UUID.randomUUID().toString();val conversation=UUID.randomUUID().toString()
        val repo=Repository(context,user);repo.initialize()
        val session=SendSession(user,UUID.randomUUID().toString(),BigInteger.ONE,"owned-read-only")
        val id=UUID.randomUUID().toString()
        val http=SyncHttps("https://localhost/",session,{Response {JSONObject().put("syncVersion","1.0").put("type","sync.user.page").put("requestId",id).put("events",JSONArray()).put("nextCursor","0").put("hasMore",false).toString()}},{id})
        val sender=SendViewModel(repo,session);val sync=SyncViewModel(sender,repo,http)
        repo.close()
        try {
            // Real SDK exceptions at the cursor/list/history/contiguous origins.
            for(read in listOf<()->Any>({repo.cursor()},{repo.conversationIds()},{repo.messages(conversation)},{repo.contiguous(conversation)})) {
                try {repositoryRead(read);error("closed SDK read accepted")}catch(error:SendStorageFailure){verify(error.cause is IllegalStateException);verify(error.cause!!.message!!.startsWith("attempt to re-open an already-closed object:"))}
            }
            try {sync.synchronize();error("closed Sync accepted")}catch(error:SendStorageFailure){verify(error.cause is IllegalStateException)}
            verify(sync.state.value.status=="failed" && sync.state.value.error=="storage")
            // Same queue resumes after the known external read fault is repaired.
            reopen(repo,user)
            SyncViewModel::class.java.getDeclaredMethod("enqueue").apply {isAccessible=true}.invoke(sync)
            until {sync.state.value.status=="idle"};verify(repo.cursor()=="0");verify(repo.conversationIds().isEmpty());verify(repo.contiguous(conversation)==0L)
            // Unknown read/mapping failures and cancellation retain original identity.
            for(original in listOf(IllegalStateException("read mapping bug"),android.database.sqlite.SQLiteException("no such table: schema_bug"),CancellationException("owned cancellation"))) {
                try {repositoryRead<Any>{throw original};error("unknown swallowed")}catch(error:Exception){verify(error===original)}
            }
            val bad=IllegalStateException("attempt to re-open an already-closed object: observer spoof")
            val fail=WorkspaceViewModel::class.java.getDeclaredMethod("fail",Exception::class.java,java.lang.Boolean.TYPE).apply {isAccessible=true}
            val workspace=withContext(Dispatchers.Main){WorkspaceViewModel(context.applicationContext as Application)}
            delay(100)
            for(active in listOf(true,false))try{fail.invoke(workspace,bad,active);error("observer spoof swallowed")}catch(error:java.lang.reflect.InvocationTargetException){verify(error.cause===bad)}
            repo.close()
            withContext(Dispatchers.Main){history(workspace,repo,0L)}
            verify(workspace.state.value.error=="Conversation history unavailable")
            val stale=withContext(Dispatchers.Main){WorkspaceViewModel(context.applicationContext as Application)};delay(100)
            withContext(Dispatchers.Main){history(stale,repo,1L)};verify(stale.state.value.error==null)
            reopen(repo,user)
            // Actual SDK schema failure remains untagged at the Workspace consumer.
            var schema:Exception?=null
            try {repositoryRead {repo.query("SELECT cursor FROM __owned_missing_table")}}catch(error:Exception){schema=error}
            verify(schema is android.database.sqlite.SQLiteException && schema !is SendStorageFailure)
            for(active in listOf(true,false))try{fail.invoke(stale,schema,active);error("schema read swallowed")}catch(error:java.lang.reflect.InvocationTargetException){verify(error.cause===schema)}
            val db=dbField.get(repo) as SQLiteDatabase
            db.execSQL("DROP TABLE messages")
            for(g in listOf(0L,1L))try{withContext(Dispatchers.Main){history(stale,repo,g)};error("history schema swallowed")}catch(error:android.database.sqlite.SQLiteException){verify(error !is SendStorageFailure);verify(stale.state.value.error==null)}
            // The unchanged constructor failure still projects the same error and
            // inactive result; only its existing capture boundary moved.
            val blockedUser=UUID.randomUUID().toString();val blocked=context.getDatabasePath("im-$blockedUser.sqlite");verify(blocked.mkdir())
            val account=WorkspaceViewModel::class.java.getDeclaredMethod("accountRepository",String::class.java).apply {isAccessible=true}
            try {
                val initialization=try{account.invoke(stale,blockedUser);error("blocked initialization accepted")}catch(error:java.lang.reflect.InvocationTargetException){error.cause as SendStorageFailure}
                verify(initialization.cause is android.database.sqlite.SQLiteException)
                fail.invoke(stale,initialization,false);verify(stale.state.value.error==null)
                fail.invoke(stale,initialization,true);verify(stale.state.value.error=="Operation unavailable")
            }finally {verify(blocked.delete())}
            for(vm in listOf(workspace,stale))WorkspaceViewModel::class.java.getDeclaredMethod("onCleared").apply {isAccessible=true}.invoke(vm)
            // Retirement suppresses only known expired work and cannot revive a pull.
            sync.dispose();repo.close();sync.synchronize();verify(sync.state.value.status=="retired")
        } finally {context.deleteDatabase("im-$user.sqlite")}
        return assertions
    }
}
