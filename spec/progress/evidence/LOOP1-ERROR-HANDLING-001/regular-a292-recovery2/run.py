from pathlib import Path
import subprocess,os,sys,json,time
E=Path(__file__).parent; R=Path('H:/.codex/worktrees/err/IM-platform')
PY='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8',GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.excludesFile',GIT_CONFIG_VALUE_0='.git/info/exclude')
env['PATH']=str(Path(PY).parent)+';C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin;'+env['PATH']
a=sys.argv[1:]; t=time.monotonic(); p=subprocess.run([PY,'-Xutf8','-B',str(R/'tools/research/recorder.py'),'run-command','--research-root',str(E/'research'),'--run-id','R-ERROR-REGULAR-A292-RECOVERY2','--',*a],cwd=R,env=env,capture_output=True)
n=len(list(E.glob('command-*.json')))+1
(E/f'command-{n:03}.stdout.txt').write_bytes(p.stdout);(E/f'command-{n:03}.stderr.txt').write_bytes(p.stderr)
(E/f'command-{n:03}.json').write_text(json.dumps({'argv':a,'cwd':str(R),'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-t},indent=2),encoding='utf8')
sys.stdout.buffer.write(p.stdout);sys.stderr.buffer.write(p.stderr);sys.exit(p.returncode)
