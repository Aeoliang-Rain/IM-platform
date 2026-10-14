import im.platform.client.sync.*
import im.platform.client.ui.*
import im.platform.client.send.SendSession
import kotlinx.coroutines.runBlocking
import java.io.*
import java.net.*
import java.math.BigInteger
import javax.net.ssl.HttpsURLConnection
class Peer(url:URL,val p:Exception,val close:Exception,val write:Boolean=false):HttpsURLConnection(url){
 override fun connect(){};override fun disconnect(){};override fun usingProxy()=false
 override fun getCipherSuite()="fixture";override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null;override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray()
 override fun getOutputStream():OutputStream=if(write)object:OutputStream(){override fun write(b:Int){throw p};override fun close(){throw close}}else ByteArrayOutputStream()
 override fun getResponseCode()=200;override fun getContentType()="application/json";override fun getHeaderField(n:String)=if(n=="Cache-Control")"no-store"else null
 override fun getInputStream()=object:InputStream(){override fun read():Int=throw p;override fun close(){throw close}}
}
var peer:Peer?=null
fun main()=runBlocking {
 URL.setURLStreamHandlerFactory{scheme->if(scheme=="https")object:URLStreamHandler(){override fun openConnection(url:URL)=peer!!}else null}
 for(write in listOf(false,true)){
  val p=IOException("controlled IO");val u=IllegalStateException("controlled cleanup");peer=Peer(URL("https://localhost"),p,u,write)
  try{Auth("https://localhost",Preferences()).request("/fixture","POST",org.json.JSONObject(),false);error("success")}catch(e:Exception){check(e is ApiFailure&&e.kind=="connection_unavailable");check(p.suppressed.single()===u);check(e.cause==null);println("REPRO Auth ${if(write)"write"else "read"} IO+unknown close => causefree known ApiFailure")}
 }
 for(p in listOf<Exception>(IOException("controlled IO"),SyncFailure("protocol"))){
  val u=IllegalStateException("controlled cleanup");val fixture=Peer(URL("https://localhost"),p,u)
  try{SyncHttps("https://localhost",SendSession("f","f",BigInteger.ONE,"f"),{fixture},{"f"}).user("0");error("success")}catch(e:Exception){check(e is SyncFailure);check(p.suppressed.single()===u);println("REPRO Sync ${p.javaClass.simpleName}+unknown close => known SyncFailure ${e.kind}")}
 }
}
