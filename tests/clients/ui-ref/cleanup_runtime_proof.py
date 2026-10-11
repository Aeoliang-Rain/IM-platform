"""Verify task-owned resources gone; archive only public generated configuration."""
from pathlib import Path
import subprocess,json,hashlib,datetime,shutil
root=Path(__file__).resolve().parents[3];evidence=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001';private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime');project='im-gui-product-20261004-35128'
docker='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
containers=subprocess.check_output([docker,'ps','-aq','--filter','label=com.docker.compose.project='+project],text=True);volumes=subprocess.check_output([docker,'volume','ls','-q','--filter','label=com.docker.compose.project='+project],text=True);assert not containers.strip() and not volumes.strip()
command="@{listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop|Where-Object LocalPort -in 8443,18443,9467,5590,5591,5592,5593|Select-Object LocalAddress,LocalPort,OwningProcess);oldOwnedLaunchers=@(Get-CimInstance Win32_Process|Where-Object {$_.ProcessId -in 28496,36216}|Select-Object ProcessId,Name,ExecutablePath)}|ConvertTo-Json -Depth 5"
facts=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',command],text=True));assert not facts['listeners'] and not facts['oldOwnedLaunchers']
raw=private/'runtime-original.txt';assert b'PASS owned fixture cleanup; no unrelated container/volume operation' in raw.read_bytes()
public=private/'failed-c-factory-public-originals';public.mkdir(exist_ok=False);c=private/'baseline-avd';cReceipt=json.loads((evidence/'baseline-avd-created.json').read_text());assert Path(cReceipt['directory']).resolve()==c.resolve()
archives=[]
for p in sorted(c.rglob('*')):
 if p.is_file() and (p.suffix in {'.txt','.ini'} or p.name.startswith('config-')):
  relative=p.relative_to(c);destination=public/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,destination);archives.append({'original':str(p),'archive':str(destination),'SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project':project,'containersAbsent':True,'volumesAbsent':True,'processAndSocketFacts':facts,'privateOriginalCleanupLog':{'path':str(raw),'SHA256':hashlib.sha256(raw.read_bytes()).hexdigest()},'failedFactoryPublicArchives':archives,'qualification':'Snapshot public witness before manager stop preserves original semantic bytes. Original proxy manager terminates its owned process; finally-only proxy dump is not claimed. No unrelated Docker resources or original userdata removed.'}
target=evidence/'runtime-resource-cleanup.json';assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('PASS task Docker/project volumes, TLS/debug/emulator sockets and owned launcher cleanup; failed factory public logs archived')
