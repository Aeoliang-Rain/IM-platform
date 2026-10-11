"""Fresh installed process/default TLS after exact temporary trust rollback."""
from pathlib import Path
import os,datetime, hashlib, json, subprocess, time, ssl, urllib.request, uuid, socket

out=Path('spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/windows-week2-negative-'+str(uuid.uuid4()))
out.mkdir(parents=True,exist_ok=False)
exe='H:/.codex/toolchains/client-gui/installed/im-client-storage.exe'
assert hashlib.sha256(Path(exe).read_bytes()).hexdigest()==json.loads(Path('spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/source-build-binding.json').read_text())['artifacts']['desktopInstalled']['sha256']
ctx=ssl.create_default_context(cafile='C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime/tls-ui-ref/ca.pem')
with urllib.request.urlopen('https://localhost:8443/__infra/health',context=ctx,timeout=10) as r: assert r.status==200
command=r"""$p=@(Get-Process im-client-storage -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'H:\.codex\toolchains\client-gui\installed\im-client-storage.exe'});if($p.Count -gt 1){throw 'Unique owned process required'};$old=if($p.Count){$p[0].Id}else{0};$path='H:/.codex/toolchains/client-gui/installed/im-client-storage.exe';$all=@(Get-CimInstance Win32_Process);$family=@();if($old){$family=@($old);do{$found=@($all|Where-Object {$family -contains $_.ParentProcessId -and $family -notcontains $_.ProcessId}|ForEach-Object ProcessId);$family+=$found}while($found.Count);Stop-Process -Id $old};for($i=0;$i -lt 40;$i++){$remaining=@($family|Where-Object {Get-Process -Id $_ -ErrorAction SilentlyContinue});if(-not $remaining.Count){break};Start-Sleep -Milliseconds 200};if($remaining.Count){throw 'Old owned family did not exit'};$new=Start-Process -FilePath $path -WindowStyle Hidden -PassThru;@{oldPid=$old;oldOwnedProcessFamily=$family;oldFamilyExited=$true;newPid=$new.Id}|ConvertTo-Json"""
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',command],text=True,encoding='utf-8',timeout=10))
try:
    assert process['newPid']!=process['oldPid']
    access=subprocess.run(['powershell','-NoProfile','-File','tests/clients/ui-ref/desktop_accessibility.ps1'],capture_output=True,timeout=60)
    (out/'owned-accessibility-original.txt').write_bytes(access.stdout+access.stderr)
    assert access.returncode==0,'Fresh owned anonymous login controls must be exposed using standard MSAA'
    def ui(action,label,name='',value=''):
        subprocess.run(['powershell','-NoProfile','-File','tests/clients/ui-ref/state/desktop_window.ps1','-Action',action,'-Name',name,'-Value',value,'-TargetPid',str(process['newPid']),'-Output',str(out/(label+'.png'))],check=True,capture_output=True,timeout=45)
        return json.loads((out/(label+'.png.json')).read_text(encoding='utf-8'))
    for i in range(20):
        try:
            state=ui('observe','startup-'+str(i))
            if any(n['name']=='Resume saved session' for n in state['nodes']):break
        except subprocess.CalledProcessError:pass
        time.sleep(.3)
    else: raise RuntimeError('Actual fresh resume control not presented')
    fixture=json.loads(Path(os.environ.get('IM_STATE_FRESH_FIXTURE','C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime/fresh-public.json')).read_text(encoding='utf-8'))
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
    try:
        with socket.create_connection(('127.0.0.1',8443),timeout=10) as transport:
            with ctx.wrap_socket(transport,server_hostname='ui-ref.invalid'): raise AssertionError('Wrong hostname must be rejected')
    except ssl.SSLCertVerificationError as error:
        assert error.verify_code==62,'Must be actual hostname mismatch with explicit pinned CA'
        proof['explicitCAWrongHostnameRejected']=True
    trust=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/windows-trust/root-rollback.json');receipt=json.loads(trust.read_text());assert receipt['exactFullSetRestored'] and not receipt['ownedCertificatePresent'];proof['trustRollback']={'path':str(trust),'SHA256':hashlib.sha256(trust.read_bytes()).hexdigest()}
    proof['actualHEAD']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();proof['productSource']='1bd1a1bf015edd6422bd8bfeeb73bc454b565034'
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(proof['result'])
finally:
    cleanup=subprocess.run(['powershell','-NoProfile','-File','tests/clients/ui-ref/desktop_owned_stop.ps1'],capture_output=True,timeout=30)
    (out/'owned-finally-cleanup-original.txt').write_bytes(cleanup.stdout+cleanup.stderr)
    assert cleanup.returncode==0,'Exact owned fresh Windows fixture must exit even after test failure'
