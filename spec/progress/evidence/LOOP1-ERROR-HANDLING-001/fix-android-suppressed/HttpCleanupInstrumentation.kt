package im.platform.client.ui
import im.platform.client.send.SendSession
import im.platform.client.sync.SyncHttps
import im.platform.client.sync.SyncFailure
import kotlinx.coroutines.*
import java.io.*
import java.net.*
import java.math.BigInteger
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.atomic.AtomicReference
import javax.net.ssl.HttpsURLConnection
import org.json.JSONObject

object HttpCleanupChecks {
 private var authPeer:HttpPeer?=null
 private val request=UUID.randomUUID().toString()
 private val session=SendSession(UUID.randomUUID().toString(),UUID.randomUUID().toString(),BigInteger.ONE,"controlled-only")
 private class HttpPeer(val primary:Throwable?=null,val cleanup:Throwable?=null,val disconnectFailure:Throwable?=null,val write:Boolean=false,val overflow:Boolean=false,val entered:CountDownLatch?=null,val release:CountDownLatch?=null):HttpsURLConnection(URL("https://localhost")){
  var closes=0;var disconnects=0;var writes=0
  override fun connect(){};override fun disconnect(){disconnects++;disconnectFailure?.let{throw it}};override fun usingProxy()=false
  override fun getCipherSuite()="controlled-fixture";override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null;override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray()
  override fun getOutputStream():OutputStream=object:ByteArrayOutputStream(){override fun write(b:ByteArray,off:Int,len:Int){writes++;if(write)primary?.let{throw it};super.write(b,off,len)};override fun close(){if(write){closes++;cleanup?.let{throw it}}}}
  override fun getResponseCode()=200;override fun getContentType()="application/json";override fun getHeaderField(name:String)=if(name=="Cache-Control")"no-store"else null
  override fun getInputStream():InputStream=object:ByteArrayInputStream(("{\"syncVersion\":\"1.0\",\"type\":\"sync.user.page\",\"requestId\":\""+request+"\",\"events\":[],\"nextCursor\":\"0\",\"hasMore\":false}").toByteArray()){
   override fun read(b:ByteArray,off:Int,len:Int):Int{entered?.countDown();release?.await();if(!write)primary?.let{throw it};if(overflow)return len;return super.read(b,off,len)}
   override fun close(){closes++;cleanup?.let{throw it}}
  }
 }
 private fun roots(error:Throwable):Set<Throwable>{val seen=java.util.Collections.newSetFromMap(java.util.IdentityHashMap<Throwable,Boolean>());fun walk(e:Throwable,ancestors:Set<Throwable>){check(e !in ancestors){"cyclic cause/suppressed graph"};if(!seen.add(e))return;e.cause?.let{walk(it,ancestors+e)};e.suppressed.forEach{walk(it,ancestors+e)}};walk(error,emptySet());return seen}
 private suspend fun failure(block:suspend()->Any?):Throwable=try{block();error("unexpected success")}catch(e:Throwable){if(e is IllegalStateException&&e.message=="unexpected success")throw e;e}
 suspend fun run(auth:Auth):Int {
  URL.setURLStreamHandlerFactory{scheme->if(scheme=="https")object:URLStreamHandler(){override fun openConnection(url:URL)=authPeer?:error("missing owned Auth connection")}else null}
  var checks=0
  for(api in listOf("sync","auth"))for(write in listOf(false,true))for(kind in listOf("plain","dual-known","mixed","unknown","disconnect-mixed")){
   val primary:Throwable=if(kind=="unknown")IllegalStateException("controlled primary")else IOException("controlled IO")
   val cleanup:Throwable?=when(kind){"dual-known"->IOException("controlled close IO");"mixed"->IllegalStateException("controlled close unknown");else->null}
   val disconnect=if(kind=="disconnect-mixed")IllegalStateException("controlled disconnect unknown")else null
   val peer=HttpPeer(primary,cleanup,disconnect,write);authPeer=peer
   val e=failure{if(api=="sync")SyncHttps("https://localhost",session,{peer},{request}).user("0")else auth.request("/fixture","POST",JSONObject(),false)}
   val graph=roots(e);check(primary in graph);cleanup?.let{check(it in graph)};disconnect?.let{check(it in graph)}
   if(kind in listOf("plain","dual-known")){if(api=="sync")check(e is SyncFailure&&e.kind=="transport")else check(e is ApiFailure&&e.kind=="connection_unavailable");check(e.cause===primary)}else{check(e !is SyncFailure&&e !is ApiFailure&&e !is IOException);if(kind=="unknown")check(e===primary)else check(e.cause===primary)}
   check(peer.closes==1&&peer.disconnects==1);checks++;println("checked "+checks)
  }
  // The real size guard raises the adapter's typed protocol failure inside use.
  for(api in listOf("sync","auth"))for(unknown in listOf(false,true)){
   val cleanup:Throwable=if(unknown)IllegalStateException("controlled protocol cleanup bug")else IOException("controlled protocol cleanup IO")
   val peer=HttpPeer(cleanup=cleanup,overflow=true);authPeer=peer
   val e=failure{if(api=="sync")SyncHttps("https://localhost",session,{peer},{request}).user("0")else auth.request("/fixture",authenticated=false)}
   val graph=roots(e);check(cleanup in graph);if(unknown){check(e is IllegalStateException);check(if(api=="sync")e.cause is SyncFailure else e.cause is ApiFailure)}else check(if(api=="sync")e is SyncFailure&&e.kind=="protocol" else e is ApiFailure&&e.kind=="invalid_server_response")
   check(peer.closes==1&&peer.disconnects==1);checks++;println("checked "+checks)
  }
  // Success is delivered only after mandatory disconnect has completed.
  for(api in listOf("sync","auth"))for(kind in listOf("success","known","unknown")){
   val disconnect:Throwable?=when(kind){"known"->IOException("controlled disconnect IO");"unknown"->IllegalStateException("controlled disconnect bug");else->null}
   val peer=HttpPeer(disconnectFailure=disconnect);authPeer=peer
   val block:suspend()->Any?={if(api=="sync")SyncHttps("https://localhost",session,{peer},{request}).user("0")else auth.request("/fixture",authenticated=false)}
   if(disconnect==null)block()else{val e=failure(block);check(disconnect in roots(e));if(kind=="unknown")check(e===disconnect)else check(if(api=="sync")e is SyncFailure else e is ApiFailure)}
   check(peer.closes==1&&peer.disconnects==1);checks++;println("checked "+checks)
  }
  for(unknown in listOf(false,true)){
   val primary=IOException("controlled cancelled read");val close:Throwable=if(unknown)IllegalStateException("controlled inactive cleanup bug")else IOException("controlled inactive close IO")
   val entered=CountDownLatch(1);val release=CountDownLatch(1);val peer=HttpPeer(primary,close,entered=entered,release=release)
   val escaped=AtomicReference<Throwable?>();val scope=CoroutineScope(SupervisorJob()+Dispatchers.Default+CoroutineExceptionHandler{_,e->escaped.set(e)})
   val operation=scope.launch{SyncHttps("https://localhost",session,{peer},{request}).user("0")}
   withContext(Dispatchers.IO){check(entered.await(10,java.util.concurrent.TimeUnit.SECONDS))};operation.cancel();release.countDown();operation.join()
   repeat(500){if(peer.closes==1&&(!unknown||escaped.get()!=null))return@repeat;delay(10)}
   if(unknown){val e=escaped.get()?:error("inactive unknown swallowed");check(e is IllegalStateException);check(primary in roots(e)&&close in roots(e))}else check(escaped.get()==null)
   check(peer.closes==1&&peer.disconnects==1);scope.cancel();checks++;println("checked "+checks)
  }
  return checks
 }
}

class HttpCleanupInstrumentation:android.app.Instrumentation(){
 override fun onCreate(args:android.os.Bundle?){super.onCreate(args);start()}
 override fun onStart(){val result=android.os.Bundle();try{val checks=runBlocking{HttpCleanupChecks.run(Auth("https://localhost",Preferences(targetContext)))};result.putString("result","PASS");result.putInt("checks",checks);result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putString("scope","Actual production SyncHttps/Auth controlled read/write/close/disconnect roots, typed protocol size guard, known failure projection, inactive cancellation, cleanups once, successful controls");finish(android.app.Activity.RESULT_OK,result)}catch(e:Throwable){result.putString("result","FAIL");result.putString("failureType",e.javaClass.name);result.putString("failure",e.message);finish(android.app.Activity.RESULT_CANCELED,result)}}
}

