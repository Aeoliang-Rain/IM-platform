"""Read-only mount/CA restoration checks, restoring the original ADB UID in finally."""
from pathlib import Path
import json,os,subprocess,datetime
adb="H:/Android/platform-tools/adb.exe";env={**os.environ,"ANDROID_USER_HOME":"H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user"}
private=Path("H:/IM-platform/.git/worktrees/IM-platform43/state-runtime");state=json.loads(Path(os.environ.get("IM_STATE_ANDROID_RECORD",str(private/"android-state-week2.json"))).read_text(encoding="utf-8"))
def call(*a):return subprocess.check_output([adb,"-s","emulator-5590",*a],env=env,text=True,encoding="utf-8",timeout=30).strip()
def sh(a):return call("shell",a)
assert call("emu","avd","name").splitlines()[0]=="IMClientSend34" and sh("getprop sys.boot_completed")=="1"
assert state["originalUid"]=="2000" and sh("id -u")=="2000";reverse=call("reverse","--list");assert not reverse
try:
 call("root");call("wait-for-device");assert sh("id -u")=="0"
 original=next(iter(state["namespaces"].values()))["files"]
 proofs=[];seen=set()
 for pid in ["1",*sh("pidof zygote64 zygote").split()]:
  ns=sh("readlink /proc/"+pid+"/ns/mnt")
  if ns in seen:continue
  seen.add(ns);mounts=[l for l in sh("cat /proc/"+pid+"/mountinfo").splitlines() if l.split()[4]=="/apex/com.android.conscrypt/cacerts"];assert not mounts
  files=sh('nsenter --mount=/proc/'+pid+'/ns/mnt -- sh -c "cd /apex/com.android.conscrypt/cacerts && sha256sum *"');assert files==original
  proofs.append({"pid":pid,"namespace":ns,"targetMounts":mounts,"caBaselineByteEqual":True,"caCount":len(files.splitlines())})
 assert sh("test ! -e /data/local/tmp/im-gui-ca && test ! -e /data/local/tmp/im-gui-mount-ro && test ! -e /apex/com.android.conscrypt/cacerts/6432a2a5.0 && echo ABSENT")=="ABSENT"
finally:call("unroot");call("wait-for-device")
assert sh("id -u")==state["originalUid"] and sh("getenforce")==state["originalSELinux"] and call("reverse","--list")==reverse
result={"actualUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"avd":"IMClientSend34","serial":"emulator-5590","originalUid":state["originalUid"],"restoredUid":sh("id -u"),"SELinux":sh("getenforce"),"reverseBaseline":reverse,"reverseRestored":call("reverse","--list"),"namespaceProofs":proofs,"ownedCAHelperDirectoryAbsent":True,"result":"PASS exact CA baseline/mount/helper/UID/reverse restoration; fresh native TLS negative pending"}
Path(os.environ.get("IM_STATE_ANDROID_RESTORE", "spec/progress/evidence/LOOP1-CLIENT-STATE-001/android-week2-rollback-baseline.json")).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(result["result"])
