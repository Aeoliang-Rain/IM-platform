"""Keep isolated fixture stdin alive and guarantee child cleanup on stop/failure."""
from pathlib import Path
import os,subprocess,sys,time,json
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=Path(os.environ['IM_GUI_PRIVATE_RUNTIME']).resolve()
stop=PRIVATE/'stop-request';assert not stop.exists()
log=(PRIVATE/'runtime-original.txt').open('xb');proxylog=(PRIVATE/'proxy-original.txt').open('xb')
fixture=None;proxy=None
try:
 fixture=subprocess.Popen([sys.executable,'-Xutf8','-B','tests/clients/gui/go_runtime.py'],cwd=ROOT,env=os.environ,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT)
 for _ in range(240):
  if fixture.poll() is not None:raise RuntimeError('Fixture exited; inspect private original')
  matches=list(PRIVATE.glob('go-*/public.json'))
  if matches:
   newest=max(matches,key=lambda p:p.stat().st_mtime)
   value=json.loads(newest.read_text());project=value['project']
   if project.endswith('-'+str(fixture.pid)):
    (PRIVATE/'go-public.json').write_bytes(newest.read_bytes());break
  time.sleep(.5)
 else:raise RuntimeError('Fixture readiness timeout')
 proxy=subprocess.Popen([sys.executable,'-Xutf8','-B','tests/clients/ui-ref/state/fault_proxy.py'],cwd=ROOT,env=os.environ,stdout=proxylog,stderr=subprocess.STDOUT)
 time.sleep(2)
 if proxy.poll() is not None:raise RuntimeError('Fault relay failed; inspect original')
 print('READY source-bound isolated Go/PG/NATS and actual ACK fault relay '+project,flush=True)
 while not stop.exists():
  if fixture.poll() is not None or proxy.poll() is not None:raise RuntimeError('Owned runtime child ended unexpectedly')
  time.sleep(.5)
finally:
 if proxy and proxy.poll() is None:proxy.terminate();proxy.wait(timeout=15)
 if fixture and fixture.poll() is None:
  fixture.stdin.write(b'stop\n');fixture.stdin.flush();fixture.wait(timeout=180)
 log.close();proxylog.close()
 print('Owned runtime stopped; actual fixture cleanup log retained',flush=True)
