from pathlib import Path
import json
E=Path(__file__).parent.parent; R=Path.cwd()
for p in [E/'regular-review-a292-recovery2/final-receipt.json',E/'regular-review-a292-recovery2/controls.py',E/'regular-review-a292-recovery2/web_retry.py',R/'spec/architecture/decisions/ADR-0011-web-appearance-storage.md',R/'spec/architecture/decisions/ADR-0012-client-supplement-planning.md']:
 print('FILE',p)
 if p.suffix=='.json':
  j=json.loads(p.read_text('utf8'));print([(k,type(v).__name__,len(v) if isinstance(v,(list,dict)) else v) for k,v in j.items() if k!='commands']); print('artifactsample',j.get('artifacts',j.get('evidence_seals',[]))[:1])
 else:print(p.read_text('utf8'))
