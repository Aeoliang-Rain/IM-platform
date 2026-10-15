from pathlib import Path
import json,sys
r=Path.cwd();p=r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json';j=json.loads(p.read_text('utf8')); print(type(j));print(j.keys() if isinstance(j,dict) else len(j));
if isinstance(j,dict):
 for k,v in j.items(): print(k,type(v),len(v) if isinstance(v,(list,dict)) else v, str(v)[:1600])
