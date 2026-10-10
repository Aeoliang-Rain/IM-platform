"""Fresh installed process/default TLS after exact temporary trust rollback."""
from pathlib import Path
import datetime, hashlib, json, subprocess, time, ssl, urllib.request, uuid

out=Path('spec/progress/evidence/LOOP1-CLIENT-STATE-001/screens/windows-week2-negative-'+str(uuid.uuid4()))
out.mkdir(parents=True,exist_ok=False)
exe='H:/.codex/toolchains/client-gui/installed/im-client-storage.exe'
assert hashlib.sha256(Path(exe).read_bytes()).hexdigest()=='18f8b5bb6f8a8c1a6ec8777421a5440c60fabf03a4f8dea0f24deb48ed870503'
ctx=ssl.create_default_context(cafile='H:/IM-platform/.git/worktrees/IM-platform43/state-runtime/tls-state-week2/ca.pem')
with urllib.request.urlopen('https://localhost:8443/__infra/health',context=ctx,timeout=10) as r: assert r.status==200
command=r"""$p=@(Get-Process im-client-storage -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'});if($p.Count -gt 1){throw 'Unique owned process required'};$old=if($p.Count){$p[0].Id}else{0};$path='H:/.codex/toolchains/client-gui/installed/im-client-storage.exe';$all=@(Get-CimInstance Win32_Process);$family=@();if($old){$family=@($old);do{$found=@($all|Where-Object {$family -contains $_.ParentProcessId -and $family -notcontains $_.ProcessId}|ForEach-Object ProcessId);$family+=$found}while($found.Count);Stop-Process -Id $old};for($i=0;$i -lt 40;$i++){$remaining=@($family|Where-Object {Get-Process -Id $_ -ErrorAction SilentlyContinue});if(-not $remaining.Count){break};Start-Sleep -Milliseconds 200};if($remaining.Count){throw 'Old owned family did not exit'};$new=Start-Process -FilePath $path -WindowStyle Hidden -PassThru;@{oldPid=$old;oldOwnedProcessFamily=$family;oldFamilyExited=$true;newPid=$new.Id}|ConvertTo-Json"""
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',command],text=True,encoding='utf-8',timeout=10))
assert process['newPid']!=process['oldPid']
def ui(action,label,name='',value=''):
    subprocess.run(['powershell','-NoProfile','-File','tests/clients/state/desktop_window.ps1','-Action',action,'-Name',name,'-Value',value,'-TargetPid',str(process['newPid']),'-Output',str(out/(label+'.png'))],check=True,capture_output=True,timeout=12)
    return json.loads((out/(label+'.png.json')).read_text(encoding='utf-8'))
for i in range(20):
    try:
        state=ui('observe','startup-'+str(i))
        if any(n['name']=='Resume saved session' for n in state['nodes']):break
    except subprocess.CalledProcessError:pass
    time.sleep(.3)
else: raise RuntimeError('Actual fresh resume control not presented')
fixture=json.loads(Path('H:/IM-platform/.git/worktrees/IM-platform43/state-runtime/fresh-public.json').read_text(encoding='utf-8'))
ui('fill','username','Username',fixture['accounts'][0]['username'])
ui('fill','password','Password','fixture-password-not-a-real-secret')
ui('click','login','Sign in')
for i in range(25):
    state=ui('observe','negative-'+str(i))
    if any(n['name']=='Connection unavailable' for n in state['nodes']):break
    time.sleep(.3)
else: raise RuntimeError('Actual fresh default TLS request did not fail')
assert not any(n['name']=='Online' for n in state['nodes'])
with urllib.request.urlopen('https://localhost:8443/__infra/health',context=ctx,timeout=10) as r: assert r.status==200
proof={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'process':process,'installedSHA256':hashlib.sha256(Path(exe).read_bytes()).hexdigest(),'liveStrictCAFileHealth':200,'actualDefaultNativeRequest':'Sign in via default reqwest HTTPS transport','actualUIError':'Connection unavailable','onlineAbsent':True,'result':'PASS fresh actual installed Windows process rejects same live temporary chain after trust rollback; no AppData directly edited by harness'}
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(proof['result'])
