"""Reset only proven newly owned factory packages for distinct GUI debug signer."""
from pathlib import Path
import subprocess,json,os,hashlib,datetime
root=Path(__file__).resolve().parents[3];evidence=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'
ready=json.loads((evidence/'baseline-avd-ready.json').read_text());assert ready['serial']=='emulator-5592' and Path(ready['directory']).resolve()==(root/'tests/clients/ui-ref/.runtime/baseline-avd').resolve()
stage=json.loads((evidence/'screens/android-baseline-sync-4ef4902a295d480186a579ef5bbb7e0e/manifest.json').read_text());assert stage['result']=='PASS'
env={**os.environ,**ready['environment']};adb='H:/Android/platform-tools/adb.exe';proof=[]
for item in reversed(stage['artifacts']):
 name=item['package'];assert name in ['im.platform.client','im.platform.client.test']
 location=subprocess.run([adb,'-s','emulator-5592','shell','pm','path',name],env=env,capture_output=True)
 device=location.stdout.decode().strip().removeprefix('package:')
 if not device:
  assert name=='im.platform.client.test' and location.returncode==1
  proof.append({'package':name,'alreadyAbsent':True,'actualPathExit':location.returncode,'qualification':'Prior owned reset succeeded at uninstall then failed because absent pm path returns1; no pre-removal receipt was written. Original failure and previous stage device archive remain.'});continue
 data=subprocess.check_output([adb,'-s','emulator-5592','exec-out','cat',device],env=env)
 assert hashlib.sha256(data).hexdigest()==item['deviceSHA256']
 before=evidence/('baseline-gui-reset-before-'+name+'.json');assert not before.exists();before.write_text(json.dumps({'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':name,'devicePath':device,'actualSHA256':hashlib.sha256(data).hexdigest()},indent=2)+'\n')
 result=subprocess.check_output([adb,'-s','emulator-5592','uninstall',name],env=env).decode();assert 'Success' in result
 absent=subprocess.run([adb,'-s','emulator-5592','shell','pm','path',name],env=env,capture_output=True);assert not absent.stdout.strip() and absent.returncode in [0,1]
 proof.append({'package':name,'beforeDevicePath':device,'beforeSHA256':item['deviceSHA256'],'ownedBaselineSourceManifest':str(evidence/'screens/android-baseline-sync-4ef4902a295d480186a579ef5bbb7e0e/manifest.json'),'uninstallRaw':result,'afterAbsent':True})
target=evidence/'baseline-gui-signer-reset.json';assert not target.exists();target.write_text(json.dumps({'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'serial':'emulator-5592','proof':proof,'qualification':'Only new factory task-owned baseline packages/data reset. Existing GUI wrapper clears build ANDROID_USER_HOME and signs with default key unlike preceding stages. Previous stage exact artifacts/data evidence retained. Never reset old emulator5590 unknown data.'},indent=2)+'\n',encoding='utf-8')
print('PASS exact owned factory-only GUI signer environment reset')
