"""Actual owned API34 instrumentation, never host substitute."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
def main():
 serial=sys.argv[1];assert serial=="emulator-5588", "explicit task-owned serial required"
 adb="H:/Android/platform-tools/adb.exe";env=os.environ.copy()
 subprocess.run([sys.executable,"-Xutf8","-B","tests/clients/gui/native.py","gradle","-PimSendInstrumentation=im.platform.client.ui.ErrorHandlingInstrumentation","assembleDebug","assembleDebugAndroidTest"],cwd=ROOT,env=env,check=True)
 for path in ["debug/app-debug.apk","androidTest/debug/app-debug-androidTest.apk"]:subprocess.run([adb,"-s",serial,"install","-r",str(ROOT/"clients/mobile/app/build/outputs/apk"/path)],env=env,check=True)
 result=subprocess.check_output([adb,"-s",serial,"shell","am","instrument","-w","im.platform.client.test/im.platform.client.ui.ErrorHandlingInstrumentation"],env=env,text=True)
 print(result)
 assert "result=PASS" in result and "sdkInt=34" in result and "INSTRUMENTATION_CODE: -1" in result
if __name__=="__main__":main()
