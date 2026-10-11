"""Candidate-scoped copies of accepted STATE scenarios; original harness/evidence stays immutable.

Only environment, evidence destination and truthful source labels change. Assertions,
fault timing, PostgreSQL/SQLite witnesses and actual UI operations are preserved.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--source',required=True);a=p.parse_args()
runtime=Path(a.runtime).resolve();source=a.source
assert subprocess.check_output(['git','rev-parse',source+'^{commit}'],cwd=ROOT,text=True).strip()==source
assert not subprocess.check_output(['git','diff',source,'--','clients'],cwd=ROOT,text=True).strip(),'Freeze actual client source before adapting formal runs'
output=ROOT/'tests/clients/ui-ref/state';output.mkdir(parents=True,exist_ok=True)
files=['web_actual.mjs','desktop_actual.mjs','android_actual.mjs','android_restart.mjs','android_fresh.mjs','desktop_fresh.mjs','fresh_web.mjs','friends_actual.mjs','prepare_desktop.mjs','fresh_fixture.py','backend_verify.py','fault_proxy.py','desktop_window.ps1','desktop_notification.ps1','desktop_shortcut.ps1','desktop_tray.ps1','desktop_toast_capture.ps1']
entries=[]
for name in files:
 original=ROOT/'tests/clients/state'/name;text=original.read_text(encoding='utf-8')
 text=text.replace('H:/IM-platform/.git/worktrees/IM-platform43/state-runtime',runtime.as_posix())
 text=text.replace('go-35588/public.json','go-public.json')
 text=text.replace('tests/clients/state/','tests/clients/ui-ref/state/')
 text=text.replace('LOOP1-CLIENT-STATE-001','LOOP1-CLIENT-UI-REF-001')
 text=text.replace("ROOT=Path(__file__).resolve().parents[3]","ROOT=Path(__file__).resolve().parents[4]")
 text=text.replace("root=Path(__file__).resolve().parents[3]","root=Path(__file__).resolve().parents[4]")
 text=text.replace('im-gui-product-20261004-35588',"'+json.loads((runtime/'go-public.json').read_text())['project']+'") if False else text
 if name in ('fresh_fixture.py','backend_verify.py'):
  text=text.replace("'im-gui-product-20261004-35588'","json.loads((Path("+repr(runtime.as_posix())+")/'go-public.json').read_text())['project']")
 if name=='fault_proxy.py':text=text.replace("TLS=PRIVATE/'tls-state-week2'","TLS=PRIVATE/'tls-ui-ref'")
 text=text.replace("runtime/'tls-state-week2/ca.pem'","runtime/'tls-ui-ref/ca.pem'")
 # All instrumented live phases use the pinned explicit test CA, never system-root mutation.
 if name.endswith('.mjs'):
  text=text.replace("'shell','am','instrument','-w'","'shell','am','instrument','-w','-e','uiRefCA','/sdcard/Android/data/im.platform.client/files/ui-ref-ca.der'")
 text=text.replace('default SDK TLS','explicit pinned test CA + default hostname verification').replace('defaultSDK','explicitTestCA').replace('defaultSDKTLS','explicitTestCATLS')
 text=text.replace('preliminary dirty source, exact candidate rerun pending','actual new candidate source '+source)
 text=text.replace('dirty candidate preliminary; no accepted SHA claim','actual candidate source '+source+'; independent acceptance pending')
 text=text.replace('new controlled Fix B exact installed source547514 product','new controlled UIREF installed product source '+source)
 text=text.replace('547514f6c8c8c0c40e27073b67d17bb3f224b6c5',source)
 target=output/name
 assert not target.exists(),'Never overwrite an adapted run harness; use a new iteration'
 target.write_text(text,encoding='utf-8',newline='\n')
 entries.append({'original':str(original.relative_to(ROOT)),'originalSHA256':hashlib.sha256(original.read_bytes()).hexdigest(),'adapted':str(target.relative_to(ROOT)),'adaptedSHA256':hashlib.sha256(target.read_bytes()).hexdigest()})
manifest={'source':source,'runtime':runtime.as_posix(),'changes':'Environment paths/new evidence destination/new source labels; Android instrumented process explicit pinned CA; assertions/faults/witnesses retained','entries':entries}
(ROOT/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/state-harness-adaptation.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('PASS new source-scoped STATE harness generated; original evidence unchanged')
