"""Durable local command facts, separate from task acceptance and Research Recorder."""
from pathlib import Path
import argparse,datetime,json,os,subprocess,time,uuid
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--cwd',default='.');p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
args=a.command[1:] if a.command[:1]==['--'] else a.command
assert args
cwd=(ROOT/a.cwd).resolve();assert cwd==ROOT or cwd.is_relative_to(ROOT)
out=ROOT/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/local';out.mkdir(parents=True,exist_ok=True)
name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'}
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
started=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.monotonic()
run=subprocess.run(args,cwd=cwd,env=env,capture_output=True)
for label,data in [('stdout',run.stdout),('stderr',run.stderr)]: (out/(name+'.'+label+'.txt')).write_bytes(data)
(out/(name+'.json')).write_text(json.dumps({'actualStartUTC':started,'actualEndUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedSeconds':time.monotonic()-clock,'command':args,'cwd':str(cwd),'actualCaptureHead':head,'actualStatusBefore':status,'exitCode':run.returncode,'result':'PASS' if run.returncode==0 else 'FAIL','stdout':name+'.stdout.txt','stderr':name+'.stderr.txt'},indent=2)+'\n',encoding='utf-8')
print(run.stdout.decode('utf-8',errors='replace'));print(run.stderr.decode('utf-8',errors='replace'))
raise SystemExit(run.returncode)
