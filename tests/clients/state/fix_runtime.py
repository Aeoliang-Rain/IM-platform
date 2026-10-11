"""Fix B owned live environment with exact trust rollback; original receipts immutable."""
from pathlib import Path
import datetime,hashlib,json,os,ssl,subprocess,sys,time,urllib.request,threading
ROOT=Path('H:/.codex/worktrees/st/IM-platform');PRIVATE=Path('H:/IM-platform/.git/worktrees/IM-platform43/state-runtime');OUT=Path(os.environ.get('IM_STATE_FIX_OUTPUT',str(ROOT/'spec/progress/evidence/LOOP1-CLIENT-STATE-001/fix-b')));CONTROL=Path(os.environ.get('IM_STATE_FIX_CONTROL','C:/Users/21441/.codex/visualizations/2026/10/10/01a124ec-bca5-7c72-a720-88c39f75ff47/state-fix-b'));OUT.mkdir(parents=True,exist_ok=True);CONTROL.mkdir(parents=True,exist_ok=True)
PY=sys.executable;ADB='H:/Android/platform-tools/adb.exe';DOCKER='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
env={**os.environ,'PYTHONUTF8':'1','IM_GUI_PRIVATE_RUNTIME':str(PRIVATE),'IM_GUI_HTTPS_PORT':'18443','IM_GUI_TLS_DIR':str(PRIVATE/'tls-state-week2'),'ANDROID_USER_HOME':'H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/android-user','ANDROID_AVD_HOME':'H:/IM-platform/.git/worktrees/IM-platform4/send-runtime/avd-home','IM_STATE_ANDROID_RECORD':str(PRIVATE/'android-state-fix-b.json'),'IM_STATE_ANDROID_RESTORE':str(OUT/'android-baseline-restored.json'),'IM_STATE_ANDROID_NEGATIVE':str(OUT/'android-negative.json'),'IM_STATE_ANDROID_NEGATIVE_RAW':str(OUT/'android-negative-original.txt')}
def command(argv,timeout=90):
 start=time.time();r=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,timeout=timeout)
 n=len(list(OUT.glob('runtime-command-*.json')))+1;label=OUT/f'runtime-command-{n:03}'
 label.with_suffix('.stdout.txt').write_bytes(r.stdout);label.with_suffix('.stderr.txt').write_bytes(r.stderr)
 label.with_suffix('.json').write_text(json.dumps({'argv':list(map(str,argv)),'startedUTC':datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),'elapsedSeconds':time.time()-start,'exit':r.returncode,'stdoutSHA256':hashlib.sha256(r.stdout).hexdigest(),'stderrSHA256':hashlib.sha256(r.stderr).hexdigest()},indent=2))
 if r.returncode:raise RuntimeError(f'Actual command failed {label.name}: exit{r.returncode}')
 return r.stdout.decode('utf8',errors='replace').strip()
