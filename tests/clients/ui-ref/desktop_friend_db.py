"""Read exact controlled-owner Repository identity/cursor; never credentials."""
from pathlib import Path
import sqlite3, json, sys, uuid
root=Path(__file__).resolve().parents[3];owner=str(uuid.UUID(sys.argv[1]))
fixtures=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001'
assert any(json.loads(p.read_text())['accounts'][0]['userId']==owner for p in fixtures.glob('friends-fixture-*.json')), 'Only task-owned controlled Friends owner'
db=sqlite3.connect('file:///C:/Users/21441/AppData/Roaming/im.platform.desktop/im-'+owner+'.sqlite?mode=ro',uri=True)
ids=[r[0] for r in db.execute("SELECT conversation_id FROM conversations UNION SELECT conversation_id FROM messages UNION SELECT subject_id FROM user_state WHERE kind IN ('conversation.changed','membership.changed') ORDER BY 1")]
print(json.dumps({'owner':owner,'conversationIds':ids,'userCursor':db.execute('SELECT cursor FROM user_cursor').fetchone()[0],'messageCount':db.execute('SELECT count(*) FROM messages').fetchone()[0],'userState':[{'kind':r[0],'subjectId':r[1],'revision':r[2]} for r in db.execute('SELECT kind,subject_id,revision FROM user_state ORDER BY kind,subject_id')],'method':'Readonly exact existing Repository conversationIds SQL UNION, controlled-owner only; no credential tables'}))
