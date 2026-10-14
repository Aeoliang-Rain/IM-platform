from pathlib import Path
import os,subprocess,socket,json
E=Path(__file__).parent;R=Path('H:/.codex/worktrees/err/IM-platform');name='HttpCleanup20261014';port=5598
avd=E/'avd'/'HttpCleanup20261014.avd';avd.parent.mkdir(exist_ok=True)
env=os.environ.copy();env.update(JAVA_HOME='H:/.jdks/jdk17',ANDROID_HOME='H:/Android',ANDROID_SDK_ROOT='H:/Android',ANDROID_USER_HOME=str(E/'android-user'),ANDROID_AVD_HOME=str(E/'avds'))
for p in [E/'android-user',E/'avds']:p.mkdir(exist_ok=True)
assert not avd.exists()
for n in [port,port+1]:
 with socket.socket() as sock:sock.bind(('127.0.0.1',n))
adb='H:/Android/platform-tools/adb.exe';before=subprocess.check_output([adb,'devices','-l'],env=env,text=True)
assert not [x for x in before.splitlines() if x.startswith('emulator-')],before
subprocess.run(['cmd.exe','/d','/c','H:/Android/cmdline-tools/latest/bin/avdmanager.bat','create','avd','-n',name,'-k','system-images;android-34;google_apis;x86_64','-p',str(avd)],input='no\n',text=True,env=env,check=True)
log=(E/'emulator.log').open('w');proc=subprocess.Popen(['H:/Android/emulator/emulator.exe','-avd',name,'-port',str(port),'-no-window','-no-audio','-no-snapshot','-gpu','swiftshader_indirect'],env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
(E/'emulator-receipt.json').write_text(json.dumps({'owned_name':name,'owned_avd':str(avd),'pid':proc.pid,'serial':'emulator-5598','baseline_devices':before,'global_trust_changed':False},indent=2))
print('Owned actual API34 emulator launched',proc.pid)
