"""Retry with new friendship targets, retaining previous fixture/data and actual failure."""
from pathlib import Path
import subprocess,json,os,hashlib,datetime,sys
root=Path(__file__).resolve().parents[3];runtime=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime');adb='H:/Android/platform-tools/adb.exe'
failed=root/('spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/'+(sys.argv[1] if len(sys.argv)>1 else 'friends-573c124c-a1ea-4ed6-b9d6-b8813f8bac1f'));assert failed.resolve().parent== (root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens').resolve()
original=Path(sys.argv[2]) if len(sys.argv)>2 else runtime/'fresh-public.json';assert original.resolve().parent==runtime.resolve()
target=failed/'fixture-retained-after-failure.json';assert not target.exists();target.write_bytes(original.read_bytes())
def pid():return subprocess.run([adb,'-s','emulator-5590','shell','pidof','im.platform.client'],capture_output=True).stdout.decode().strip()
before=pid();assert not before or before.isdecimal()
if before:subprocess.run([adb,'-s','emulator-5590','shell','am','force-stop','im.platform.client'],check=True,capture_output=True)
after=pid();assert not after
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exactOwnedPackage':'im.platform.client','beforePID':before or None,'terminated':not after,'afterPID':None,'currentSourceInstallBinding':os.environ.get('IM_UIREF_ANDROID_BINDING','android-install-binding-b02a853.json'),'originalFailureSourceBinding':'source-install-binding-before.json retained beside original raw','fixtureRetainedSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':'Controlled failed fixture runner package only; no app data clear, no other PID stopped'}
(failed/'owned-runner-termination.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
r=subprocess.run([os.sys.executable,'-Xutf8','-B','tests/clients/ui-ref/state/fresh_fixture.py','--new-friends-owner' if '--new-owner' in sys.argv else '--rotate-targets'],cwd=root,capture_output=True,text=True);print(r.stdout);print(r.stderr);assert r.returncode==0
path=Path(r.stdout.strip().split('output ',1)[1]);assert path.resolve().parent==runtime.resolve();assert path.name.startswith('friends-fixture-')
env=os.environ.copy();env['IM_STATE_FRESH_FIXTURE']=str(path);env.setdefault('IM_UIREF_ANDROID_BINDING','spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/android-install-binding-b02a853.json')
subprocess.run(['node','tests/clients/ui-ref/state/friends_actual.mjs'],cwd=root,env=env,check=True)
