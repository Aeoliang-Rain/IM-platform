"""Readonly actual Sync events/cursors after retained Friends failure."""
from pathlib import Path
import json, urllib.request, ssl, sqlite3, sys, datetime
root=Path(__file__).resolve().parents[3]
private=Path('C:/Users/21441/.codex/visualizations/2026/10/11/01a129aa-d2ed-7350-8f8d-efb0ecc85664/ui-ref-runtime')
out=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens'/sys.argv[1]
fixture=json.loads((private/sys.argv[2]).read_text())
ctx=ssl.create_default_context(cafile=str(private/'tls-ui-ref/ca.pem'))
with urllib.request.urlopen('https://localhost:8443/__state/events',context=ctx,timeout=15) as response: events=json.load(response)
owner=fixture['accounts'][0]['userId']
conn=sqlite3.connect('file:///C:/Users/21441/AppData/Roaming/im.platform.desktop/im-'+owner+'.sqlite?mode=ro',uri=True)
conn.row_factory=sqlite3.Row
tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
data={t:[dict(r) for r in conn.execute('SELECT * FROM "'+t+'"')] for t in tables if 'cursor' in t or 'conversation' in t}
target=out/'readonly-sync-diagnosis.json';assert not target.exists()
target.write_text(json.dumps({'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner':owner,'events':[e for e in events if e.get('userId')==owner][-120:],'tables':data,'qualification':'Readonly post-failure observation; no fixture, transport or product-state mutation'},indent=2)+'\n',encoding='utf-8')
print('Readonly evidence',target)
