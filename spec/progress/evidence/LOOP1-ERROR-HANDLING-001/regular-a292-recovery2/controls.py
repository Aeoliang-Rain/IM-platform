from pathlib import Path
import subprocess,os,sys,json,time,shutil,hashlib
E=Path(__file__).parent;R=Path.cwd();F=E/'fixture';PY=sys.executable
NODE='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';NPM='H:/node.js/npm.cmd'
paths=['clients/shared/protocol-sdk','clients/desktop/src','clients/desktop/package.json','clients/desktop/package-lock.json','clients/desktop/tsconfig.json','clients/web/src','clients/web/package.json','clients/web/package-lock.json','clients/web/tsconfig.json','tests/clients/send','tests/clients/sync','tests/clients/errors','tests/clients/web','tests/clients/gui','tests/clients/i18n','contracts/websocket','contracts/fixtures/websocket','tools/verify_client_send.py','tools/verify_client_sync.py']
proof=[]
for rel in paths:
 src=R/rel
 for p in src.rglob('*') if src.is_dir() else [src]:
  if not p.is_file() or any(z in p.parts for z in ['node_modules','dist','__pycache__']):continue
  q=F/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
  proof.append({'path':p.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'copy_sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
(E/'fixture-inputs.json').write_text(json.dumps(proof,indent=2),encoding='utf8');assert all(x['source_sha256']==x['copy_sha256'] for x in proof)
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8',npm_config_cache=str(E/'npm-cache'),WEB_BUILD_DIR=str(F/'web-build'))
env['PATH']=str(Path(PY).parent)+';'+str(Path(NODE).parent)+';H:/node.js;'+env['PATH']
hist=[]
def run(c,cwd=F):
 t=time.monotonic();p=subprocess.run(list(map(str,c)),cwd=cwd,env=env,capture_output=True);i=len(hist)
 (E/f'controls-{i:02}.stdout').write_bytes(p.stdout);(E/f'controls-{i:02}.stderr').write_bytes(p.stderr)
 hist.append({'argv':list(map(str,c)),'cwd':str(cwd),'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-t});(E/'controls-history.json').write_text(json.dumps(hist,indent=2),encoding='utf8')
 print(json.dumps(hist[-1]),flush=True);print(p.stdout.decode('utf8','replace')[-4000:]);print(p.stderr.decode('utf8','replace')[-2500:]);p.check_returncode()
for name in ['shared/protocol-sdk','desktop','web']:run([NPM,'--prefix',F/'clients'/name,'ci','--ignore-scripts','--no-audit','--no-fund'])
run([NODE,F/'clients/shared/protocol-sdk/node_modules/typescript/bin/tsc','-p',F/'clients/shared/protocol-sdk/tsconfig.json'])
for file in ['tests/clients/sync/shared.mjs','tests/clients/send/shared.mjs']:run([NODE,F/file])
run([NODE,F/'clients/desktop/node_modules/typescript/bin/tsc','-p',F/'clients/desktop/tsconfig.json'])
build=F/'clients/desktop/dist';(build/'package.json').write_text('{"type":"module"}',encoding='utf8');shutil.copytree(F/'clients/desktop/node_modules',build/'node_modules',dirs_exist_ok=True)
run([NODE,R/'tests/clients/errors/desktop_reads.mjs',build.as_uri()+'/'])
probe=Path('H:/.codex/toolchains/client-gui/target/debug/storage_probe.exe');actual=hashlib.sha256(probe.read_bytes()).hexdigest();expected=(R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read/probe-sha256.txt').read_text('utf8').strip();assert actual==expected,(actual,expected)
(E/'probe-binding.json').write_text(json.dumps({'path':str(probe),'sha256':actual,'expected':expected,'bound_unchanged_native_adapter':True}),encoding='utf8')
run([NODE,R/'tests/clients/errors/desktop_native_reads.mjs',build.as_uri()+'/',probe])
run([NPM,'--prefix',F/'clients/web','run','build'])
for file in ['tests/clients/web/behavior.mjs','tests/clients/web/appearance.mjs']:run([NODE,F/file])
print('PASS fresh locked exact-source shared/Web/Desktop strict/read/SQLx/stream controls; no installed GUI/Android acceptance claimed')
