from pathlib import Path
import shutil,hashlib,json,os,subprocess,time,sys
E=Path(__file__).parent;R=Path.cwd();F=E/'fixture'
proof=[]
for p in (R/'clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n').glob('*.kt'):
 q=F/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);assert p.read_bytes()==q.read_bytes();proof.append(dict(path=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(E/'web-retry-inputs.json').write_text(json.dumps(proof,indent=2))
env=os.environ.copy();env['WEB_BUILD_DIR']=str(F/'web-build')
node='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
h=[]
commands=[[node,str(F/'tests/clients/web/behavior.mjs')],[node,str(F/'tests/clients/web/appearance.mjs')],[sys.executable,'-Xutf8','-B','tools/build_language_packs.py','--verify']]
for i,c in enumerate(commands):
 t=time.monotonic();p=subprocess.run(c,cwd=F if i<2 else R,env=env,capture_output=True)
 (E/f'web-retry-{i}.stdout').write_bytes(p.stdout);(E/f'web-retry-{i}.stderr').write_bytes(p.stderr)
 h.append(dict(argv=c,cwd=str(F if i<2 else R),exit_code=p.returncode,elapsed_seconds=time.monotonic()-t));(E/'web-retry-history.json').write_text(json.dumps(h,indent=2))
 print(json.dumps(h[-1]),flush=True);print(p.stdout.decode('utf8','replace'));print(p.stderr.decode('utf8','replace'));p.check_returncode()
