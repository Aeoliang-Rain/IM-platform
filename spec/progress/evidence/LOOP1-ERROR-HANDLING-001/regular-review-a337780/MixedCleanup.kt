import im.platform.client.sync.*
import im.platform.client.send.SendSession
import kotlinx.coroutines.runBlocking
import java.io.*
import java.net.URL
import java.math.BigInteger
import javax.net.ssl.HttpsURLConnection
class Peer(url:URL,val primary:IOException,val cleanup:RuntimeException):HttpsURLConnection(url){
 override fun connect(){};override fun disconnect(){};override fun usingProxy()=false
 override fun getCipherSuite()="fixture";override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null
 override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray()
 override fun getOutputStream()=ByteArrayOutputStream()
 override fun getResponseCode()=200
 override fun getContentType()="application/json"
 override fun getHeaderField(name:String)=if(name=="Cache-Control")"no-store"else null
 override fun getInputStream()=object:InputStream(){override fun read():Int=throw primary;override fun close(){throw cleanup}}
}
fun main()=runBlocking {
 val primary=IOException("controlled read failure");val cleanup=IllegalStateException("controlled cleanup bug")
 val session=SendSession("fixture","fixture",BigInteger.ONE,"fixture")
 val http=SyncHttps("https://localhost/",session,{Peer(it,primary,cleanup)},{"fixture"})
 try{http.user("0");error("unexpected success")}catch(error:Exception){
  println("OBSERVED "+error.javaClass.name+" kind="+(error as? SyncFailure)?.kind)
  println("primary suppressed cleanup identity="+(primary.suppressed.singleOrNull()===cleanup))
  println("projected cause="+error.cause+" suppressedCount="+error.suppressed.size)
  check(error is SyncFailure && error.kind=="transport")
  check(primary.suppressed.single()===cleanup)
  check(error.cause==null && error.suppressed.isEmpty())
  println("REPRODUCED: actual production SyncHttps discards unknown cleanup root and projects mixed failure as known transport")
 }
}
