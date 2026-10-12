"""Real Go/PG/NATS Web i18n harness. Owns only a loopback fault relay/browser.
Existing parent-owned services, CA and fixture accounts are prerequisites.
No trust mutation, generated ACK, backend start or repository evidence writes.
"""
from pathlib import Path
import argparse,hashlib,http.client,json,os,re,socket,ssl,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
RELAY_SHA='88fe2660b52b62abaf7a715eae0e6014db853b462e9eef8bf2603e0765ec6b7e'
BASE_JS_SHA='bb1499788615f01d00b0447f51a469d3e08fa2d43d1cc40a176ae53b29069c7a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def run(argv,timeout=30):
 p=subprocess.run(list(map(str,argv)),cwd=ROOT,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError('Subcommand failed: '+Path(str(argv[0])).name+' exit='+str(p.returncode)+'; private output withheld')
 return p.stdout.decode('utf8').strip()
def inventory(base):
 data={}
 if base.is_symlink():raise ValueError('Symlink input forbidden')
 for p in sorted(base.rglob('*')):
  if p.is_symlink():raise ValueError('Symlink input forbidden')
  if p.is_file():data[p.relative_to(base).as_posix()]=sha(p)
 return data
def source():return {n:inventory(ROOT/n) for n in ('clients/web','clients/shared')}
def external(value):
 p=Path(value)
 if not p.is_absolute():raise ValueError('Absolute external path required')
 p=p.resolve()
 if p==ROOT or ROOT in p.parents:raise ValueError('Output/runtime input must be outside repository')
 return p
def relay_source(build,tls,private):
 p=ROOT/'tests/clients/ui-ref/state/fault_proxy.py'
 if sha(p)!=RELAY_SHA:raise ValueError('Readonly fault relay changed: require new author inspection')
 text=p.read_text(encoding='utf8')
 def swap(old,new,count=1):
  nonlocal text
  if text.count(old)!=count:raise ValueError('Relay exact substitution count mismatch')
  text=text.replace(old,new)
 swap('ROOT=Path(__file__).resolve().parents[4]','ROOT=Path('+repr(str(ROOT))+')')
 line=next(x for x in text.splitlines() if x.startswith('PRIVATE=Path(os.environ.get('))
 swap(line,'PRIVATE=Path('+repr(str(private))+')')
 swap("TLS=PRIVATE/'tls-ui-ref'",'TLS=Path('+repr(str(tls))+')')
 swap("PRIVATE/'web-build'",'BUILD',2)
 swap("PRIVATE/'web-build/index.html'","BUILD/'index.html'")
 swap("'localhost',18443","'localhost',8443",2)
 swap("(('127.0.0.1',8443),Handler)","(('127.0.0.1',18444),Handler)")
 swap('READY actual-Go fault relay https://localhost:8443','READY actual-Go fault relay https://localhost:18444')
 # Same original relay/event semantics; only explicit filesystem/port config.
 compile(text,str(p),'exec')
 return text,{'readonly_source_sha256':RELAY_SHA,'configured_source_sha256':hashlib.sha256(text.encode()).hexdigest(),'substitutions':'ROOT/PRIVATE/TLS/BUILD/listener18444/upstream8443 only'}
def parse():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--assigned-root',required=True);p.add_argument('--source-sha',required=True);p.add_argument('--wip',action='store_true')
 p.add_argument('--out',required=True);p.add_argument('--build',required=True);p.add_argument('--build-binding',required=True);p.add_argument('--fixture-public',required=True);p.add_argument('--tls-dir',required=True)
 p.add_argument('--node',required=True);p.add_argument('--playwright-module',required=True);p.add_argument('--docker',required=True)
 b=p.add_mutually_exclusive_group();b.add_argument('--browser-exe');b.add_argument('--browser-channel',default='msedge')
 p.add_argument('--relay-child',action='store_true',help=argparse.SUPPRESS)
 return p.parse_args()
def main():
 a=parse();out=None;proc=None;log=None;report={'result':'PENDING','scope':'real existing Go/PG/NATS Web i18n; local evidence only'};failed=None
 try:
  if Path(a.assigned_root).resolve()!=ROOT or Path(run(['git','rev-parse','--show-toplevel'])).resolve()!=ROOT:raise ValueError('WORKSPACE_ERROR assigned Git root mismatch')
  if not re.fullmatch(r'[a-f0-9]{40}',a.source_sha) or run(['git','rev-parse','HEAD'])!=a.source_sha:raise ValueError('Exact actual HEAD required')
  dirty=bool(run(['git','-c','core.excludesFile=.git/info/exclude','status','--porcelain=v1','--untracked-files=all']))
  if dirty and not a.wip:raise ValueError('Dirty source requires explicit --wip')
  build=external(a.build);tls=external(a.tls_dir);out=external(a.out)
  if build in out.parents or tls in out.parents or out in build.parents or out in tls.parents or out==build or out==tls:raise ValueError('Fresh output must not overlap static build or owned TLS directory')
  if not re.fullmatch(r'[A-Za-z0-9-]{1,80}',out.name):raise ValueError('Safe unique output basename required')
  if a.relay_child:
   if not (out/'relay').is_dir():raise ValueError('Parent-owned relay directory required')
   configured,meta=relay_source(build,tls,out/'relay');emit(out/'relay/config.json',meta)
   exec(compile(configured,str(ROOT/'tests/clients/ui-ref/state/fault_proxy.py'),'exec'),{'__file__':str(ROOT/'tests/clients/ui-ref/state/fault_proxy.py'),'__name__':'__main__','BUILD':build})
   return 0
  if out.exists():raise ValueError('Fresh nonexistent external output required')
  if not build.is_dir() or not (build/'index.html').is_file():raise ValueError('Actual retained compiled Web build required')
  for name in ('server.pem','server.key','ca.pem'):
   if not (tls/name).is_file():raise ValueError('Owned TLS prerequisite missing')
  for name in ('node','playwright_module','docker'):
   if not Path(getattr(a,name)).is_file():raise ValueError('Existing explicit tool path required')
  if a.browser_exe and not Path(a.browser_exe).is_file():raise ValueError('Existing browser executable required')
  if not a.browser_exe and a.browser_channel!='msedge':raise ValueError('Default Edge TLS requires msedge channel or explicit approved Edge executable')
  binding_path=external(a.build_binding);binding=json.loads(binding_path.read_text(encoding='utf8'))
  before=source();built=inventory(build)
  if binding.get('result')!='PASS_LOCAL_CHECKS' or binding.get('mode')!='stage' or binding.get('source_sha')!=a.source_sha or binding.get('source_inputs')!=before or binding.get('build_files')!=built or Path(binding.get('web_build_dir','')).resolve()!=build:raise ValueError('Build/source binding mismatch; restage actual current source')
  if not a.wip and not binding.get('source_is_clean_committed_candidate'):raise ValueError('Clean candidate requires its own clean committed build binding')
  public_path=external(a.fixture_public);public=json.loads(public_path.read_text(encoding='utf8'))
  if public.get('endpoint')!='https://localhost:8443' or not public.get('status','').startswith('actual owned Go/PG/NATS') or not re.fullmatch(r'im-gui-product-[A-Za-z0-9-]+',public.get('project','')):raise ValueError('Actual owned Go/PG/NATS public fixture on8443 required')
  for user in public.get('accounts',[]):
   if not re.fullmatch(r'gui_[A-Za-z0-9_]+',user.get('username','')) or not user.get('displayName','').startswith('GUI Fixture ') or not re.fullmatch(r'[a-f0-9-]{36}',user.get('userId','')):raise ValueError('Only controlled fixture accounts allowed')
  if len(public.get('accounts',[]))<2 or not re.fullmatch(r'[a-f0-9-]{36}',public.get('conversationId','')):raise ValueError('Actual public fixture identities missing')
  for suffix in ('postgres-1','nats-1'):
   container=public['project']+'-'+suffix
   label=run([a.docker,'inspect','--format','{{index .Config.Labels "com.docker.compose.project"}}',container])
   running=run([a.docker,'inspect','--format','{{.State.Running}}',container])
   if label!=public['project'] or running!='true':raise ValueError('Actual PG/NATS project not running')
  # Read the owned CA only for a strict TLS probe; never install/modify trust.
  ca=ssl.create_default_context(cafile=str(tls/'ca.pem'))
  upstream=http.client.HTTPSConnection('localhost',8443,context=ca,timeout=10)
  try:
   upstream.request('GET','/__infra/health');response=upstream.getresponse();response.read()
   if response.status!=200:raise ValueError('Actual upstream health unavailable')
  finally:upstream.close()
  # Reserve-check only; a racing bind fails the owned child, never stops another listener.
  with socket.socket() as probe:probe.bind(('127.0.0.1',18444))
  if sha(ROOT/'tests/clients/ui-ref/state/web_actual.mjs')!=BASE_JS_SHA:raise ValueError('A/B baseline assertions changed; author reinspection required')
  configured,relay_meta=relay_source(build,tls,out/'relay')
  out.mkdir(parents=True);(out/'relay').mkdir()
  report.update(source_sha=a.source_sha,wip=bool(a.wip),source_is_clean_committed_candidate=not dirty and not a.wip,source_inputs=before,build_files=built,build_binding_sha256=sha(binding_path),fixture_public_sha256=sha(public_path),backend_project=public['project'],upstream='https://localhost:8443',relay='https://localhost:18444',relay_config=relay_meta,helper_sha256=sha(Path(__file__)),actual_js_sha256=sha(ROOT/'tests/clients/i18n/actual.mjs'),baseline_ab_sha256=BASE_JS_SHA,started_unix=time.time(),cleanup={'backend':'parent-owned unchanged','trust':'parent-owned unchanged'})
  config=dict(out=str(out),build=str(build),source_sha=a.source_sha,wip=bool(a.wip),clean=not dirty and not a.wip,fixture=public,origin='https://localhost:18444',playwright_module=str(Path(a.playwright_module).resolve()),browser_exe=a.browser_exe,browser_channel=a.browser_channel,docker=str(Path(a.docker).resolve()),source_inputs=before,build_files=built)
  emit(out/'config.json',config)
  child=[sys.executable,'-Xutf8','-B',str(Path(__file__)),*sys.argv[1:],'--relay-child']
  log=open(out/'relay/relay.log','wb');proc=subprocess.Popen(child,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  ready=False;deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   if proc.poll() is not None:raise RuntimeError('Owned relay exited before readiness; inspect retained relay log')
   # Readiness comes from our child, not a preexisting/racing external listener.
   if 'READY actual-Go fault relay https://localhost:18444' in (out/'relay/relay.log').read_text(encoding='utf8',errors='replace'):
    connection=http.client.HTTPSConnection('localhost',18444,context=ca,timeout=2)
    try:
     connection.request('GET','/__state/events');r=connection.getresponse();payload=r.read()
     if r.status==200 and json.loads(payload)==[]:ready=True;break
    finally:connection.close()
   time.sleep(.1)
  if not ready:raise RuntimeError('Owned relay readiness timeout')
  env=os.environ.copy();env['I18N_REAL_CONFIG']=str(out/'config.json')
  result=subprocess.run([a.node,str(ROOT/'tests/clients/i18n/actual.mjs')],cwd=ROOT,env=env,capture_output=True,timeout=600)
  # JS deliberately emits only generic status; no browser request URLs/auth values.
  (out/'browser-status.log').write_text('exit='+str(result.returncode)+'\n'+result.stdout.decode('utf8','replace')[:2000],encoding='utf8')
  if result.returncode:raise RuntimeError('Real browser assertion failed; inspect sanitized browser-result.json/failure screenshot')
  observed=json.loads((out/'browser-result.json').read_text(encoding='utf8'))
  if observed.get('result')!='PASS_LOCAL_CHECKS' or len(observed.get('proofs',[]))!=6:raise ValueError('Six actual locale/A/B proofs required')
  if source()!=before or inventory(build)!=built or run(['git','rev-parse','HEAD'])!=a.source_sha:raise ValueError('Relevant source/build/HEAD changed during actual verification')
  report['browser']='PASS_LOCAL_CHECKS'
 except BaseException as e:failed=type(e).__name__+': '+str(e)
 finally:
  if proc:
   stopped=False
   try:
    if proc.poll() is None:
     # Only called after our child proved readiness; never kill by port/name.
     if locals().get('ready',False):
      c=http.client.HTTPSConnection('localhost',18444,context=ca,timeout=4)
      try:c.request('POST','/__state/stop',body=b'{}');r=c.getresponse();r.read();stopped=r.status==200
      finally:c.close()
     proc.wait(timeout=10)
    stopped=stopped or proc.returncode==0
   except BaseException:
    proc.terminate()
    try:proc.wait(timeout=5)
    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
   if log:log.close()
   report['cleanup']['relay_process_exited']=proc.poll() is not None
   report['cleanup']['relay_graceful_stop']=stopped
   events=list((out/'relay').glob('fault-events-*.json'))
   if not events:failed=failed or 'Owned relay final event log missing; cleanup/evidence incomplete'
   report['relay_event_files']={p.name:sha(p) for p in events}
  report['result']='FAIL' if failed else 'PASS_LOCAL_CHECKS'
  if failed:report['failure']=failed
  report['finished_unix']=time.time()
  if out and out.is_dir() and (out/'config.json').exists():emit(out/'binding.json',report)
  print(report['result']+'; external binding/browser-result; no trust/backend mutation; no independent acceptance')
 return 1 if failed else 0
if __name__=='__main__':sys.exit(main())
