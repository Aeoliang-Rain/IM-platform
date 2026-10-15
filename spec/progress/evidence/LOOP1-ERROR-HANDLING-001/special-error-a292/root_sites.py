from pathlib import Path
import json
r=Path.cwd();e=Path(__file__).parent;j=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text('utf8'));own={x['path'] for x in json.loads((e/'root-selected.json').read_text('utf8'))}; rr=json.loads((e.parent/'regular-review-a292-recovery2/retained-grounds.json').read_text('utf8'));print(type(rr),rr.keys() if isinstance(rr,dict) else len(rr));
for i,s in enumerate(j['retained_sites'],1):
 if s['path'] in own:print(json.dumps({'ordinal':i,**s},ensure_ascii=False))
print('regular sample',str(rr)[:2000])