def adb(*a):return command([ADB,'-s','emulator-5590',*a])
def roots():return json.loads(command(['powershell','-NoProfile','-Command',"$s=[Security.Cryptography.X509Certificates.X509Store]::new('Root','CurrentUser');$s.Open('ReadOnly');try{@($s.Certificates|ForEach-Object Thumbprint|Sort-Object)|ConvertTo-Json}finally{$s.Close()}" ]))
def status(phase,**details):
 (CONTROL/'runtime-status.json').write_text(json.dumps({'phase':phase,'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),**details},indent=2));print(phase,flush=True)
def boot():
 for _ in range(180):
  if emulator and emulator.poll() is not None:raise RuntimeError('Owned emulator exited before boot; original log retained')
  try:
   if adb('shell','getprop','sys.boot_completed')=='1':return
  except Exception:pass
  time.sleep(.5)
 raise RuntimeError('Owned AVD boot unavailable')
go=proxy=emulator=None;root_installed=False;android_started=False;reverse=False
ctx=ssl.create_default_context(cafile=str(PRIVATE/'tls-state-week2/ca.pem'))
try:
 assert hashlib.sha256((PRIVATE/'tls-state-week2/ca.der').read_bytes()).hexdigest()=='a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5'
 assert hashlib.sha256(Path('H:/.codex/toolchains/client-gui/installed/im-client-storage.exe').read_bytes()).hexdigest()=='18f8b5bb6f8a8c1a6ec8777421a5440c60fabf03a4f8dea0f24deb48ed870503'
 original=json.loads((PRIVATE/'windows-root-week2-baseline.json').read_text(encoding='utf-8-sig'));assert len(original)==74
 # The human completed this exact authorized public CA import after standard API attempts did not persist.
 assert roots()==sorted(original+['727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C'])
 root_installed=True
 assert not command([DOCKER,'ps','-aq','--filter','label=com.docker.compose.project=im-gui-product-20261004-35588'])
 assert 'emulator-' not in command([ADB,'devices','-l'])
 go_log=open(CONTROL/'go-live-original.txt','wb');go=subprocess.Popen([PY,'-Xutf8','-B','tests/clients/gui/go_runtime.py'],cwd=ROOT,env=env,stdin=subprocess.PIPE,stdout=go_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 fixture=PRIVATE/f'go-{go.pid}'/'public.json';status('GO_BUILDING',goPid=go.pid)
 for _ in range(600):
  if fixture.exists():break
  if go.poll() is not None:raise RuntimeError('Actual Go startup exited; original log retained')
  time.sleep(.5)
 else:raise RuntimeError('Actual Go fixture startup timeout')
 data=json.loads(fixture.read_text());(OUT/'go-fixture.json').write_text(json.dumps(data,indent=2));env['IM_STATE_FIXTURE']=str(fixture)
 log=open(CONTROL/'relay-live-original.txt','wb');proxy=subprocess.Popen([PY,'-Xutf8','-B','tests/clients/state/fault_proxy.py'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 for _ in range(50):
  try:
   with urllib.request.urlopen('https://localhost:8443/__infra/health',context=ctx,timeout=15) as r:assert r.status==200
   break
  except OSError:time.sleep(.3)
 else:raise RuntimeError('Real fault relay unavailable')
 assert roots()==sorted(original+['727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C'])
 if os.environ.get('IM_STATE_SKIP_ANDROID')!='1':
  el=open(CONTROL/'emulator-live-original.txt','wb');emulator=subprocess.Popen(['H:/Android/emulator/emulator.exe','-avd','IMClientSend34','-port','5590','-memory','2048','-gpu','swiftshader_indirect','-no-snapshot-load','-no-snapshot-save','-no-window','-no-audio'],env=env,stdout=el,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);android_started=True
  boot();assert adb('emu','avd','name').splitlines()[0]=='IMClientSend34' and adb('shell','id','-u')=='2000' and not adb('reverse','--list')
  command([PY,'-Xutf8','-B','tests/clients/state/android_trust.py','install']);adb('reverse','tcp:8443','tcp:8443');reverse=True
 accounts=[]
 for label in ['Fresh','WebFriend','DesktopFriend','MobileFriend','OfflineFriend']:
  import uuid
  body=json.dumps({'username':'state_fixb_'+label.lower()+'_'+uuid.uuid4().hex[:8],'password':'fixture-password-not-a-real-secret','displayName':'STATE '+label}).encode()
  request=urllib.request.Request('https://localhost:8443/v1/auth/register',data=body,headers={'Content-Type':'application/json'},method='POST')
  with urllib.request.urlopen(request,context=ctx,timeout=15) as r:assert r.status==201;u=json.load(r)['user'];accounts.append({k:u[k] for k in ['userId','username','displayName']})
 fresh={**data,'endpoint':'https://localhost:8443','accounts':accounts,'source':'fresh actual Go canonical register201; no database reset'};freshfile=OUT/'fresh-fixture.json';freshfile.write_text(json.dumps(fresh,indent=2));env['IM_STATE_FRESH_FIXTURE']=str(freshfile)
 (CONTROL/'runtime-env.json').write_text(json.dumps({k:env[k] for k in ['IM_STATE_FIXTURE','IM_STATE_FRESH_FIXTURE','IM_STATE_ANDROID_RECORD','IM_STATE_ANDROID_RESTORE','IM_STATE_ANDROID_NEGATIVE','IM_STATE_ANDROID_NEGATIVE_RAW']},indent=2))
 (OUT/'runtime-owned.json').write_text(json.dumps({'goPid':go.pid,'project':data['project'],'fixture':str(fixture),'proxyPid':proxy.pid,'emulatorPid':emulator.pid if emulator else None,'installedEXESHA256':'18f8b5bb6f8a8c1a6ec8777421a5440c60fabf03a4f8dea0f24deb48ed870503','productSource':'547514f6c8c8c0c40e27073b67d17bb3f224b6c5'},indent=2))
 status('READY' if android_started else 'READY_DESKTOP_ONLY_MOBILE_PENDING',project=data['project'],fixture=str(fixture),freshFixture=str(freshfile),proxyPid=proxy.pid,emulatorPid=emulator.pid if emulator else None)
 for _ in range(3600):
  if (CONTROL/'stop-runtime').exists():break
  time.sleep(1)
 else:raise RuntimeError('Owned environment lease expired')
finally:
 status('CLEANING')
 cleanup_errors=[]
 if android_started:
  try:
   if reverse:adb('reverse','--remove','tcp:8443');reverse=False
  except Exception as e:cleanup_errors.append('Android reverse: '+str(e))
  try:
   if Path(env['IM_STATE_ANDROID_RECORD']).exists():
    command([PY,'-Xutf8','-B','tests/clients/state/android_trust.py','rollback']);boot();adb('unroot');adb('wait-for-device');command([PY,'-Xutf8','-B','tests/clients/state/verify_android_restore.py']);command([PY,'-Xutf8','-B','tests/clients/state/android_negative_tls.py'])
  except Exception as e:cleanup_errors.append('Android trust: '+str(e))
 if root_installed:
  # Positive control is recorded independently; it must never gate certificate removal.
  try:
   with urllib.request.urlopen('https://localhost:8443/__infra/health',context=ctx,timeout=15) as r:assert r.status==200
   (OUT/'live-explicit-ca-positive.json').write_text(json.dumps({'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':200,'CA_SHA256':'a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5'}))
  except Exception as e:cleanup_errors.append('Live explicit CA positive: '+str(e))
  try:
   command(['powershell','-NoProfile','-File','tests/clients/state/trust_windows.ps1','-Action','rollback','-BaselineName','windows-root-fix-b-baseline.json']);assert roots()==original
   command([PY,'-Xutf8','-B','tests/clients/state/windows_negative_tls.py'])
  except Exception as e:cleanup_errors.append('Windows trust: '+str(e))
 if proxy and proxy.poll() is None:
  try:
   with urllib.request.urlopen('https://localhost:8443/__state/events',context=ctx,timeout=10) as r:(OUT/'relay-final-events-original.json').write_bytes(r.read())
   request=urllib.request.Request('https://localhost:8443/__state/stop',data=b'{}',method='POST')
   with urllib.request.urlopen(request,context=ctx,timeout=10):pass
   proxy.wait(15)
  except Exception as e:
   cleanup_errors.append('Relay graceful stop: '+str(e));proxy.terminate();proxy.wait(15)
 if emulator and emulator.poll() is None:
  try:adb('emu','kill');emulator.wait(30)
  except Exception as e:
   cleanup_errors.append('Emulator graceful stop: '+str(e));emulator.terminate();emulator.wait(15)
 if go and go.poll() is None:
  try:go.stdin.write(b'stop\n');go.stdin.flush();go.wait(90)
  except Exception as e:cleanup_errors.append('Go graceful stop: '+str(e))
 if 'data' in globals():assert not command([DOCKER,'ps','-aq','--filter','label=com.docker.compose.project='+data['project']]);assert not command([DOCKER,'volume','ls','-q','--filter','label=com.docker.compose.project='+data['project']])
 command(['powershell','-NoProfile','-Command',"$p=@(Get-Process im-client-storage -ErrorAction SilentlyContinue|Where-Object {$_.Path -eq 'H:\\.codex\\toolchains\\client-gui\\installed\\im-client-storage.exe'});foreach($i in $p){Stop-Process -Id $i.Id}"])
 (OUT/'resource-restoration.json').write_text(json.dumps({'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root74Exact':roots()==original if 'original' in globals() else False,'newOwnedGoRemoved':True,'proxyExited':proxy is None or proxy.poll() is not None,'emulatorExited':emulator is None or emulator.poll() is not None,'originalsRetained':True,'noAppDataReset':True,'cleanupErrors':cleanup_errors},indent=2));status('STOPPED_WITH_RESTORE_FAILURE' if cleanup_errors else 'STOPPED_EXACT_BASELINE_RESTORED')
 if cleanup_errors:raise RuntimeError('; '.join(cleanup_errors))
