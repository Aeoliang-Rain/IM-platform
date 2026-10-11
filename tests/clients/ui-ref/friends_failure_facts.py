"""Readonly public relationship/cursor/no-chat linkage after the retained formal failure."""
from pathlib import Path
import json, sqlite3, subprocess, ssl, urllib.request, hashlib, datetime
root=Path(__file__).resolve().parents[3];private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
out=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/friends-8c44b6a2-1cc4-4874-835d-c47c0555a825'
fixture=json.loads((private/'friends-fixture-ff1065c09806460890d4a8675f0e6b76.json').read_text());owner=fixture['accounts'][0]['userId']
sql=f"SELECT coalesce(json_agg(json_build_object('userLow',user_low_id,'userHigh',user_high_id,'directConversationId',direct_conversation_id)),'[]'::json) FROM friendships WHERE user_low_id='{owner}' OR user_high_id='{owner}'"
def query(sql):return json.loads(subprocess.check_output(['C:/Program Files/Docker/Docker/resources/bin/docker.exe','exec',fixture['project']+'-postgres-1','psql','-U','im','-d','im','-Atc',sql],text=True))
rows=query(sql);assert len(rows)==3
for account in fixture['accounts'][1:4]:assert sum(account['userId'] in [r['userLow'],r['userHigh']] for r in rows)==1
conn=sqlite3.connect('file:///C:/Users/21441/AppData/Roaming/im.platform.desktop/im-'+owner+'.sqlite?mode=ro',uri=True);conn.row_factory=sqlite3.Row
stored=[dict(r) for r in conn.execute("SELECT conversation_id FROM conversations UNION SELECT conversation_id FROM messages UNION SELECT subject_id FROM user_state WHERE kind IN ('conversation.changed','membership.changed') ORDER BY 1")];cursor=[dict(r) for r in conn.execute('SELECT cursor FROM user_cursor')]
assert {r['directConversationId'] for r in rows}=={r['conversation_id'] for r in stored}
before=json.loads((out/'messages-before.json').read_text());after=query("SELECT json_build_object('messages',(SELECT count(*) FROM messages),'outbox',(SELECT count(*) FROM outbox_events),'messageOutbox',(SELECT count(*) FROM outbox_events WHERE event_type='message.created'))")
assert after['messages']==before['messages'] and after['messageOutbox']==before['messageOutbox']
with urllib.request.urlopen('https://localhost:8443/__state/events',context=ssl.create_default_context(cafile=str(private/'tls-ui-ref/ca.pem')),timeout=15) as r:events=json.load(r)
boundary=json.loads((out/'initial-sync-complete-event-boundary.json').read_text())['lastEvent'];post=events[boundary:];assert not any(e.get('kind') in ['actual_created','send','actual_ack'] for e in post)
inputs=['desktop-offline-state.png.json','desktop-reconnect-chat-header.png.json','direct-idle-probe.json','readonly-sync-diagnosis.json','initial-sync-complete-event-boundary.json']
receipt={'actualUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qualification':'Readonly post-failure facts. Three origin changes/projection and offline retained→Connected are proven; fourth change/offline-other-platform recovery/account isolation are still unfinished. Reconnect Sync idle FAIL remains FAIL. No complete Friends acceptance claim.','fixture':fixture,'actualGoRelationships':rows,'desktopRepositoryConversations':stored,'desktopRepositoryUserCursor':cursor,'messagesBefore':before,'messagesAfter':after,'newMessageDeliveryEvents':0,'eventBoundary':boundary,'ownerSyncRequests':[e for e in post if e.get('kind')=='sync_request' and e.get('userId')==owner],'inputHashes':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in inputs}}
target=out/'readonly-friend-convergence-facts.json';assert not target.exists();target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('PASS readonly exact3 relationships/Repository conversations/cursor/no-chat linkage; unfinished fullchain',target)
