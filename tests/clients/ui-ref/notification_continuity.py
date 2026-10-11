"""Bound unchanged native responsibility to the previously approved original OS card."""
from pathlib import Path
import subprocess,hashlib,json,datetime,re
root=Path(__file__).resolve().parents[3];old='cc13ba1284e3c11a44203377b3ac7adb3d0e25d6';base='ca527ca889e6b88d39ce2f9e8e2ae599aa2d7be5';product='1bd1a1bf015edd6422bd8bfeeb73bc454b565034'
def blob(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=root)
def sha(data):return hashlib.sha256(data).hexdigest()
paths=['clients/desktop/src/application/ui/native.ts','clients/desktop/src-tauri/src/desktop_capabilities.rs','clients/desktop/src-tauri/tauri.conf.json','clients/desktop/src-tauri/Cargo.toml','clients/desktop/src-tauri/Cargo.lock']
checks=[]
for path in paths:
 values={ref:sha(blob(ref,path)) for ref in [old,base,product,'HEAD']};assert len(set(values.values()))==1
 checks.append({'path':path,'SHA256BySource':values,'gitBlobBySource':{ref:subprocess.check_output(['git','rev-parse',ref+':'+path],cwd=root,text=True).strip() for ref in values}})
path='clients/desktop/src/application/ui/workspace.ts'
methods={ref:re.search(r'async testNotification\(\)\{.*?\}\}',blob(ref,path).decode()).group() for ref in [old,base,product,'HEAD']};assert len(set(methods.values()))==1
raw=root/'spec/progress/evidence/LOOP1-CLIENT-GUI-001/win20261008/raw/native-notification-candidate-1.png';assert sha(raw.read_bytes())=='85ca0a51ad84ba852a6d9150244e685f2b49f6af78fd803dd70a94f9271f4535'
report=root/'spec/progress/evidence/LOOP1-CLIENT-GUI-001/win20261008/architect/addon-report.md'
value={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'nativeChecks':checks,'unchangedTestNotificationMethod':methods,'callbackTrace':'Shell app.testNotification.bind(app) -> SettingsPanel direct testNotification -> ProfilePanel onClick run(testNotification()) -> unchanged workspace method -> unchanged native notify -> unchanged native capability','oldActualOSCard':{'file':str(raw.relative_to(root)),'sha256':sha(raw.read_bytes()),'originalSource':old,'originalReviewCandidate':'79ec62c73b6681b4a544869051722a85521b9b4e','originalInstalledPackageSHA256':'6707f9d5d5b1c1d2fc195b5c9ef91f11fa86b195e20f83b0dc046864ae9f8b8c','approvedReport':str(report.relative_to(root)),'approvedReportSHA256':sha(report.read_bytes())},'currentActualRuntime':'desktop-matrix-7591a6ad811443f3b30baabffdbeccfd manifest and native Test notification own History5->6; actual shortcut/tray actions own PID','qualification':'Old accepted raw is cited unchanged, never relabeled new. Current overlay and notification-center capture attempts FAILED; no newly visible OS card claimed. History increment is delivery evidence only. Native unchanged responsibility continuity requires fresh independent Architect judgment.'}
target=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/notification-continuity.json';assert not target.exists();target.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');print('PASS exact native source/blob and accepted original card hash continuity; fresh Architect acceptance pending')
