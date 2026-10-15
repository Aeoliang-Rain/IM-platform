package im.platform.client.send
import java.net.*
import java.io.*
import javax.net.ssl.*
import java.util.concurrent.*
import java.util.concurrent.atomic.*
class Peer(val primary:Throwable?,val cleanup:Throwable?):SSLSocket(){
 var closes=0
 val gate=CountDownLatch(1);val started=CountDownLatch(1);var block=false;var text=false
 override fun startHandshake(){started.countDown();if(block){check(gate.await(10,TimeUnit.SECONDS));throw IOException("cancelled transport")};primary?.let{throw it}}

 override fun close(){closes++;gate.countDown();cleanup?.let{throw it}}
 private val output=ByteArrayOutputStream()
 override fun getInputStream():InputStream=object:InputStream(){var data:ByteArray?=null;var n=0;override fun read():Int{if(data==null){val key=output.toString("US-ASCII").split("\r\n").first{it.startsWith("Sec-WebSocket-Key:")}.substringAfter(":").trim();val accept=java.util.Base64.getEncoder().encodeToString(java.security.MessageDigest.getInstance("SHA-1").digest((key+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").toByteArray()));data=("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: $accept\r\n\r\n").toByteArray()+if(text)byteArrayOf(0x81.toByte(),1,65,0x88.toByte(),0)else byteArrayOf(0x88.toByte(),0)};val d=data!!;return if(n<d.size)d[n++].toInt() and 255 else -1}}
 override fun getOutputStream():OutputStream=output
 override fun getSupportedCipherSuites()=arrayOf("TLS_AES_128_GCM_SHA256")
 override fun getEnabledCipherSuites()=supportedCipherSuites
 override fun setEnabledCipherSuites(s:Array<String>){}
 override fun getSupportedProtocols()=arrayOf("TLSv1.2")
 override fun getEnabledProtocols()=supportedProtocols
 override fun setEnabledProtocols(s:Array<String>){}
 override fun getSession():SSLSession=throw IllegalStateException("unused session")
 override fun addHandshakeCompletedListener(l:HandshakeCompletedListener){}
 override fun removeHandshakeCompletedListener(l:HandshakeCompletedListener){}
 override fun setUseClientMode(v:Boolean){}
 override fun getUseClientMode()=true
 override fun setNeedClientAuth(v:Boolean){}
 override fun getNeedClientAuth()=false
 override fun setWantClientAuth(v:Boolean){}
 override fun getWantClientAuth()=false
 override fun setEnableSessionCreation(v:Boolean){}
 override fun getEnableSessionCreation()=true
}
class Factory(val peer:Peer):SSLSocketFactory(){
 override fun getDefaultCipherSuites()=peer.supportedCipherSuites
 override fun getSupportedCipherSuites()=peer.supportedCipherSuites
 override fun createSocket(s:Socket,h:String,p:Int,c:Boolean)=peer
 override fun createSocket(h:String,p:Int)=peer
 override fun createSocket(h:String,p:Int,l:InetAddress,q:Int)=peer
 override fun createSocket(h:InetAddress,p:Int)=peer
 override fun createSocket(h:InetAddress,p:Int,l:InetAddress,q:Int)=peer
}

object WssCleanupChecks {
 private fun roots(root:Throwable):Set<Throwable>{val seen=java.util.Collections.newSetFromMap(java.util.IdentityHashMap<Throwable,Boolean>());val active=java.util.Collections.newSetFromMap(java.util.IdentityHashMap<Throwable,Boolean>());fun walk(e:Throwable){check(active.add(e)){"cyclic Throwable graph"};if(seen.add(e)){e.cause?.let(::walk);e.suppressed.forEach(::walk)};active.remove(e)};walk(root);return seen}
 fun run():Int {
  val previous=Thread.getDefaultUncaughtExceptionHandler();var checks=0
  try {
   fun case(name:String,primary:Throwable?,cleanup:Throwable?,observer:Throwable?=null,at:String="",cancel:Boolean=false){
    val peer=Peer(if(at.isEmpty())primary else null,cleanup);peer.text=at=="message";peer.block=cancel
    val surfaced=AtomicReference<Throwable?>();val done=CountDownLatch(1);val ended=AtomicInteger();val opened=AtomicInteger();val messages=AtomicInteger()
    val expectedFailure=(primary!=null && (primary !is IOException || at.isNotEmpty())) || (cleanup!=null && cleanup !is IOException) || observer!=null
    Thread.setDefaultUncaughtExceptionHandler{thread,error->if(thread.name=="im-wss"){surfaced.set(error);done.countDown()}else previous?.uncaughtException(thread,error)}
    val ws=Wss("wss://localhost/v1/ws",{opened.incrementAndGet();if(at=="opened")throw primary!!},{messages.incrementAndGet();if(at=="message")throw primary!!},{ended.incrementAndGet();observer?.let{throw it};if(!expectedFailure)done.countDown()},Factory(peer))
    if(cancel){check(peer.started.await(10,TimeUnit.SECONDS));ws.close()}
    check(done.await(10,TimeUnit.SECONDS)){name+" timeout"}
    val error=surfaced.get()
    check((error!=null)==expectedFailure){name+" failure classification"};check(ended.get()==1){name+" ended count"};ws.close();check(peer.closes==1){name+" close count ${peer.closes}"}
    if(error!=null){val all=roots(error);listOfNotNull(primary,cleanup,observer).forEach{check(it in all){name+" missing original root"}};if(listOfNotNull(primary,cleanup,observer).distinct().size==1)check(error===listOfNotNull(primary,cleanup,observer).first()){name+" single identity"}}
    if(primary==null && !cancel)check(opened.get()==1);if(at=="message")check(messages.get()==1)
    checks++;println("WSS-CHECK $name PASS")
   }
   case("unknown-primary-unknown-close",IllegalStateException("primary"),IllegalStateException("close"))
   case("Error-primary-unknown-close",AssertionError("primary"),IllegalStateException("close"))
   case("known-IO-primary-unknown-close",IOException("primary"),IllegalStateException("close"))
   case("unknown-primary-only",IllegalStateException("primary"),null)
   case("Error-primary-only",AssertionError("primary"),null)
   case("known-IO-primary",IOException("primary"),null)
   case("dual-known-IO",IOException("primary"),IOException("close"))
   case("unknown-primary-known-close",IllegalStateException("primary"),IOException("close"))
   case("normal",null,null)
   case("close-only-unknown",null,IllegalStateException("close"))
   case("close-only-Error",null,AssertionError("close"))
   case("close-only-known",null,IOException("close"))
   case("ended-unknown",null,null,IllegalStateException("ended"))
   case("ended-IO-is-observer",null,null,IOException("ended"))
   case("primary-close-ended",AssertionError("primary"),IllegalStateException("close"),IOException("ended"))
   case("opened-unknown",IllegalStateException("opened"),null,at="opened")
   case("opened-IO-is-observer",IOException("opened"),null,at="opened")
   case("message-unknown",IllegalStateException("message"),null,at="message")
   case("message-IO-is-observer",IOException("message"),null,at="message")
   val same=IllegalStateException("same identity");case("same-primary-close",same,same)
   case("cancel-known",null,null,cancel=true)
   return checks
  } finally {Thread.setDefaultUncaughtExceptionHandler(previous)}
 }
}

class WssCleanupInstrumentation:android.app.Instrumentation(){
 override fun onCreate(args:android.os.Bundle?){super.onCreate(args);start()}
 override fun onStart(){val result=android.os.Bundle();try{result.putInt("wssCleanupChecks",WssCleanupChecks.run());result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putString("result","PASS");finish(android.app.Activity.RESULT_OK,result)}catch(error:Throwable){result.putString("result","FAIL");result.putString("error",error.stackTraceToString());finish(android.app.Activity.RESULT_CANCELED,result)}}
}
