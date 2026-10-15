import pathlib,subprocess,sys,time,json
R=pathlib.Path('H:/.codex/worktrees/err/IM-platform');E=pathlib.Path(__file__).parent;adb='H:/Android/platform-tools/adb.exe';serial='emulator-5598';runner=sys.argv[1];PY=sys.executable
subprocess.run([PY,'-Xutf8','-B',str(R/'tests/clients/gui/native.py'),'gradle','-PimSendInstrumentation='+runner,'assembleDebug','assembleDebugAndroidTest'],cwd=R,check=True)
subprocess.run([adb,'-s',serial,'wait-for-device'],check=True,timeout=120)
for _ in range(100):
 boot=subprocess.check_output([adb,'-s',serial,'shell','getprop','sys.boot_completed'],text=True).strip()
 if boot=='1':break
 time.sleep(1)
else:raise RuntimeError('owned emulator boot timeout')
for path in ['debug/app-debug.apk','androidTest/debug/app-debug-androidTest.apk']:subprocess.run([adb,'-s',serial,'install','-r',str(R/'clients/mobile/app/build/outputs/apk'/path)],check=True)
p=subprocess.run([adb,'-s',serial,'shell','am','instrument','-w','im.platform.client.test/'+runner],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180);print(p.stdout,flush=True)
(E/(runner.rsplit('.',1)[-1]+'.output.txt')).write_text(p.stdout,encoding='utf8');assert p.returncode==0 and 'result=PASS' in p.stdout and 'sdkInt=34' in p.stdout and 'INSTRUMENTATION_CODE: -1' in p.stdout,p.stdout
