from pathlib import Path
import subprocess,os,json,time,sys
E=Path(__file__).parent;R=Path.cwd();PY=sys.executable
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PATH']=str(Path(PY).parent)+';'+env['PATH'];env['GOCACHE']=str(E/'go-cache')
commands=[[PY,'-Xutf8','-B','tools/verify_frozen_architecture.py'],[PY,'-Xutf8','-B','ci/check_architecture.py','--scope','all','--json'],[PY,'-Xutf8','-B','ci/check_s2_planning.py'],[PY,'-Xutf8','-B','-m','unittest','discover','-s','tests/architecture','-v'],['C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development'],['C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance']]
hist=[]
for i,c in enumerate(commands):
 t=time.monotonic();p=subprocess.run(c,cwd=R,env=env,capture_output=True);(E/f'baseline-{i}.stdout').write_bytes(p.stdout);(E/f'baseline-{i}.stderr').write_bytes(p.stderr)
 hist.append({'argv':c,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-t});(E/'baseline-history.json').write_text(json.dumps(hist,indent=2),encoding='utf8')
 print(json.dumps(hist[-1]),flush=True);print(p.stdout.decode('utf8','replace')[-3000:]);print(p.stderr.decode('utf8','replace')[-2000:]);
 if p.returncode:sys.exit(p.returncode)
