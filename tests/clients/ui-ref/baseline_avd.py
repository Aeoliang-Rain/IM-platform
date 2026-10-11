"""Create an independent owned API34 factory AVD; never copy existing userdata."""
from pathlib import Path
import subprocess, os, json, time, datetime, socket, hashlib, sys, uuid
root=Path(__file__).resolve().parents[3]
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
on_h='--h-storage' in sys.argv
auth_fix='--auth-fix' in sys.argv
directory=root/'tests/clients/ui-ref/.runtime/baseline-avd' if on_h else private/'baseline-avd'
assert not on_h or directory.resolve().is_relative_to((root/'tests/clients/ui-ref').resolve())
resume='--resume-own' in sys.argv;attempt=uuid.uuid4().hex
if resume:
 original=json.loads((root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/baseline-avd-created.json').read_text());assert Path(original['directory']).resolve()==directory.resolve();assert original['serial']=='emulator-5592'
else:assert not directory.exists();directory.mkdir(parents=True)
user=directory/'android-user';avds=directory/'avds'
if not resume:user.mkdir();avds.mkdir()
env={**os.environ,'JAVA_HOME':'H:/.jdks/jdk17','ANDROID_HOME':'H:/Android','ANDROID_SDK_ROOT':'H:/Android','ANDROID_USER_HOME':str(user),'ANDROID_AVD_HOME':str(avds)}
adb='H:/Android/platform-tools/adb.exe';serial='emulator-5592';image='system-images;android-34;google_apis;x86_64'
assert (Path('H:/Android/system-images/android-34/google_apis/x86_64/system.img')).is_file()
before=subprocess.check_output([adb,'devices'],env=env,text=True);assert serial not in before
for port in [5592,5593]:
 with socket.socket() as probe:probe.bind(('127.0.0.1',port))
name='IMUIRefBaselineH34' if on_h else 'IMUIRefBaseline34'
create=['H:/Android/cmdline-tools/latest/bin/avdmanager.bat','create','avd','--name',name,'--package',image,'--path',str(avds/(name+'.avd'))]
if not resume:
 r=subprocess.run(create,input=b'no\n',env=env,capture_output=True);(directory/'create-original.txt').write_bytes(r.stdout+r.stderr);assert r.returncode==0
argv=['H:/Android/emulator/emulator.exe','-avd',name,'-port','5592','-no-window','-no-snapshot','-no-audio','-no-boot-anim','-gpu','swiftshader_indirect','-memory','1536']
if resume:argv+=['-partition-size','2047']
suffix='-'+attempt if resume else ''
stdout=(directory/('emulator-stdout'+suffix+'.txt')).open('xb');stderr=(directory/('emulator-stderr'+suffix+'.txt')).open('xb')
process=subprocess.Popen(argv,env=env,stdout=stdout,stderr=stderr)
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directory':str(directory),'serial':serial,'image':image,'createCommand':create,'launchCommand':argv,'launcherPID':process.pid,'originalDevices':before,'method':'Factory SDK image; independent new owned userdata; no original AVD copy/reset or root/SELinux/system trust changes','environment':{k:env[k] for k in ['JAVA_HOME','ANDROID_HOME','ANDROID_USER_HOME','ANDROID_AVD_HOME']}}
receipt.update({'attempt':attempt,'resumeOwnedFactory':resume,'userdataPartitionMegabytes':2047 if resume else 'SDK default','priorFailureQualification':'Default userdata required7372MB but only6175MB available; emulator rejects2048 above its2047MB CLI limit; both original logs retained' if resume else None})
import shutil
receipt.update({'resolvedOwnedRoot':str(directory.resolve()),'freeBytesBeforeLaunch':shutil.disk_usage(directory).free,'environmentMethod':'Child-only explicit env mapping; parent environment unchanged','storageOnAssignedTaskAllowedPath':on_h})
target=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'/('auth-fix-avd-created.json' if auth_fix else 'baseline-avd-h-created.json' if on_h else 'baseline-avd-restart-'+attempt+'.json' if resume else 'baseline-avd-created.json');assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
try:
 for _ in range(180):
  assert process.poll() is None
  boot=subprocess.run([adb,'-s',serial,'shell','getprop','sys.boot_completed'],env=env,capture_output=True).stdout.decode().strip()
  if boot=='1':break
  time.sleep(1)
 else:raise RuntimeError('Independent baseline AVD boot timeout')
 sdk=subprocess.check_output([adb,'-s',serial,'shell','getprop','ro.build.version.sdk'],env=env,text=True).strip();assert sdk=='34'
 ready=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'/('auth-fix-avd-ready.json' if auth_fix else 'baseline-avd-ready.json');assert not ready.exists();ready.write_text(json.dumps({**receipt,'actualReadyUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualSDK':sdk},indent=2)+'\n',encoding='utf-8');print('READY independent owned API34 baseline '+serial,flush=True)
 while not (directory/'stop-request').exists():
  assert process.poll() is None;time.sleep(.5)
finally:
 if process.poll() is None:
  subprocess.run([adb,'-s',serial,'emu','kill'],env=env,capture_output=True);process.wait(timeout=30)
 stdout.close();stderr.close()
 print('Owned baseline emulator stopped; raw originals retained',flush=True)
