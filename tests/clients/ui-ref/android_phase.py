"""Run original authenticated instrumented phases; qualify explicit test-process CA."""
from pathlib import Path
import subprocess,sys,json,uuid,hashlib,datetime,os
ROOT=Path(__file__).resolve().parents[3];private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime');fixture=json.loads((private/'go-public.json').read_text());adb='H:/Android/platform-tools/adb.exe'
phase=sys.argv[1];run='ui-ref-'+uuid.uuid4().hex;out=ROOT/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens'/('android-'+phase+'-'+run);out.mkdir()
def binding():
 return json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {actualBinding} from './tests/clients/ui-ref/state/android_binding.mjs'; console.log(JSON.stringify(await actualBinding()))"],cwd=ROOT,env=os.environ.copy(),text=True))
before=binding();(out/'source-install-binding-before.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
args=[adb,'-s','emulator-5590','shell','am','instrument','-w','-e','uiRefCA','/sdcard/Android/data/im.platform.client/files/ui-ref-ca.der','-e','expectedConversation',fixture['conversationId'],'-e','phase',phase,'-e','stateRun',run,'-e','avery',fixture['accounts'][0]['username'],'-e','averyId',fixture['accounts'][0]['userId'],'-e','riley',fixture['accounts'][2]['username'],'im.platform.client.test/im.platform.client.ui.GuiAuthenticatedInstrumentation']
r=subprocess.run(args,capture_output=True,timeout=240);(out/'instrumentation-original.txt').write_bytes(r.stdout+r.stderr)
subprocess.run([adb,'-s','emulator-5590','pull','/sdcard/Android/data/im.platform.client/files/gui-auth/'+run,str(out/'native-originals')],check=True,capture_output=True)
raw=(r.stdout+r.stderr).decode('utf-8',errors='replace');print(raw)
after=binding();(out/'source-install-binding-after.json').write_text(json.dumps(after,indent=2)+'\n',encoding='utf-8')
entries=[{'file':str(p.relative_to(out)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
(out/'manifest.json').write_text(json.dumps({'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,'actualHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'actualStatus':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),'productSource':'1bd1a1bf015edd6422bd8bfeeb73bc454b565034','androidBindingBefore':before,'androidBindingAfter':after,'fixture':fixture,'TLSQualification':'Pinned explicit test-process CA for HTTPS and WSS; default endpoint hostname verification; empty process-only Provider cache marker restored finally; no device/system roots changed','entries':entries},indent=2)+'\n',encoding='utf-8')
assert r.returncode==0 and 'INSTRUMENTATION_RESULT: result=PASS' in raw and 'actualDefaultSocketTLSHostnamePositive=PASS' in raw and 'defaultHostnameMismatch=PASS' in raw
print('PASS actual Android authenticated '+phase+' phase + explicit TLS positive/hostname negative')
