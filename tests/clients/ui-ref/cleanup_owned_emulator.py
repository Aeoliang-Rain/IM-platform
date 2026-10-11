"""Close only task-started5590; preserve original AVD and unknown account data."""
from pathlib import Path
import subprocess,json,hashlib,time,datetime
root=Path(__file__).resolve().parents[3];evidence=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001';adb='H:/Android/platform-tools/adb.exe'
def call(*args):return subprocess.check_output([adb,'-s','emulator-5590',*args])
def processes():
 text=subprocess.check_output(['powershell','-NoProfile','-Command',"$all=@(Get-CimInstance Win32_Process);$family=@(28496);do{$found=@($all|Where-Object {$family -contains $_.ParentProcessId -and $family -notcontains $_.ProcessId}|ForEach-Object ProcessId);$family+=$found}while($found.Count);@($all|Where-Object {$family -contains $_.ProcessId}|Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine)|ConvertTo-Json"],text=True)
 value=json.loads(text) if text.strip() else [];return value if isinstance(value,list) else [value]
before=processes();launcher=next(p for p in before if p['ProcessId']==28496)
assert launcher['ExecutablePath'].lower()=='h:\\android\\emulator\\emulator.exe' and '-avd IMClientSend34 -port 5590' in launcher['CommandLine']
reverseBefore=call('reverse','--list').decode();owned=[line for line in reverseBefore.splitlines() if 'tcp:8443' in line.split()];assert len(owned)==1 and owned[0].split()[-2:]==['tcp:8443','tcp:8443']
certificate='/sdcard/Android/data/im.platform.client/files/ui-ref-ca.der';certificateHash=hashlib.sha256(call('exec-out','cat',certificate)).hexdigest();assert certificateHash=='a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5'
unknown='databases/im-9c73d299-ed01-487f-857c-c3fbd74de0ce.sqlite';call('shell','run-as','im.platform.client','test','-f',unknown)
pidBefore=subprocess.run([adb,'-s','emulator-5590','shell','pidof','im.platform.client'],capture_output=True).stdout.decode().strip();assert not pidBefore or pidBefore.isdecimal()
if pidBefore:call('shell','am','force-stop','im.platform.client')
assert not subprocess.run([adb,'-s','emulator-5590','shell','pidof','im.platform.client'],capture_output=True).stdout.strip()
call('reverse','--remove','tcp:8443');reverseAfter=call('reverse','--list').decode();assert sorted(reverseAfter.splitlines())==sorted(line for line in reverseBefore.splitlines() if line not in owned)
call('shell','rm',certificate);assert subprocess.run([adb,'-s','emulator-5590','shell','test','-e',certificate]).returncode==1
call('shell','run-as','im.platform.client','test','-f',unknown)
kill=call('emu','kill').decode()
for _ in range(60):
 if not processes():break
 time.sleep(.5)
assert not processes(),'Owned launcher/child family did not exit'
devices=subprocess.check_output([adb,'devices'],text=True);assert 'emulator-5590' not in devices and 'emulator-5592' not in devices
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'beforeOwnedFamily':before,'ownedPackagePIDBefore':pidBefore or None,'ownedPackageStopped':True,'reverseBefore':reverseBefore,'reverseAfter':reverseAfter,'removedExactTaskCAFile':{'devicePath':certificate,'DERHash':certificateHash},'unknownAccountDatabasePresentBeforeAndAfterOwnedFileRemoval':True,'unknownDataQualification':'Filename existence only; no unknown DB content read/copied/reset/deleted. Original AVD userdata remains on disk. App package data and controlled old relationships remain.','emulatorKillRaw':kill,'ownedFamilyGone':True,'bothOwnedSerialsAbsent':True,'devicesAfter':devices}
target=evidence/'owned-emulator-cleanup.json';assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('PASS owned5590 package/CAfile/reverse/emulatorfamily cleanup; original unknown userdata preserved')
