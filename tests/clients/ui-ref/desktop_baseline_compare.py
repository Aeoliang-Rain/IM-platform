"""Bounded accepted-artifact comparison; finally restore exact candidate3 files."""
from pathlib import Path
import subprocess, json, hashlib, datetime, uuid, shutil
root=Path(__file__).resolve().parents[3]
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
target=Path('H:/.codex/toolchains/client-gui/installed')
assert target.resolve()==Path('H:/.codex/toolchains/client-gui/installed').resolve()
baseline=private/'desktop-before';original=json.loads((baseline/'original.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for e in original:assert sha(baseline/e['name'])==e['sha256'].lower()
accepted=root/'spec/progress/evidence/LOOP1-CLIENT-STATE-001'
binding=json.loads((accepted/'source547514-native-binding.json').read_text())
assert binding['sha256']['H:/.codex/toolchains/client-gui/installed/im-client-storage.exe']==sha(baseline/'im-client-storage.exe')
run='desktop-accepted-base-compare-'+uuid.uuid4().hex;out=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens'/run;out.mkdir()
saved=private/run;saved.mkdir()
fixture=json.loads((private/'friends-fixture-ff1065c09806460890d4a8675f0e6b76.json').read_text())
candidate={e['name']:sha(target/e['name']) for e in original}
for name in candidate:shutil.copyfile(target/name,saved/name)
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'Diagnostic accepted-base comparison, not task acceptance','candidateFiles':candidate,'acceptedOriginalFiles':original,'acceptedProductSource':binding['productSource'],'bindingReferences':{str(accepted/n):sha(accepted/n) for n in ['source547514-native-binding.json','desktop-source547514-install.json','final-resource-baseline.json']},'fixture':fixture,'appearanceBaseline':'Existing exact warm14/.8 unchanged; no direct preferences writes','sourceQualification':'Coordinator independently verified entire clients/desktop547514→acceptedca527ca tree unchanged'}
def ps(script,*args,label):
 r=subprocess.run(['powershell','-NoProfile','-File',script,*args],cwd=root,capture_output=True)
 (out/(label+'-stdout-original.txt')).write_bytes(r.stdout);(out/(label+'-stderr-original.txt')).write_bytes(r.stderr)
 return r
def ui(action,name='',value='',label='observe'):
 r=ps('tests/clients/ui-ref/state/desktop_window.ps1','-Action',action,'-Name',name,'-Value',value,'-Output',str(out/(label+'.png')),label=label);assert r.returncode==0,r.stderr.decode(errors='replace')
try:
 assert ps('tests/clients/ui-ref/desktop_owned_stop.ps1',label='candidate-stop').returncode==0
 for e in original:shutil.copyfile(baseline/e['name'],target/e['name']);assert sha(target/e['name'])==e['sha256'].lower()
 assert ps('tests/clients/ui-ref/desktop_formal_start.ps1',label='accepted-default-start').returncode==0
 assert ps('tests/clients/ui-ref/desktop_accessibility.ps1',label='accepted-owned-accessibility').returncode==0
 ui('fill','Username',fixture['accounts'][0]['username'],'accepted-username');ui('fill','Password','fixture-password-not-a-real-secret','accepted-password');ui('click','Sign in',label='accepted-signin')
 ui('click','Friends',label='accepted-friends')
 for account in fixture['accounts'][1:4]:ui('reach',account['username'],label='accepted-exact-friend-'+account['userId'])
 ui('open-friend',fixture['accounts'][1]['username'],label='accepted-exact-conversation-open')
 ui('observe',label='accepted-connected-before-offline')
 ui('click','⚙ Settings',label='accepted-settings');ui('click','Go offline',label='accepted-disconnect');ui('click','Friends',label='accepted-offline-friends')
 for account in fixture['accounts'][1:4]:ui('reach',account['username'],label='accepted-offline-retained-'+account['userId'])
 ui('click','⚙ Settings',label='accepted-reconnect-settings');ui('click','Reconnect',label='accepted-reconnect');ui('click','Chat',label='accepted-reconnect-chat')
 probe=ps('tests/clients/ui-ref/desktop_idle_probe.ps1','-Output',str(out/'accepted-direct-idle-probe.json'),label='accepted-direct-idle-probe')
 receipt['actualIdleProbeExit']=probe.returncode
 ui('observe',label='accepted-after-probe');ui('click','Friends',label='accepted-reconnected-friends')
 for account in fixture['accounts'][1:4]:ui('reach',account['username'],label='accepted-reconnected-exact-'+account['userId'])
 receipt['exactThreeFriendsVisibleAfterReconnect']=True
finally:
 stopped=ps('tests/clients/ui-ref/desktop_owned_stop.ps1',label='accepted-finally-stop');assert stopped.returncode==0,'Cannot overwrite running owned baseline'
 for name,digest in candidate.items():assert sha(saved/name)==digest;shutil.copyfile(saved/name,target/name);assert sha(target/name)==digest
 receipt['candidateFilesRestored']=True;receipt['acceptedOwnedProcessStopped']=True
 receipt['endUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 receipt['entries']=[{'file':str(p.relative_to(out)),'sha256':sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
 (out/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('Bounded accepted-base comparison complete; candidate exact3files restored:',out)
