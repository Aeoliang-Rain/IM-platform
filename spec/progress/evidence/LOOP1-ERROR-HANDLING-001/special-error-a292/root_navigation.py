from pathlib import Path
import json
E=Path(__file__).parent;own={x['path'] for x in json.loads((E/'root-selected.json').read_text('utf8'))}; rows=json.loads((E.parent/'regular-review-a292-recovery2/retained-grounds.json').read_text('utf8'))
for s in sorted([s for s in rows if s['path'] in own],key=lambda s:s['original_inventory_entry']): print(json.dumps(s,ensure_ascii=False))
