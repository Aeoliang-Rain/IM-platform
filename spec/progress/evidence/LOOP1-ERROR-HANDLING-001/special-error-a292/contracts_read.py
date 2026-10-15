from pathlib import Path
import json
R=Path.cwd()
for d in ['contracts/errors','contracts/http','contracts/websocket','contracts/database']:
 for p in (R/d).glob('*'):
  if p.is_file():print(p.relative_to(R),p.stat().st_size)
for p in (R/'contracts/errors').glob('*'):
 if p.is_file():print('FILE',p.relative_to(R));print(p.read_text('utf8'))
for rel in ['contracts/websocket/message-v1.schema.json','contracts/websocket/sync-v1.schema.json']:
 p=R/rel
 if p.exists():print('FILE',rel);print(p.read_text('utf8'))
