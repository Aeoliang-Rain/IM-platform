"""Fresh distinct process SDK trust negative against the same live pinned fixture."""
from pathlib import Path
import subprocess,json,hashlib,datetime,sys,re,ssl,urllib.request,time
root=Path(__file__).resolve().parents[3];private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime');adb='H:/Android/platform-tools/adb.exe'
positive=Path(sys.argv[1]);assert positive.resolve().is_relative_to((root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001').resolve())
raw=positive.read_text();assert 'INSTRUMENTATION_RESULT: result=PASS' in raw and 'testTrustRestore=PASS' in raw and 'actualDefaultSocketTLSHostnamePositive=PASS' in raw
old=int(re.search(r'targetProcessId=(\d+)',raw).group(1));head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();out=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens'/('android-default-negative-'+head[:7]);out.mkdir(exist_ok=False)
def call(*args):return subprocess.check_output([adb,'-s','emulator-5590',*args])
def pid():return subprocess.run([adb,'-s','emulator-5590','shell','pidof','im.platform.client'],capture_output=True).stdout.decode().strip()
ctx=ssl.create_default_context(cafile=str(private/'tls-ui-ref/ca.pem'))
def health():
 with urllib.request.urlopen('https://localhost:8443/__infra/health',context=ctx,timeout=15) as response:assert response.status==200;return {'status':response.status,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
beforeHealth=health();liveBefore=pid();assert not liveBefore or liveBefore.isdecimal()
if liveBefore:call('shell','am','force-stop','im.platform.client')
assert not pid(),'Old owned package process must be absent before new runner'
apk=root/'clients/mobile/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk';archive=private/('negative-test-'+head[:7]+'.apk');assert not archive.exists();archive.write_bytes(apk.read_bytes())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
install=call('install','-r',str(archive)).decode();assert 'Success' in install
device=call('shell','pm','path','im.platform.client.test').decode().strip().removeprefix('package:');pulled=private/('negative-installed-'+head[:7]+'.apk');subprocess.run([adb,'-s','emulator-5590','pull',device,str(pulled)],check=True,capture_output=True);assert sha(pulled)==sha(archive)
result=subprocess.run([adb,'-s','emulator-5590','shell','am','instrument','-w','im.platform.client.test/im.platform.client.ui.UiRefTLSNegative'],capture_output=True,timeout=90);(out/'instrumentation-original.txt').write_bytes(result.stdout+result.stderr);text=(result.stdout+result.stderr).decode(errors='replace');print(text)
assert result.returncode==0 and 'INSTRUMENTATION_RESULT: result=PASS' in text and 'freshDefaultSDKHTTPSRejected=PASS' in text and 'freshDefaultSDKSocketRejected=PASS' in text
new=int(re.search(r'INSTRUMENTATION_RESULT: pid=(\d+)',text).group(1));assert new!=old and (not liveBefore or new!=int(liveBefore))
afterHealth=health();receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualHEAD':head,'positiveOriginal':str(positive),'positiveSHA256':sha(positive),'lastPositivePID':old,'actualLivePIDBefore':liveBefore or None,'oldPackageAbsentBeforeNewProcess':True,'newActualInstrumentationPID':new,'negativeRunner':'im.platform.client.ui.UiRefTLSNegative','source':head,'sourceQualification':'Actual build HEAD; androidTest tracked tree must be clean before build','negativeAPK':{'archive':str(archive),'sha256':sha(archive),'actualDevicePath':device,'deviceArchive':str(pulled),'deviceSHA256':sha(pulled),'installRaw':install},'sameFixtureCertificateDERHash':sha(private/'tls-ui-ref/ca.der'),'explicitPinnedCAHealthBefore':beforeHealth,'explicitPinnedCAHealthAfter':afterHealth,'qualification':'No helper/explicit CA installed in new process; original SDK default HTTPS and socket trust reject same live fixture. Context/factory/property/full provider order restoration bound to preceding positive original. No Android system roots/security changes.'}
(out/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('PASS fresh distinct Android process/default SDK HTTPS+socket negative; same pinned live explicitCA health positive before/after')
