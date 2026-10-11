"""Archive actual pre/post device APK bytes, then install exact frozen helper APK."""
from pathlib import Path
import subprocess,json,hashlib,datetime
root=Path(__file__).resolve().parents[3];adb='H:/Android/platform-tools/adb.exe'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
out=private/('apk-install-'+head[:7]);out.mkdir(exist_ok=False)
def run(*args):return subprocess.check_output([adb,'-s','emulator-5590',*args])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def installed(package,label):
 paths=run('shell','pm','path',package).decode().strip().splitlines();assert len(paths)==1
 path=paths[0].removeprefix('package:').strip();target=out/(label+'.apk')
 subprocess.run([adb,'-s','emulator-5590','pull',path,str(target)],check=True,capture_output=True)
 return {'devicePath':path,'archive':str(target),'sha256':digest(target)}
before=installed('im.platform.client.test','before-device-test')
source=root/'clients/mobile/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk';archive=out/'candidate-test.apk';archive.write_bytes(source.read_bytes())
install=run('install','-r',str(archive)).decode();assert 'Success' in install
after=installed('im.platform.client.test','after-device-test');assert after['sha256']==digest(archive)
production=installed('im.platform.client','device-production')
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':head,'runner':'im.platform.client.ui.GuiAuthenticatedInstrumentation','productSource':'1bd1a1bf015edd6422bd8bfeeb73bc454b565034','beforeTest':before,'candidateArchive':str(archive),'candidateSHA256':digest(archive),'installRaw':install,'afterTest':after,'production':production,'status':subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)}
target=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'/('android-install-binding-'+head[:7]+'.json');assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
