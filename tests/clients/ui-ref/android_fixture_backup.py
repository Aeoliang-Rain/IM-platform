"""Fail closed on unknown account databases before native baseline's owned app reset."""
from pathlib import Path
import subprocess,json,re,hashlib,datetime,sys
root=Path(__file__).resolve().parents[3];private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime');adb='H:/Android/platform-tools/adb.exe'
def call(*args):return subprocess.check_output([adb,'-s','emulator-5590',*args])
proofs={}
def visit(value,path):
 if isinstance(value,dict):
  if isinstance(value.get('userId'),str) and (str(value.get('username','')).startswith(('gui_','state_')) or str(value.get('displayName','')).startswith(('GUI Fixture','STATE '))):
   proofs.setdefault(value['userId'],[]).append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'username':value.get('username'),'displayName':value.get('displayName')})
  for child in value.values():visit(child,path)
 elif isinstance(value,list):
  for child in value:visit(child,path)
for directory in [root/'spec/progress/evidence/LOOP1-CLIENT-GUI-001',root/'spec/progress/evidence/LOOP1-CLIENT-STATE-001',root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001']:
 for path in directory.rglob('*.json'):
  try:visit(json.loads(path.read_text(encoding='utf-8-sig')),path)
  except (ValueError,UnicodeError):pass
for path in private.glob('*public*.json'):
 visit(json.loads(path.read_text(encoding='utf-8')),path)
files=call('shell','run-as','im.platform.client','ls','databases').decode().splitlines()
ids=sorted({re.fullmatch(r'im-([0-9a-f-]{36})\.sqlite(?:-journal|-wal|-shm)?',name).group(1) for name in files if re.fullmatch(r'im-([0-9a-f-]{36})\.sqlite(?:-journal|-wal|-shm)?',name)})
unknown=[identity for identity in ids if identity not in proofs];unknownFiles=[name for name in files if not re.fullmatch(r'im-([0-9a-f-]{36})\.sqlite(?:-journal|-wal|-shm)?',name)]
if '--inspect-only' in sys.argv:
 print(json.dumps({'method':'Readonly ownership inventory only; no process stop/data write/reset','accountCount':len(ids),'unknownAccounts':unknown,'unknownDatabaseFiles':unknownFiles},indent=2));sys.exit(0)
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':'im.platform.client','serial':'emulator-5590','databaseAccounts':{identity:proofs.get(identity,[]) for identity in ids},'unknownAccounts':unknown,'unknownDatabaseFiles':unknownFiles,'qualification':'Accepted historical and current disposable GUI/STATE fixture identities only; no database content/credential output; reset is separate required baseline scenario, never current live-scenario repair'}
target=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/android-fixture-ownership-before-baseline.json';assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
assert not unknown and not unknownFiles,('Unknown data preserved; app reset forbidden',unknown,unknownFiles)
subprocess.run([adb,'-s','emulator-5590','shell','am','force-stop','im.platform.client'],check=True,capture_output=True)
out=private/'owned-app-before-native-baseline.tar';assert not out.exists()
out.write_bytes(call('exec-out','run-as','im.platform.client','tar','-cf','-','databases','shared_prefs','files'))
receipt['privateArchive']={'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size};receipt['allOwnershipProven']=True
backup=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/android-fixture-private-backup.json';assert not backup.exists();backup.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('PASS owned fixture-only account ownership and private application backup; no app reset performed by this command')
