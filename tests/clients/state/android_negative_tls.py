"""Fresh default-SDK negative test after exact rollback; own reverse restored in finally."""
from pathlib import Path
import hashlib,json,os,subprocess,ssl,urllib.request,datetime
adb="H:/Android/platform-tools/adb.exe";env={**os.environ,"ANDROID_USER_HOME":"H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user"};runtime=Path("H:/IM-platform/.git/worktrees/IM-platform43/state-runtime")
def call(*args):return subprocess.check_output([adb,"-s","emulator-5590",*args],env=env,text=True,encoding="utf-8",timeout=30).strip()
assert call("shell","id","-u")=="2000" and call("shell","getenforce")=="Enforcing";baseline=call("reverse","--list");assert not baseline
ctx=ssl.create_default_context(cafile=str(runtime/"tls-state-week2/ca.pem"))
with urllib.request.urlopen("https://localhost:8443/__infra/health",context=ctx,timeout=10) as response:positive=response.status
assert positive==200
apk=Path(os.environ.get("IM_STATE_ANDROID_NEGATIVE_APK", "clients/mobile/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk"));raw=""
expected=os.environ.get("IM_STATE_ANDROID_NEGATIVE_APK_SHA256")
if expected:assert hashlib.sha256(apk.read_bytes()).hexdigest()==expected, "Retained bound negative APK hash differs"
try:
 call("reverse","tcp:8443","tcp:8443");call("install","-r",str(apk))
 registration=call("shell","pm","list","instrumentation","im.platform.client")
 assert "im.platform.client.test/im.platform.client.ui.GuiTrustRollbackInstrumentation" in registration, "Actual installed rollback runner registration absent"
 raw=call("shell","am","instrument","-w","-e","caFile","6432a2a5.0","-e","port","8443","im.platform.client.test/im.platform.client.ui.GuiTrustRollbackInstrumentation")
 assert "INSTRUMENTATION_RESULT: result=PASS" in raw and "tlsRejection=SSLHandshakeException" in raw
finally:
 current=call("reverse","--list");assert any(l.split()[-2:]==["tcp:8443","tcp:8443"] for l in current.splitlines());call("reverse","--remove","tcp:8443");assert call("reverse","--list")==baseline
 Path(os.environ.get("IM_STATE_ANDROID_NEGATIVE_RAW", "spec/progress/evidence/LOOP1-CLIENT-STATE-001/android-week2-native-negative-original.txt")).write_text(raw+"\n",encoding="utf-8")
result={"actualUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"strictCAFileLiveHealth":positive,"nativeDefaultTLS":"SSLHandshakeException","testApkSHA256":hashlib.sha256(apk.read_bytes()).hexdigest(),"originalUid":call("shell","id","-u"),"reverseBaseline":baseline,"reverseRestored":call("reverse","--list"),"result":"PASS fresh actual Android SDK default TLS rejects same healthy temporary chain after rollback"}
Path(os.environ.get("IM_STATE_ANDROID_NEGATIVE", "spec/progress/evidence/LOOP1-CLIENT-STATE-001/android-week2-native-negative.json")).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(result["result"])
