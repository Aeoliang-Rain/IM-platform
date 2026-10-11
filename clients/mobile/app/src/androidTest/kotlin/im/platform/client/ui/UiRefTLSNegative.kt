package im.platform.client.ui
import android.app.Instrumentation
import android.app.Activity
import android.os.Bundle
import java.net.URL
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLSocket
import javax.net.ssl.SSLSocketFactory
/** Fresh process, no fixture helper: original SDK trust must reject the same live CA. */
class UiRefTLSNegative:Instrumentation(){
 override fun onCreate(arguments:Bundle?){super.onCreate(arguments);start()}
 override fun onStart(){
  val result=Bundle()
  try{
   check(java.security.Security.getProvider("UIRefFixtureCacheRefresh")==null)
   val c=URL("https://localhost:8443/__infra/health").openConnection() as HttpsURLConnection
   c.connectTimeout=10000;c.readTimeout=10000
   var rejected=false
   try{c.responseCode}catch(_:javax.net.ssl.SSLHandshakeException){rejected=true}finally{c.disconnect()}
   check(rejected);result.putString("freshDefaultSDKHTTPSRejected","PASS")
   val s=(SSLSocketFactory.getDefault() as SSLSocketFactory).createSocket("localhost",8443) as SSLSocket
   rejected=false
   try{s.soTimeout=10000;val p=s.sslParameters;p.endpointIdentificationAlgorithm="HTTPS";s.sslParameters=p;s.startHandshake()}catch(_:javax.net.ssl.SSLHandshakeException){rejected=true}finally{s.close()}
   check(rejected);result.putString("freshDefaultSDKSocketRejected","PASS");result.putString("result","PASS");result.putInt("pid",android.os.Process.myPid())
  }catch(e:Throwable){result.putString("result","FAIL");result.putString("failure",e.toString())}
  finish(if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED,result)
 }
}
