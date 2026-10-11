"""Capture actual immutable source/build facts; never rewrite screenshot originals."""
from pathlib import Path
import hashlib,json,subprocess,datetime
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
SOURCE='1bd1a1bf015edd6422bd8bfeeb73bc454b565034'
assert not subprocess.check_output(['git','diff',SOURCE,'--','clients'],cwd=ROOT).strip()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
artifacts={}
for name,path in {'web':PRIVATE/'web-build','desktopInstalled':Path('H:/.codex/toolchains/client-gui/installed/im-client-storage.exe'),'desktopInstaller':Path('H:/.codex/toolchains/client-gui/target/x86_64-pc-windows-msvc/release/bundle/nsis/IM Plus_0.1.0_x64-setup.exe'),'androidAPK':ROOT/'clients/mobile/app/build/outputs/apk/debug/app-debug.apk','androidTestAPK':ROOT/'clients/mobile/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'}.items():
 assert path.exists()
 artifacts[name]=({'path':str(path),'sha256':digest(path)} if path.is_file() else {'path':str(path),'files':{str(p.relative_to(path)):digest(p) for p in sorted(path.rglob('*')) if p.is_file()}})
value={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCommit':SOURCE,'actualHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'actualStatus':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),'productDiffSinceSource':'empty','artifacts':artifacts,'fixture':json.loads((PRIVATE/'go-public.json').read_text()),'certificate':{'thumbprint':'727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C','derSHA256':digest(PRIVATE/'tls-ui-ref/ca.der'),'trust':'Windows Human manual machine/user-view lease; Android instrumented test-process-only explicit pinned CA'},'language':'Web zh/default; native English/default','acceptance':'independent review/CI/main sync pending'}
target=ROOT/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/source-build-binding.json';assert not target.exists();target.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
print('PASS actual frozen source/build bindings captured')
