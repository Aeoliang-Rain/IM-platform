from pathlib import Path
import subprocess,os,json,time,sys
E=Path(__file__).parent;R=Path.cwd();F=E/'fixture';NODE='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
env=os.environ.copy();env['WEB_BUILD_DIR']=str(F/'web-build');env['PYTHONDONTWRITEBYTECODE']='1';env['PATH']=str(Path(NODE).parent)+';'+env['PATH']
hist=[]
for file in ['tests/clients/web/behavior.mjs','tests/clients/web/appearance.mjs']:
 c=[NODE,str(R/file)];t=time.monotonic();p=subprocess.run(c,cwd=R,env=env,capture_output=True);i=len(hist)
 (E/f'web-retry-{i}.stdout').write_bytes(p.stdout);(E/f'web-retry-{i}.stderr').write_bytes(p.stderr);hist.append({'argv':c,'cwd':str(R),'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-t,'reason':'Original source test resolves existing Android dictionary input absent from external runtime fixture; no test/source/contract changes.'});(E/'web-retry-history.json').write_text(json.dumps(hist,indent=2),encoding='utf8')
 print(json.dumps(hist[-1]),flush=True);print(p.stdout.decode('utf8','replace'));print(p.stderr.decode('utf8','replace'));p.check_returncode()
