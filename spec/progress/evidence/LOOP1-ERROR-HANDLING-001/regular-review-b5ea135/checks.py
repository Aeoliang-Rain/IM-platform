from pathlib import Path
import os,subprocess,json,time,hashlib,sys
R=Path('H:/.codex/worktrees/err/IM-platform');E=Path(__file__).parent
os.environ['PYTHONDONTWRITEBYTECODE']='1';os.environ['PYTHONIOENCODING']='utf-8'
D=Path('C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies')
os.environ['PATH']=str(D/'node/bin')+os.pathsep+str(D/'python')+os.pathsep+os.environ['PATH']
history=[]
def run(a):
 t=time.monotonic();p=subprocess.run(list(map(str,a)),cwd=R,capture_output=True,text=True,encoding='utf8',errors='replace');history.append(dict(argv=list(map(str,a)),exit=p.returncode,duration_ms=round((time.monotonic()-t)*1000),stdout=p.stdout,stderr=p.stderr));(E/'checks.json').write_text(json.dumps(history,indent=2),'utf8');print(p.stdout,p.stderr);return p.returncode
P=sys.executable
for a in [[P,'-Xutf8','-B','tools/verify_frozen_architecture.py'],[P,'-Xutf8','-B','ci/check_architecture.py','--scope','all','--json'],[P,'-Xutf8','-B','ci/check_s2_planning.py'],[P,'-Xutf8','-B','-m','unittest','discover','-s','tests/architecture'],[D/'native/powershell/pwsh.exe','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance']]:
 assert run(a)==0
NODE=D/'node/bin/node.exe';T=E.parent/'fix-send-cleanup/owned-build-artifacts/clients_shared_protocol-sdk_node_modules/typescript/lib/tsc.js'
assert run([NODE,T,'--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--skipLibCheck','--rootDir',R/'clients','--outDir',E/'compiled',R/'clients/shared/protocol-sdk/src/sync/http.ts',R/'clients/web/src/application/http.ts'])==0
(E/'compiled/package.json').write_text('{"type":"module"}','utf8')
assert run([NODE,E/'cycle-repro.mjs'])==0
