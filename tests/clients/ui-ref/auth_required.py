"""Four missing real Auth cases; public receipts contain no credentials/tokens."""
from pathlib import Path
import subprocess,os,json,hashlib,datetime,uuid,time,re,sys
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=Path(os.environ['IM_GUI_PRIVATE_RUNTIME']).resolve()
EVIDENCE=ROOT/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'
ADB='H:/Android/platform-tools/adb.exe';SERIAL='emulator-5592'
PY='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PWSH='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
DOCKER='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
F=json.loads((PRIVATE/'go-public.json').read_text())
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def adb(*args):return subprocess.check_output([ADB,'-s',SERIAL,*args])
def expire(client):
 uid=str(uuid.UUID(F['accounts'][0]['userId']))
 query="UPDATE sessions SET expires_at=now()-interval '1 second' WHERE user_id='"+uid+"' AND client_type='"+client+"'; SELECT json_build_object('userId',user_id,'clientType',client_type,'sessionId',session_id,'expiresBeforeNow',expires_at<now()) FROM sessions WHERE user_id='"+uid+"' AND client_type='"+client+"'"
 raw=subprocess.check_output([DOCKER,'exec',F['project']+'-postgres-1','psql','-U','im','-d','im','-v','ON_ERROR_STOP=1','-Atc',query],text=True)
 fact=json.loads(raw.splitlines()[-1]);assert fact['expiresBeforeNow'];return {'commandQualification':'Only current disposable fixture user/client slot expired through actual Go PostgreSQL; no token/password read','publicServerState':fact,'rawOriginal':raw}
def seal(out,result,**extra):
 entries=[{'file':str(p.relative_to(out)),'sha256':SHA(p)} for p in sorted(out.rglob('*')) if p.is_file()]
 (out/'manifest.json').write_text(json.dumps({'task':'LOOP1-CLIENT-UI-REF-001','actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':result,'actualHEAD':HEAD,'productSource':'1bd1a1bf015edd6422bd8bfeeb73bc454b565034','fixture':F,'entries':entries,**extra},indent=2)+'\n',encoding='utf-8')
def android():
 run='auth-required-'+uuid.uuid4().hex;out=EVIDENCE/'screens'/('android-'+run);out.mkdir()
 archive=PRIVATE/run;archive.mkdir();binding={};passed=False;child=None
 try:
  for pkg in ['im.platform.client','im.platform.client.test']:
   old=subprocess.run([ADB,'-s',SERIAL,'shell','pm','path',pkg],capture_output=True);assert not old.stdout.strip(),'Only empty owned factory device may be installed'
  for pkg,source in [('im.platform.client',Path(sys.argv[2])),('im.platform.client.test',ROOT/'clients/mobile/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk')]:
   owned=archive/(pkg+'.apk');owned.write_bytes(source.read_bytes());raw=adb('install',str(owned)).decode();assert 'Success' in raw
   path=adb('shell','pm','path',pkg).decode().strip().removeprefix('package:');actual=archive/(pkg+'-device.apk');subprocess.run([ADB,'-s',SERIAL,'pull',path,str(actual)],check=True,capture_output=True);assert SHA(actual)==SHA(owned)
   binding[pkg]={'archive':str(owned),'sha256':SHA(owned),'deviceArchive':str(actual),'deviceSHA256':SHA(actual),'devicePath':path,'installOriginal':raw}
  assert binding['im.platform.client']['sha256']==os.environ['IM_UIREF_PRODUCT_APK_SHA256']
  beforeReverse=adb('reverse','--list').decode();assert 'tcp:8443' not in beforeReverse
  adb('reverse','tcp:8443','tcp:8443');adb('shell','mkdir','-p','/sdcard/Android/data/im.platform.client/files');adb('push',str(PRIVATE/'tls-ui-ref/ca.der'),'/sdcard/Android/data/im.platform.client/files/ui-ref-ca.der')
  log=(out/'instrumentation-original.txt').open('xb')
  args=[ADB,'-s',SERIAL,'shell','am','instrument','-w','-e','uiRefCA','/sdcard/Android/data/im.platform.client/files/ui-ref-ca.der','-e','phase','auth-required','-e','stateRun',run,'-e','avery',F['accounts'][0]['username'],'im.platform.client.test/im.platform.client.ui.GuiAuthenticatedInstrumentation']
  child=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
  marker='/sdcard/Android/data/im.platform.client/files/gui-auth/'+run
  for _ in range(600):
   if subprocess.run([ADB,'-s',SERIAL,'shell','test','-f',marker+'/expiry-ready'],capture_output=True).returncode==0:break
   assert child.poll() is None,'Actual runner ended before expiry boundary';time.sleep(.2)
  else:raise RuntimeError('Actual expiry boundary unavailable')
  (out/'actual-server-expiry.json').write_text(json.dumps(expire('MOBILE'),indent=2)+'\n',encoding='utf-8')
  adb('shell','touch',marker+'/expiry-continue');child.wait(timeout=120);log.close()
  subprocess.run([ADB,'-s',SERIAL,'pull',marker,str(out/'native-originals')],check=True,capture_output=True)
  raw=(out/'instrumentation-original.txt').read_text(encoding='utf-8')
  assert child.returncode==0 and 'INSTRUMENTATION_RESULT: result=PASS' in raw
  for key in ['logoutSecureSlotAbsent','expiredSecureSlotAbsent','actualDefaultSocketTLSHostnamePositive','defaultHostnameMismatch','testTrustRestore']:assert key+'=PASS' in raw
  for pkg,b in binding.items():assert hashlib.sha256(adb('exec-out','cat',b['devicePath'])).hexdigest()==b['sha256']
  pid=int(re.search(r'targetProcessId=(\d+)',raw).group(1));passed=True
  print('PASS actual Android wrong-password, completed logout, actual server-expired refresh and credential/session clearing; '+str(out),flush=True)
 finally:
  if child and child.poll() is None:child.terminate();child.wait(timeout=15)
  seal(out,'PASS' if passed else 'FAIL',serial=SERIAL,androidBinding=binding,positivePID=pid if passed else None,TLSQualification='Pinned test-process context/socket factory only; native HttpsURLConnection/default hostname verification; original provider/context/factory restored by runner finally. No system roots modified.')
