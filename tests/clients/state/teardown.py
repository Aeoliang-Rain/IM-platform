"""Exact registered test resources only; preserve installed candidates and all application data."""
from pathlib import Path
import datetime, json, os, ssl, subprocess, time, urllib.request

private=Path('H:/IM-platform/.git/worktrees/IM-platform43/state-runtime')
out=Path('spec/progress/evidence/LOOP1-CLIENT-STATE-001')
def ps(code):return subprocess.check_output(['powershell','-NoProfile','-Command',code],text=True,encoding='utf-8',timeout=12)
proxy=json.loads(ps('Get-CimInstance Win32_Process -Filter "ProcessId=38928" | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json'))
assert proxy['ExecutablePath'].replace('\\','/')=='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
assert proxy['CommandLine'].endswith(' -B tests/clients/state/fault_proxy.py')
assert int((private/'emulator.pid').read_text(encoding='utf-8-sig').strip())==4656
emulator=json.loads(ps('Get-CimInstance Win32_Process -Filter "ProcessId=4656" | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json'))
assert emulator['ExecutablePath'].replace('\\','/')=='H:/Android/emulator/emulator.exe'
assert ' -avd IMClientSend34 -port 5590 ' in emulator['CommandLine'] and '-no-snapshot-save' in emulator['CommandLine']
ctx=ssl.create_default_context(cafile=str(private/'tls-state-week2/ca.pem'))
with urllib.request.urlopen('https://localhost:8443/__state/events',context=ctx,timeout=10) as r:events=r.read()
(out/'relay-final-events-original.json').write_bytes(events)
req=urllib.request.Request('https://localhost:8443/__state/stop',data=b'{}',method='POST')
with urllib.request.urlopen(req,context=ctx,timeout=10) as r:assert r.status==200
for _ in range(40):
    found=ps('if(Get-Process -Id 38928 -ErrorAction SilentlyContinue){"PRESENT"}').strip()
    if not found:break
    time.sleep(.2)
else:raise RuntimeError('Owned relay did not stop')
env={**os.environ,'ANDROID_USER_HOME':'H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user'}
def adb(*args):return subprocess.check_output(['H:/Android/platform-tools/adb.exe','-s','emulator-5590',*args],env=env,text=True,encoding='utf-8',timeout=15).strip()
assert adb('shell','id','-u')=='2000' and adb('shell','getenforce')=='Enforcing' and not adb('reverse','--list')
assert adb('emu','avd','name').splitlines()[0]=='IMClientSend34'
adb('emu','kill')
desktop=ps("$p=@(Get-Process im-client-storage -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'H:\\.codex\\toolchains\\client-gui\\installed\\im-client-storage.exe'});foreach($item in $p){Stop-Process -Id $item.Id};@{stoppedOwnedPID=@($p|ForEach-Object Id);installedCandidateRetained=$true;appDataOperation='none'}|ConvertTo-Json")
proof={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registeredProxy':proxy,'proxyStopped':True,'registeredEmulator':emulator,'adbBeforeStop':{'uid':'2000','reverse':[],'SELinux':'Enforcing'},'emulatorStopRequested':True,'desktop':json.loads(desktop),'retained':'Controlled Windows18f8/Android current candidate install, baseline snapshot, all account databases/appearance/secure slots preserved. Go runtime receives its own stop separately; no unrelated resource operation.'}
(out/'runtime-teardown.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print('PASS exact owned relay/AVD/app teardown; installed candidates and all AppData retained')
