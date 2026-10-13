package im.platform.client.ui
import android.app.Activity
import android.app.Instrumentation
import android.os.Bundle
import im.platform.client.send.SendSession
import im.platform.client.send.SendViewModel
import im.platform.client.send.WireFailure
import im.platform.client.send.Wire as SendWire
import im.platform.client.sync.SyncHttps
import im.platform.client.sync.SyncFailure
import im.platform.client.storage.Repository
import kotlinx.coroutines.*
import org.json.JSONObject
import im.platform.client.send.SendSocket
import java.math.BigInteger
import java.util.UUID

class ErrorHandlingInstrumentation:Instrumentation(){
 private suspend fun until(test:()->Boolean){repeat(500){if(test())return;delay(10)};error("controlled runtime condition timed out")}
 private class Utf8Peer(url:java.net.URL):javax.net.ssl.HttpsURLConnection(url){override fun connect(){};override fun disconnect(){};override fun usingProxy()=false;override fun getCipherSuite()="controlled-fixture";override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null;override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray();override fun getOutputStream()=java.io.ByteArrayOutputStream();override fun getInputStream()=java.io.ByteArrayInputStream(byteArrayOf(0xff.toByte()));override fun getResponseCode()=200;override fun getHeaderField(name:String)=if(name=="Cache-Control")"no-store"else null;override fun getContentType()="application/json"}
 private class Peer:SendSocket {lateinit var open:()->Unit;lateinit var message:(String)->Unit;val frames=java.util.concurrent.CopyOnWriteArrayList<JSONObject>();override fun send(text:String){frames.add(JSONObject(text))};override fun close(){}}
 override fun onCreate(args:Bundle?){super.onCreate(args);start()}
 override fun onStart(){
  val result=Bundle()
  try{runBlocking{
   val original=IllegalStateException("controlled internal HTTPS adapter bug")
   val user=UUID.randomUUID().toString();val session=SendSession(user,UUID.randomUUID().toString(),BigInteger.ONE,"controlled-test-only")
   val unknown=SyncHttps("https://localhost/",session,connection={throw original})
   try{unknown.user("0");error("unknown HTTPS error swallowed")}catch(error:Exception){check(error===original){"original unknown error replaced"}}
   try{SyncHttps("https://localhost/",session,connection={Utf8Peer(it)}).user("0");error("invalid UTF8 accepted")}catch(error:SyncFailure){check(error.kind=="protocol")}
   try{SendWire.decode("{}");error("invalid wire accepted")}catch(_:WireFailure){}
   val row=listOf<String?>("controlled-request",user,"controlled required body","SENDING",null,null,null)
   check(im.platform.client.ui.components.messageBody(row)=="controlled required body")
   for(state in listOf("SENDING","SENT","FAILED"))check(im.platform.client.ui.components.messageState(state)=="chat."+state.lowercase())
   check(im.platform.client.ui.components.messageIdentity(row)=="controlled-request")
   val server=row.toMutableList();server[0]=null;server[4]="controlled-server";check(im.platform.client.ui.components.messageIdentity(server)=="controlled-server")
   for(kind in listOf("state","body","identity")){
    val bad=row.toMutableList();if(kind=="body")bad[2]=null;if(kind=="identity"){bad[0]=null;bad[4]=null}
    var failed=false;try{when(kind){"state"->im.platform.client.ui.components.messageState("UNKNOWN");"body"->im.platform.client.ui.components.messageBody(bad);else->im.platform.client.ui.components.messageIdentity(bad)}}catch(_:IllegalStateException){failed=true};check(failed)
   }
   val searching=WorkspaceState();check(!im.platform.client.ui.components.noSearchMatch(searching,"alice",null));check(!im.platform.client.ui.components.noSearchMatch(searching.copy(error="unavailable"),"alice","alice"));check(im.platform.client.ui.components.noSearchMatch(searching.copy(searchComplete=true),"alice","alice"));check(!im.platform.client.ui.components.noSearchMatch(searching.copy(searchComplete=true),"bob","alice"))
   val repo=Repository(targetContext,user);repo.initialize()
   val send=SendViewModel(repo,session)
   val detach=send.observeDelivery{_,_->throw original}
   val method=SendViewModel::class.java.getDeclaredMethod("delivered",String::class.java,java.lang.Long.TYPE);method.isAccessible=true
   try{method.invoke(send,UUID.randomUUID().toString(),1L);error("delivery observer swallowed")}catch(error:java.lang.reflect.InvocationTargetException){check(error.cause===original)}
   detach();send.dispose()
   val peer=Peer();val vm=SendViewModel(repo,session,{_,open,message,_->peer.also{it.open=open;it.message=message}},10000)
   val conversation=UUID.randomUUID().toString();vm.openConversation(conversation);vm.connect("wss://localhost/");peer.open();until{peer.frames.isNotEmpty()}
   val bind=peer.frames.last().getString("requestId");peer.message(SendWire.envelope("auth.ack",bind,JSONObject().put("status","bound").put("userId",user).put("sessionId",session.sessionId).put("clientType","MOBILE").put("sessionEpoch",1)));until{vm.state.value.connection=="ready"}
   val observerBug=IllegalStateException("controlled mixed observer bug");val escaped=java.util.concurrent.atomic.AtomicReference<Throwable?>();val previous=Thread.getDefaultUncaughtExceptionHandler()
   Thread.setDefaultUncaughtExceptionHandler{thread,error->if(error===observerBug)escaped.set(error)else previous?.uncaughtException(thread,error)}
   val unsubscribe=vm.observeDelivery{_,_->throw observerBug}
   try{val request=vm.send(conversation,"controlled mixed callback");peer.message(SendWire.envelope("message.ack",request,JSONObject().put("status","committed").put("conversationId",conversation).put("messageId",UUID.randomUUID().toString()).put("seq",1).put("createdAt","2026-10-03T00:00:00Z")));until{escaped.get()!=null};check(escaped.get()===observerBug);check(vm.state.value.error!="storage");check(repo.messages(conversation).single()[3]=="SENT")}finally{unsubscribe();Thread.setDefaultUncaughtExceptionHandler(previous);vm.dispose()}
   repo.close();targetContext.deleteDatabase("im-$user.sqlite")
  };result.putString("result","PASS");result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putString("scope","actual Android unknown HTTPS identity, invalid wire and direct non-storage delivery callback; message invariant and search-state mapping; mixed observer unknown original escapes actual coroutine; genuine SQLite recovery covered by SendInstrumentation");finish(Activity.RESULT_OK,result)}catch(error:Throwable){result.putString("result","FAIL");result.putString("failureType",error.javaClass.simpleName);finish(Activity.RESULT_CANCELED,result)}
 }
}
