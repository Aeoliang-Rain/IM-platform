"""Read only owned fixture database, preserving exact original bytes privately."""
from pathlib import Path
import subprocess, sqlite3, json, hashlib
root=Path(__file__).resolve().parents[3]
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
fixture=json.loads((private/'go-public.json').read_text())
out=private/'matrix-diagnosis-620676b5';out.mkdir(exist_ok=False)
name='im-'+fixture['accounts'][0]['userId']+'.sqlite'
originals=[]
for suffix in ['', '-wal', '-shm']:
 r=subprocess.run(['H:/Android/platform-tools/adb.exe','-s','emulator-5590','exec-out','run-as','im.platform.client','cat','databases/'+name+suffix],capture_output=True)
 if r.returncode==0:
  (out/(name+suffix)).write_bytes(r.stdout);originals.append({'file':name+suffix,'sha256':hashlib.sha256(r.stdout).hexdigest()})
 else: originals.append({'file':name+suffix,'exit':r.returncode,'error':r.stderr.decode(errors='replace')})
db=sqlite3.connect((out/name).as_uri()+'?mode=ro',uri=True)
rows=db.execute("SELECT conversation_id,request_id,sender_id,content,state,server_message_id FROM messages WHERE content=?",('GUI Android actual send 1791705899429',)).fetchall()
conversations=db.execute('SELECT DISTINCT conversation_id FROM messages').fetchall();db.close()
receipt={'mode':'read-only original device files; private copy SQLite readonly','accountId':fixture['accounts'][0]['userId'],'expectedMorganConversation':fixture['conversationId'],'rows':rows,'conversations':conversations,'originals':originals}
target=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/android-matrix-diagnosis-620676b5.json'
target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
