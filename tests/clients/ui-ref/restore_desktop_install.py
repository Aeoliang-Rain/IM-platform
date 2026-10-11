"""Restore only verified owned three install files; never touch account data."""
from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
root=Path(__file__).resolve().parents[3];evidence=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
target=Path('H:/.codex/toolchains/client-gui/installed');original=private/'desktop-before'
assert target.resolve()==Path('H:/.codex/toolchains/client-gui/installed').resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
snapshot=json.loads((original/'original.json').read_text(encoding='utf-8-sig'))
assert {f['name'] for f in snapshot}=={'im-client-storage.exe','storage_probe.exe','uninstall.exe'}
acceptedCompare=evidence/'screens/desktop-accepted-base-compare-80be375d4fa3412f84d8040910f6333d/manifest.json'
candidate=json.loads(acceptedCompare.read_text())['candidateFiles']
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"$owned=@(Get-Process im-client-storage -ErrorAction SilentlyContinue | Where-Object Path -eq 'H:\\.codex\\toolchains\\client-gui\\installed\\im-client-storage.exe');$owned|ForEach-Object Id;exit 0"],text=True).strip(),'Owned install must be stopped before restore'
archive=private/'candidate-install-before-final-restore';archive.mkdir(exist_ok=False)
for item in snapshot:
 name=item['name'];assert sha(original/name)==item['sha256'].lower();assert sha(target/name)==candidate[name];shutil.copyfile(target/name,archive/name);assert sha(archive/name)==candidate[name]
for item in snapshot:
 name=item['name'];shutil.copyfile(original/name,target/name);assert sha(target/name)==item['sha256'].lower()
prefs=Path('C:/Users/21441/AppData/Roaming/im.platform.desktop/appearance.json');assert prefs.read_bytes()==b'["warm",14,0.8]'
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'originalSnapshot':{'path':str(original/'original.json'),'SHA256':sha(original/'original.json')},'beforeCandidate':candidate,'candidateArchive':str(archive),'restored':[{'file':str(target/f['name']),'SHA256':sha(target/f['name'])} for f in snapshot],'originalInstallRestoredExactly':True,'originalAppearance':{'file':str(prefs),'SHA256':sha(prefs),'bytes':'["warm",14,0.8]','exactBytesRestored':True},'dataOperation':'No AppData/preferences/credentials/account databases written or deleted; only previously owned three installer files restored.'}
out=evidence/'desktop-install-restored.json';assert not out.exists();out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('PASS exact original installed3files and preference bytes restored; candidate bytes archived')
