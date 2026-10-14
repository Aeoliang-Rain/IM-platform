from pathlib import Path
import json
E=Path(__file__).parent
for d in ['server','client']:
 print('SCOPE',d)
 for p in (E/d).glob('*.json'):print(p.name,p.stat().st_size)
for p in [E/'server/coverage.json',E/'client/coverage.json']:
 if p.exists():
  j=json.loads(p.read_text('utf8')); files=j.get('files',[]) if isinstance(j,dict) else j
  for s in files:print(json.dumps(s,ensure_ascii=False))
