package im.platform.client.ui
import android.content.Context
import android.content.ContextWrapper
import android.content.SharedPreferences
import kotlinx.coroutines.runBlocking
import java.io.*
import java.net.*
import java.lang.reflect.Proxy
import javax.net.ssl.HttpsURLConnection

class RefreshCleanupInstrumentation:android.app.Instrumentation(){
 override fun onCreate(args:android.os.Bundle?){super.onCreate(args);start()}
 override fun onStart(){val result=android.os.Bundle();try{val checks=runBlocking{runChecks()};result.putString("result","PASS");result.putInt("checks",checks);result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putString("scope","Actual Auth.refresh request401 lifecycle and Preferences encrypted read/remove commit boundary; exact primary+cleanup roots, known IO and unknown propagation, normal controls");finish(android.app.Activity.RESULT_OK,result)}catch(e:Throwable){result.putString("result","FAIL");result.putString("failureType",e.javaClass.name);result.putString("failure",e.message);finish(android.app.Activity.RESULT_CANCELED,result)}}
 private var status=401
 private class Peer(url:URL,private val status:Int):HttpsURLConnection(url){
  override fun connect(){};override fun disconnect(){};override fun usingProxy()=false
  override fun getCipherSuite()="controlled";override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null;override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray()
  override fun getOutputStream():OutputStream=ByteArrayOutputStream();override fun getResponseCode()=status;override fun getContentType()="application/json"
  override fun getErrorStream():InputStream=ByteArrayInputStream("{\"error\":{\"code\":\"AUTH_SESSION_REVOKED\"}}".toByteArray())
 }
 private fun roots(error:Throwable):Set<Throwable>{val seen=java.util.Collections.newSetFromMap(java.util.IdentityHashMap<Throwable,Boolean>());fun walk(e:Throwable,ancestors:Set<Throwable>){check(e !in ancestors){"cycle"};if(!seen.add(e))return;e.cause?.let{walk(it,ancestors+e)};e.suppressed.forEach{walk(it,ancestors+e)}};walk(error,emptySet());return seen}
 private suspend fun runChecks():Int{
  URL.setURLStreamHandlerFactory{scheme->if(scheme=="https")object:URLStreamHandler(){override fun openConnection(url:URL)=Peer(url,status)}else null}
  var count=0
  for(kind in listOf("normal","commit-false","unknown","Error","nonexpiry")){
   var armed=false;var removes=0;var cleanup:Throwable?=null
   val unknown=IllegalStateException("controlled credential cleanup unknown")
   val supplied:Throwable?=when(kind){"unknown"->unknown;"Error"->AssertionError("controlled credential cleanup Error");else->null}
   val files=mutableListOf<SharedPreferences>()
   val context=object:ContextWrapper(targetContext){override fun getSharedPreferences(name:String,mode:Int):SharedPreferences{
    val original=super.getSharedPreferences("refresh-cleanup-controlled-"+kind+"-"+name,mode);files.add(original)
    if(name!="secure-refresh")return original
    return Proxy.newProxyInstance(SharedPreferences::class.java.classLoader,arrayOf(SharedPreferences::class.java)){_,method,args->
     if(method.name!="edit")method.invoke(original,*(args?:emptyArray()))else{
      val editor=original.edit()
      Proxy.newProxyInstance(SharedPreferences.Editor::class.java.classLoader,arrayOf(SharedPreferences.Editor::class.java)){proxy,m,a->
       if(armed && m.name=="remove")removes++
       if(armed && m.name=="commit"){
        supplied?.let{cleanup=it;throw it}
        if(kind=="commit-false")false else m.invoke(editor,*(a?:emptyArray()))
       }else{val value=m.invoke(editor,*(a?:emptyArray()));if(value===editor)proxy else value}
      }
     }
    } as SharedPreferences
   }}
   try{
    val prefs=Preferences(context);val endpoint="https://fixture.invalid";val slot=endpoint+"/11111111-1111-4111-8111-111111111111/22222222-2222-4222-8222-222222222222"
    prefs.write(slot,"controlled-only");prefs.write(endpoint+"/current",slot);val owner=Auth(endpoint,prefs);check(owner.savedAccount()=="11111111-1111-4111-8111-111111111111");status=if(kind=="nonexpiry")403 else 401;armed=true
    val error=try{owner.refresh();error("unexpected success")}catch(e:Throwable){e};val graph=roots(error);val primary=graph.filterIsInstance<ApiFailure>().single()
    check(primary.kind==if(kind=="nonexpiry")"AUTH_SESSION_REVOKED" else "session_expired");check(owner.session==null)
    when(kind){
     "normal"->{check(error===primary);check(removes==2)}
     "nonexpiry"->{check(error===primary);check(removes==0)}
     "commit-false"->{check(error is IOException);check(error.cause===primary);val c=error.suppressed.single();check(c is IOException&&c.message=="Credential cleanup failed");check(removes==1)}
     else->{check(error is IllegalStateException);check(error.cause===primary);check(error.suppressed.single()===cleanup);check(supplied in graph);check(removes==1)}
    }
    count++;println("REFRESH-CLEANUP "+kind+" PASS")
   }finally{armed=false;files.forEach{check(it.edit().clear().commit())}}
  }
  return count
 }
}
