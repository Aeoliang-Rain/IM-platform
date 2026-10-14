import pathlib,json,hashlib,subprocess,sys
ROOT=pathlib.Path('H:/.codex/worktrees/err/IM-platform'); EXT=pathlib.Path(__file__).parent
old=EXT.parent/'regular-review-a337780';receipt=json.loads((old/'final-receipt.json').read_text());assert hashlib.sha256((old/'final-receipt.json').read_bytes()).hexdigest()=='a25308d22980cad1363686564ba1c1b9b5ea5c2454b8a6ec4bf0c1d673c8deb9'
for entry in receipt['artifacts']:
 p=old/entry['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],p
assert len(receipt['artifacts'])==63
print('63 immutable prior review artifacts verified; exact receipt verified')
cache=pathlib.Path('H:/gradle/caches/modules-2/files-2.1')
def jar(g,n,v):return next((cache/g/n/v).rglob('*.jar'))
std=jar('org.jetbrains.kotlin','kotlin-stdlib','2.1.10');cor=jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.9.0');ann=jar('org.jetbrains','annotations','23.0.0')
compiler=[jar('org.jetbrains.kotlin','kotlin-compiler-embeddable','2.1.10'),std,cor,ann,jar('org.jetbrains.kotlin','kotlin-script-runtime','2.1.10'),jar('org.jetbrains.kotlin','kotlin-reflect','1.6.10'),jar('org.jetbrains.intellij.deps','trove4j','1.0.20200330')]
(EXT/'Session.kt').write_bytes((old/'Session.kt').read_bytes());(EXT/'SyncStubs.kt').write_bytes((old/'SyncStubs.kt').read_bytes())
(EXT/'AuthStubs.kt').write_text('''package im.platform.client.ui
class Preferences {fun write(a:String,b:String){};fun remove(a:String){};fun read(a:String):String?=null}
''')
(EXT/'SendWire.kt').write_text('''package im.platform.client.send
import java.math.BigInteger
class WireFailure:Exception()
object Wire {fun parse(raw:String,max:Int):Any=emptyMap<String,Any>();fun obj(v:Any?,keys:Set<String>):Map<String,Any?> = emptyMap();fun uuid(v:Any?):String="fixture";fun integer(v:Any?):BigInteger=BigInteger.ONE}
''')
(EXT/'Json.kt').write_text('''package org.json
class JSONObject {fun put(k:String,v:Any?):JSONObject=this;override fun toString()="{}"}
''')
(EXT/'Baseline.kt').write_text('''import im.platform.client.sync.*
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
''')
java='H:/.jdks/jdk17/bin/java.exe';target=EXT/'baseline-classes';target.mkdir(exist_ok=True)
sources=[ROOT/'clients/mobile/app/src/main/kotlin/im/platform/client/sync/Https.kt',ROOT/'clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt',*[EXT/x for x in ['Session.kt','SyncStubs.kt','AuthStubs.kt','SendWire.kt','Json.kt','Baseline.kt']]]
for p in sources[:2]:print('exact production source',p,hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
r=subprocess.run([java,'-cp',';'.join(map(str,compiler)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',';'.join(map(str,[std,cor,ann])),'-d',str(target),*map(str,sources)]);assert r.returncode==0
sys.exit(subprocess.call([java,'-cp',';'.join(map(str,[target,std,cor,ann])),'BaselineKt']))
