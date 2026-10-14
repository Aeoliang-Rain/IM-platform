from pathlib import Path
import json
E=Path(__file__).parent
for f in ['server/coverage.json','server/retained-grounds.json','server/prior-live-verified.json','client/protected-checks.json']:
 p=E/f
 if not p.exists(): print('PENDING',f);continue
 j=json.loads(p.read_text('utf8'));print('FILE',f)
 if f.endswith('coverage.json'):print('\n'.join(str(x) for x in j))
 else: print(json.dumps(j,ensure_ascii=False,indent=2))
