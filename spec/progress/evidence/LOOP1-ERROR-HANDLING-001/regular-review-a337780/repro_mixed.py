import pathlib,subprocess,hashlib,json,time
out=pathlib.Path(__file__).parent;root=pathlib.Path('H:/.codex/worktrees/err/IM-platform');cache=pathlib.Path('H:/gradle/caches/modules-2/files-2.1')
def jar(group,name,ver):return next((cache/group/name/ver).rglob('*.jar'))
std=jar('org.jetbrains.kotlin','kotlin-stdlib','2.1.10');cor=jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.9.0');ann=jar('org.jetbrains','annotations','23.0.0')
compiler=[jar('org.jetbrains.kotlin','kotlin-compiler-embeddable','2.1.10'),std,cor,ann,jar('org.jetbrains.kotlin','kotlin-script-runtime','2.1.10'),jar('org.jetbrains.kotlin','kotlin-reflect','1.6.10'),jar('org.jetbrains.intellij.deps','trove4j','1.0.20200330')]
(out/'Session.kt').write_text('package im.platform.client.send\nimport java.math.BigInteger\ndata class SendSession(val userId:String,val sessionId:String,val sessionEpoch:BigInteger,val accessToken:String)\n',encoding='utf8')
(out/'SyncStubs.kt').write_text('''package im.platform.client.sync
const val MAX_RESPONSE=6*1024*1024
class SyncFailure(val kind:String):Exception("Sync $kind failure")
class UserPage
class ConversationPage
object Wire {
 fun userRequest(id:String,cursor:String)="{}"
 fun conversationRequest(id:String,c:String,after:Long)="{}"
 fun user(raw:String,id:String,input:String)=UserPage()
 fun conversation(raw:String,id:String,c:String,after:Long)=ConversationPage()
 fun error(raw:String,id:String,status:Int,conversation:Boolean)=SyncFailure("protocol")
}
''',encoding='utf8')
(out/'MixedCleanup.kt').write_text('''import im.platform.client.sync.*
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
''',encoding='utf8')
java='H:/.jdks/jdk17/bin/java.exe';src=root/'clients/mobile/app/src/main/kotlin/im/platform/client/sync/Https.kt';target=out/'mixed-classes';target.mkdir(exist_ok=True)
cmd=[java,'-cp',';'.join(map(str,compiler)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',';'.join(map(str,[std,cor,ann])),'-d',str(target),str(src),str(out/'Session.kt'),str(out/'SyncStubs.kt'),str(out/'MixedCleanup.kt')]
print('Exact production Https.kt SHA256',hashlib.sha256(src.read_bytes()).hexdigest(),flush=True)
r=subprocess.run(cmd);assert r.returncode==0,r.returncode
r=subprocess.run([java,'-cp',';'.join(map(str,[target,std,cor,ann])),'MixedCleanupKt']);raise SystemExit(r.returncode)
