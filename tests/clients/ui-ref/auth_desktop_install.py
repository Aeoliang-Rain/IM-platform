"""Temporarily restore exact previously installed source1bd bytes; own 3 files only."""
from pathlib import Path
import subprocess,json,hashlib,shutil,sys,datetime,os
root=Path(__file__).resolve().parents[3];e=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'
old=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
private=Path(os.environ['IM_GUI_PRIVATE_RUNTIME']).parent/'desktop-install';target=Path('H:/.codex/toolchains/client-gui/installed')
prefs=Path('C:/Users/21441/AppData/Roaming/im.platform.desktop/appearance.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
candidate=json.loads((e/'screens/desktop-accepted-base-compare-80be375d4fa3412f84d8040910f6333d/manifest.json').read_text())['candidateFiles']
original=json.loads((old/'desktop-before/original.json').read_text(encoding='utf-8-sig'))
assert set(candidate)=={f['name'] for f in original}=={'im-client-storage.exe','storage_probe.exe','uninstall.exe'}
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process im-client-storage -ErrorAction SilentlyContinue | Where-Object Path -eq 'H:\\.codex\\toolchains\\client-gui\\installed\\im-client-storage.exe' | Select-Object -ExpandProperty Id; exit 0"],text=True).strip()
if sys.argv[1]=='install':
 assert not private.exists();private.mkdir()
 assert prefs.read_bytes()==b'["warm",14,0.8]';shutil.copyfile(prefs,private/'appearance-original.json')
 for f in original:
  name=f['name'];assert sha(target/name)==f['sha256'].lower();assert sha(old/'candidate-install-before-final-restore'/name)==candidate[name]
  shutil.copyfile(target/name,private/name);assert sha(private/name)==f['sha256'].lower()
 for name in candidate:shutil.copyfile(old/'candidate-install-before-final-restore'/name,target/name);assert sha(target/name)==candidate[name]
 result={'originalFiles':original,'candidateFiles':candidate,'originalAppearanceSHA256':sha(private/'appearance-original.json'),'installedCurrentSource1bd':True,'identityQualification':'Exact archive of previously source1bd NSIS-installed identity and3files, matching accepted-base compare manifest candidateFiles. No installer rebuilt or fake new installation claim.'}
else:
 for f in original:
  name=f['name'];assert sha(private/name)==f['sha256'].lower();assert sha(target/name)==candidate[name]
 for f in original:
  shutil.copyfile(private/f['name'],target/f['name']);assert sha(target/f['name'])==f['sha256'].lower()
 shutil.copyfile(private/'appearance-original.json',prefs);assert prefs.read_bytes()==b'["warm",14,0.8]'
 result={'originalFiles':original,'originalInstallRestoredExactly':True,'originalAppearanceRestoredExactly':True}
out=e/('auth-fix-desktop-'+sys.argv[1]+'.json');assert not out.exists();out.write_text(json.dumps({'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'privateOwnedBackup':str(private),'result':'PASS','dataQualification':'Only exact three owned install files and owned appearance preference; no database/userdata or credentials read/copied/deleted',**result},indent=2)+'\n',encoding='utf-8')
print('PASS exact auth-fix desktop '+sys.argv[1])
