"""Reinstall exact archived790 helper after SDKnegative; preserve actual device binding."""
from pathlib import Path
import subprocess,json,os,hashlib,datetime,uuid
root=Path(__file__).resolve().parents[3];evidence=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'
old=json.loads((evidence/'android-install-binding-7907a23.json').read_text());assert old['HEAD'].startswith('7907a23')
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime');run='restore-friends-apk-'+uuid.uuid4().hex;out=private/run;out.mkdir()
adb='H:/Android/platform-tools/adb.exe';env={**os.environ,'ANDROID_USER_HOME':'H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def call(*args):return subprocess.check_output([adb,'-s','emulator-5590',*args],env=env)
def installed(name,label):
 device=call('shell','pm','path',name).decode().strip().removeprefix('package:');path=out/(label+'.apk');subprocess.run([adb,'-s','emulator-5590','pull',device,str(path)],env=env,check=True,capture_output=True);return {'devicePath':device,'archive':str(path),'sha256':sha(path)}
before=installed('im.platform.client.test','before-negative-runner')
archive=Path(old['afterTest']['archive']);assert sha(archive)==old['afterTest']['sha256']
result=call('install','-r',str(archive)).decode();assert 'Success' in result
after=installed('im.platform.client.test','after-exact-790-runner');assert after['sha256']==old['afterTest']['sha256']
production=installed('im.platform.client','production-unchanged');assert production['sha256']==old['production']['sha256']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
receipt={**old,'HEAD':old['HEAD'],'actualInstallHEAD':head,'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'beforeTest':before,'afterTest':after,'production':production,'installRaw':result,'originalBuildBinding':str(evidence/'android-install-binding-7907a23.json'),'qualification':'Actual reinstallation of archived790 build bytes, not a rebuild at current host helperHEAD; original APK/testSource790 and productSource1bd unchanged. Old unknown app data preserved.'}
target=evidence/('android-reinstalled-binding-'+head[:7]+'.json');assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('PASS actual790 archive==new installed device APK binding',target)
