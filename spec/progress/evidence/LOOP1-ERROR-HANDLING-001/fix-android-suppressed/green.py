import pathlib,subprocess,sys
E=pathlib.Path(__file__).parent;R=pathlib.Path('H:/.codex/worktrees/err/IM-platform')
s=(E/'HttpCleanupInstrumentation.kt').read_text().split('\nclass HttpCleanupInstrumentation:')[0]
(E/'Checks.kt').write_text(s);(E/'Main.kt').write_text('import im.platform.client.ui.*\nimport kotlinx.coroutines.runBlocking\nfun main()=runBlocking {println("GREEN actual source Kotlin production cleanup checks="+HttpCleanupChecks.run(Auth("https://localhost",Preferences())))}\n')
cache=pathlib.Path('H:/gradle/caches/modules-2/files-2.1')
def jar(g,n,v):return next((cache/g/n/v).rglob('*.jar'))
std=jar('org.jetbrains.kotlin','kotlin-stdlib','2.1.10');cor=jar('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm','1.9.0');ann=jar('org.jetbrains','annotations','23.0.0')
compiler=[jar('org.jetbrains.kotlin','kotlin-compiler-embeddable','2.1.10'),std,cor,ann,jar('org.jetbrains.kotlin','kotlin-script-runtime','2.1.10'),jar('org.jetbrains.kotlin','kotlin-reflect','1.6.10'),jar('org.jetbrains.intellij.deps','trove4j','1.0.20200330')]
java='H:/.jdks/jdk17/bin/java.exe';target=E/'green-classes';target.mkdir(exist_ok=True)
sources=[R/'clients/mobile/app/src/main/kotlin/im/platform/client/sync/Https.kt',R/'clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt',*[E/x for x in ['Session.kt','SyncStubs.kt','AuthStubs.kt','SendWire.kt','Json.kt','Checks.kt','Main.kt']]]
r=subprocess.run([java,'-cp',';'.join(map(str,compiler)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',';'.join(map(str,[std,cor,ann])),'-d',str(target),*map(str,sources)]);assert r.returncode==0
sys.exit(subprocess.call([java,'-cp',';'.join(map(str,[target,std,cor,ann])),'MainKt']))
