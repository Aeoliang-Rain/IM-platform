package im.platform.client.ui
import android.app.Application
import android.content.ContextWrapper
import android.content.SharedPreferences
import im.platform.client.send.*
import im.platform.client.storage.Repository
import im.platform.client.sync.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import java.io.*
import java.net.*
import java.lang.reflect.Proxy
import java.math.BigInteger
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import javax.net.ssl.HttpsURLConnection

class RefreshOwnerInstrumentation:android.app.Instrumentation(){
 override fun onCreate(args:android.os.Bundle?){super.onCreate(args);start()}
 override fun onStart(){val result=android.os.Bundle();try{val checks=runBlocking{runChecks()};result.putString("result","PASS");result.putInt("checks",checks);result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putString("scope","Actual Workspace.refresh/Auth/Preferences and existing Sync/Send owner retirement; controlled HTTP and secure commit producer, native Android runtime");finish(android.app.Activity.RESULT_OK,result)}catch(e:Throwable){e.printStackTrace();result.putString("result","FAIL");result.putString("failureType",e.javaClass.name);result.putString("failure",e.message);finish(android.app.Activity.RESULT_CANCELED,result)}}
 private fun field(target:Any,name:String)=target.javaClass.getDeclaredField(name).also{it.isAccessible=true}
 private fun get(target:Any,name:String)=field(target,name).get(target)
 private fun set(target:Any,name:String,value:Any?){field(target,name).set(target,value)}
 private var responseStatus=401
 private var entered:CountDownLatch?=null;private var release:CountDownLatch?=null
 private inner class Peer(url:URL):HttpsURLConnection(url){
  override fun connect(){};override fun disconnect(){};override fun usingProxy()=false
  override fun getCipherSuite()="controlled";override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null;override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray()
  override fun getOutputStream():OutputStream=ByteArrayOutputStream();override fun getResponseCode():Int{entered?.countDown();release?.let{check(it.await(10,TimeUnit.SECONDS))};return responseStatus};override fun getContentType()="application/json"
  override fun getInputStream():InputStream=ByteArrayInputStream("""{"session":{"sessionId":"22222222-2222-4222-8222-222222222222","userId":"11111111-1111-4111-8111-111111111111","clientType":"MOBILE","sessionEpoch":2,"status":"ACTIVE"},"tokens":{"accessToken":"rotated-controlled","accessTokenExpiresInSeconds":300,"refreshToken":"rotated-controlled-refresh","refreshTokenExpiresInSeconds":86400,"refreshTokenDelivery":"RESPONSE_BODY_FOR_OS_SECURE_STORAGE"},"replacedExistingSession":false}""".toByteArray())
  override fun getErrorStream():InputStream=ByteArrayInputStream("{\"error\":{\"code\":\"AUTH_SESSION_REVOKED\"}}".toByteArray())
 }
 private fun roots(error:Throwable):Set<Throwable>{val seen=java.util.Collections.newSetFromMap(java.util.IdentityHashMap<Throwable,Boolean>());fun walk(e:Throwable,ancestors:Set<Throwable>){check(e !in ancestors){"cycle"};if(!seen.add(e))return;e.cause?.let{walk(it,ancestors+e)};e.suppressed.forEach{walk(it,ancestors+e)}};walk(error,emptySet());return seen}
 @Suppress("UNCHECKED_CAST") private suspend fun runChecks():Int{
  URL.setURLStreamHandlerFactory{scheme->if(scheme=="https")object:URLStreamHandler(){override fun openConnection(url:URL)=Peer(url)}else null}
  var count=0
  for(kind in listOf("success","normal","commit-false","unknown","Error","close","retired-operation","retired-generation","retired-owner","cancel")){
   var armed=false;var removes=0;var closes=0
   val cleanup=IllegalStateException("controlled credential cleanup unknown");val fatal=AssertionError("controlled credential cleanup Error");val close=IllegalStateException("controlled owner close unknown")
   val files=mutableListOf<SharedPreferences>()
   val context=object:ContextWrapper(targetContext){override fun getSharedPreferences(name:String,mode:Int):SharedPreferences{
    val original=super.getSharedPreferences("refresh-owner-"+kind+"-"+name,mode);files.add(original)
    if(name!="secure-refresh")return original
    return Proxy.newProxyInstance(SharedPreferences::class.java.classLoader,arrayOf(SharedPreferences::class.java)){_,method,args->
     if(method.name!="edit")method.invoke(original,*(args?:emptyArray()))else{
      val editor=original.edit()
      Proxy.newProxyInstance(SharedPreferences.Editor::class.java.classLoader,arrayOf(SharedPreferences.Editor::class.java)){proxy,m,a->
       if(armed && m.name=="remove")removes++
       if(armed && m.name=="commit")when(kind){"unknown"->throw cleanup;"Error"->throw fatal;"normal"->m.invoke(editor,*(a?:emptyArray()));else->false}
       else{val value=m.invoke(editor,*(a?:emptyArray()));if(value===editor)proxy else value}
      }
     }
    } as SharedPreferences
   }}
   var vm:WorkspaceViewModel?=null;var ownScope:CoroutineScope?=null;var sync:SyncViewModel?=null;var repo:Repository?=null
   try{
    val prefs=Preferences(context);val endpoint="https://fixture.invalid";val account="11111111-1111-4111-8111-111111111111";val session=SendSession(account,"22222222-2222-4222-8222-222222222222",BigInteger.ONE,"controlled-only");val slot=endpoint+"/"+account+"/"+session.sessionId
    prefs.write(slot,"controlled-only");prefs.write(endpoint+"/current",slot);val owner=Auth(endpoint,prefs);check(owner.savedAccount()==account);set(owner,"session",session)
    responseStatus=if(kind=="success")200 else 401
    if(kind=="success"){val next=owner.refresh();check(next.sessionEpoch==BigInteger.TWO);check(owner.session===next);check(prefs.read(slot)=="rotated-controlled-refresh");check(prefs.read(endpoint+"/current")==slot);check(removes==0);count++;println("REFRESH-OWNER normal Auth refresh rotation PASS");continue}
    val failures=java.util.concurrent.CopyOnWriteArrayList<Throwable>();ownScope=CoroutineScope(SupervisorJob()+Dispatchers.Main.immediate+CoroutineExceptionHandler{_,e->failures.add(e)})
    withContext(Dispatchers.Main){vm=WorkspaceViewModel(targetContext.applicationContext as Application)}
    delay(100);val w=vm!!;(get(w,"scope") as CoroutineScope).cancel();set(w,"scope",ownScope);set(w,"auth",owner)
    val dbContext=object:ContextWrapper(targetContext){override fun getDatabasePath(name:String)=java.io.File(cacheDir,"refresh-owner-"+kind+"-"+name)}
    repo=Repository(dbContext,account);val send=SendViewModel(repo,session);val old=SyncViewModel(send,repo,SyncHttps(endpoint,session));sync=old
    set(send,"socket",object:SendSocket{override fun send(text:String){};override fun close(){closes++;if(kind=="close")throw close}})
    set(w,"sync",old);val projection=get(w,"mutable") as MutableStateFlow<WorkspaceState>;withContext(Dispatchers.Main){projection.value=projection.value.copy(session=session)}
    val timer=ownScope.launch{delay(Long.MAX_VALUE)};val observers=ownScope.launch{delay(Long.MAX_VALUE)};set(w,"refreshTimer",timer);set(w,"observers",observers)
    if(kind.startsWith("retired-")||kind=="cancel"){entered=CountDownLatch(1);release=CountDownLatch(1)}
    armed=true;withContext(Dispatchers.Main){w.refresh()}
    if(entered!=null){check(withContext(Dispatchers.IO){entered!!.await(10,TimeUnit.SECONDS)});withContext(Dispatchers.Main){when(kind){"retired-operation"->set(w,"operation",(get(w,"operation") as Long)+1);"retired-generation"->set(w,"generation",(get(w,"generation") as Long)+1);"retired-owner"->set(w,"auth",Auth(endpoint,prefs));"cancel"->ownScope.cancel()}};release!!.countDown()}
    withTimeout(10000){while(owner.session!=null && kind!="cancel")delay(10);while(kind!="cancel" && w.state.value.busy && kind!="retired-operation")delay(10)};delay(150)
    if(kind.startsWith("retired-")){check(w.state.value.session===session);check(get(w,"sync")===old);check(closes==0);check(timer.isActive);check(failures.isEmpty())}
    else if(kind=="cancel"){check(failures.isEmpty());check(w.state.value.session==null);check(get(w,"sync")==null);check(!timer.isActive);check(closes==1)}
    else{
     check(owner.session==null);check(w.state.value.session==null);check(get(w,"auth")==null);check(get(w,"sync")==null);check(!w.state.value.busy);check(!timer.isActive && !observers.isActive);check(get(w,"refreshTimer")==null && get(w,"observers")==null);check(closes==1);check(old.state.value.status=="retired")
     check(removes==if(kind=="normal")2 else 1);val before=removes;withContext(Dispatchers.Main){w.refresh()};delay(50);check(removes==before && closes==1)
     if(kind in listOf("normal","commit-false")){check(failures.isEmpty());check(w.state.value.error!=null)}else{check(failures.size==1);val graph=roots(failures.single());check(graph.filterIsInstance<ApiFailure>().single().kind=="session_expired");when(kind){"unknown"->check(cleanup in graph);"Error"->check(fatal in graph);"close"->check(close in graph)}}
    }
    count++;println("REFRESH-OWNER "+kind+" PASS")
   }finally{release?.countDown();entered=null;release=null;armed=false;ownScope?.cancel();sync?.dispose();repo?.close();files.forEach{check(it.edit().clear().commit())}}
  }
  return count
 }
}