def desktop():
 out=EVIDENCE/'screens'/('desktop-auth-required-'+uuid.uuid4().hex);out.mkdir();passed=False
 def ui(action='observe',name='',value='',label='observe'):
  p=out/(label+'.png');r=subprocess.run([PWSH,'-NoProfile','-File','tests/clients/ui-ref/state/desktop_window.ps1','-Action',action,'-Name',name,'-Value',value,'-Output',str(p)],cwd=ROOT,capture_output=True,timeout=45)
  (out/(label+'-command-original.txt')).write_bytes(r.stdout+r.stderr);assert r.returncode==0,'Actual native UI failed '+label
  return json.loads(Path(str(p)+'.json').read_text(encoding='utf-8'))['nodes']
 def wait(name,label):
  for n in range(50):
   nodes=ui(label=label+'-'+str(n))
   if any(x['name']==name and not x['offscreen'] for x in nodes):return nodes
   time.sleep(.2)
  raise RuntimeError('Actual native UI state absent '+name)
 try:
  initial=ui(label='anonymous-before');assert any(x['name']=='Username' and x['type']=='ControlType.Edit' for x in initial)
  ui('fill','Username',F['accounts'][0]['username'],'fixture-username');ui('fill','Password','fixture-password-not-a-real-secret','fixture-password');ui('click','Sign in',label='login')
  wait('Online','logged-in');ui('click','⚙ Settings',label='settings');ui('click','Go offline',label='disconnect');ui(label='session-before-expiry')
  (out/'actual-server-expiry.json').write_text(json.dumps(expire('DESKTOP'),indent=2)+'\n',encoding='utf-8');ui('click','Refresh session',label='refresh-expired')
  nodes=wait('Session expired. Sign in again.','session-expired')
  assert any(x['name']=='Username' and x['type']=='ControlType.Edit' and x['enabled'] for x in nodes)
  assert any(x['name']=='Sign in' and x['type']=='ControlType.Button' and x['enabled'] for x in nodes)
  assert not any(x['name'] in ['Please wait…','⚙ Settings','Session expired; secure credential cleanup failed'] for x in nodes)
  passed=True;print('PASS actual installed native default-TLS session-expired classification and anonymous idle UI; '+str(out),flush=True)
 finally:seal(out,'PASS' if passed else 'FAIL',runtimeQualification='Installed current source1bd native reqwest system TLS; actual owned user DESKTOP session expired in Go PostgreSQL; user-operated Refresh through real UI, no mock transport or synthetic ViewModel calls. UI anonymity/idle observed; no claim to directly reading session/credential contents.')
if __name__=='__main__':
 {'android':android,'desktop':desktop}[sys.argv[1]]()
