from pathlib import Path
import json,collections
E=Path(__file__).parent; reg=json.loads((E.parent/'regular-review-a292-recovery2/retained-grounds.json').read_text('utf8')); print('regular',collections.Counter(s['token_class'] for s in reg)); rr={s['original_inventory_entry']:s for s in reg};cli=json.loads((E/'client/retained-map.json').read_text('utf8')); print('client',collections.Counter(s['token_class'] for s in cli));
for s in cli:
 r=rr[s['original_ordinal']]; actual=not r['token_class'].startswith('nonexecutable')
 if actual!=s['executable']:print('DIFF',json.dumps({'ordinal':s['original_ordinal'],'path':s['path'],'token':s['token'],'regular':r['token_class'],'special':s['token_class'],'source':s['source'],'specific_fault':s['specific_fault']},ensure_ascii=False))
