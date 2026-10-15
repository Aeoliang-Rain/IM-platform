from pathlib import Path
import json
E=Path(__file__).parent
for f in ['root-assessment.json','client/report.json','client/sealed-receipt.json']:
 j=json.loads((E/f).read_text('utf8')); print('FILE',f);print(json.dumps(j,ensure_ascii=False,indent=2)[:22000])
for f in ['client/retained-map.json','client/protected-verification.json','client/coverage.json']:
 j=json.loads((E/f).read_text('utf8'));print('structure',f,type(j),list(j.keys()) if isinstance(j,dict) else len(j));print(str(j)[:3200])
