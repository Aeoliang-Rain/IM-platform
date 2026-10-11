"""Run one required baseline on the new owned factory AVD; archive each actual APK."""
from pathlib import Path
import os, subprocess, json, hashlib, datetime, time, sys, uuid, re
root=Path(__file__).resolve().parents[3]
evidence=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
ready=json.loads((evidence/'baseline-avd-ready.json').read_text())
owned=root/'tests/clients/ui-ref/.runtime/baseline-avd'
assert Path(ready['directory']).resolve()==owned.resolve() and ready['serial']=='emulator-5592' and ready['actualSDK']=='34'
stage=sys.argv[1];assert stage in ['sqlite','send','sync','gui']
serial='emulator-5592';adb='H:/Android/platform-tools/adb.exe'
env={**os.environ,**ready['environment'],'ANDROID_SDK_ROOT':'H:/Android','GRADLE_USER_HOME':'H:/gradle','IM_CLIENT_ADB':adb,'IM_CLIENT_GRADLE':str(root/'tests/clients/ui-ref/gradle_bounded.cmd')}
args=[sys.executable,'-Xutf8','-B',f'tools/verify_client_{stage}.py','--scope','mobile','--serial',serial] if stage!='gui' else [sys.executable,'-Xutf8','-B','tests/clients/gui/android.py','--serial',serial,'--capture']
run='android-baseline-'+stage+'-'+uuid.uuid4().hex
out=evidence/'screens'/run;out.mkdir()
archive=private/run;archive.mkdir()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
status=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
before=datetime.datetime.now(datetime.timezone.utc).isoformat();start=time.monotonic()
r=subprocess.run(args,cwd=root,env=env,capture_output=True)
(out/'command-stdout-original.txt').write_bytes(r.stdout);(out/'command-stderr-original.txt').write_bytes(r.stderr)
print(r.stdout.decode(errors='replace'));print(r.stderr.decode(errors='replace'),file=sys.stderr)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
artifacts=[]
for package,path in [('im.platform.client','debug/app-debug.apk'),('im.platform.client.test','androidTest/debug/app-debug-androidTest.apk')]:
 built=root/'clients/mobile/app/build/outputs/apk'/path
 item={'package':package,'outputsQualification':'Observed after actual stage command; only accepted when commandPASS and matches installed bytes'}
 if built.exists():
  saved=archive/(package+'-built.apk');saved.write_bytes(built.read_bytes());item.update({'buildArchive':str(saved),'buildSHA256':sha(saved)})
 location=subprocess.run([adb,'-s',serial,'shell','pm','path',package],env=env,capture_output=True)
 (out/(package+'-device-path-original.txt')).write_bytes(location.stdout+location.stderr)
 device=location.stdout.decode().strip().removeprefix('package:')
 if device.startswith('/data/app/'):
  pulled=archive/(package+'-device.apk');pull=subprocess.run([adb,'-s',serial,'pull',device,str(pulled)],env=env,capture_output=True)
  (out/(package+'-pull-original.txt')).write_bytes(pull.stdout+pull.stderr)
  if pull.returncode==0:item.update({'devicePath':device,'deviceArchive':str(pulled),'deviceSHA256':sha(pulled)})
 artifacts.append(item)
 if r.returncode==0:assert item.get('buildSHA256')==item.get('deviceSHA256') and item.get('deviceSHA256'), 'Actual stage installed APK does not match archived build'
if stage=='gui':
 match=re.search(rb'INSTRUMENTATION_RESULT: captureRun=(\d+)',r.stdout)
 if match:
  pull=subprocess.run([adb,'-s',serial,'pull','/sdcard/Android/data/im.platform.client/files/gui-captures/'+match[1].decode(),str(out/'native-originals')],env=env,capture_output=True)
  (out/'capture-pull-original.txt').write_bytes(pull.stdout+pull.stderr)
  if r.returncode==0:assert pull.returncode==0
entries=[{'file':str(p.relative_to(out)),'sha256':sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
receipt={'task_id':'LOOP1-CLIENT-UI-REF-001','stage':stage,'command':args,'actualHEAD':head,'actualStatusBefore':status,'productSource':'1bd1a1bf015edd6422bd8bfeeb73bc454b565034','startUTC':before,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedSeconds':time.monotonic()-start,'exit':r.returncode,'result':'PASS' if r.returncode==0 else 'FAIL','actualAVD':ready,'artifacts':artifacts,'entries':entries,'qualification':'Separate factory-owned emulator baseline/reset; never clears old emulator5590 unknown userdata and never replaces actual A/B/Friends evidence. APKs archived and installed bytes pulled before any later runner rebuild.'}
(out/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(receipt['result'],stage,'actual baseline:',out)
raise SystemExit(r.returncode)
