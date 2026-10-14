import pathlib,json,hashlib,subprocess
r=pathlib.Path('H:/.codex/worktrees/err/IM-platform'); e=pathlib.Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c')
p=e/'regular-review-a292-recovery2/final-receipt.json'
print('receipt hash',hashlib.sha256(p.read_bytes()).hexdigest()); print(p.read_text(encoding='utf-8'))
a=r/'spec/architecture/frozen-architecture.md'; print('canonical hash',hashlib.sha256(a.read_bytes()).hexdigest()); t=a.read_text(encoding='utf-8'); sections=t.split('<a id="section-')
for s in sections:
 n=s.split('"')[0]
 if n.split('-')[0] in ['2','3','5','6','7','10','11','12','13','14','18','21']: print('<a id="section-'+s)
print('evidence files'); print('\n'.join(str(p.relative_to(r)) for p in (r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001').glob('*')))
print('external regular files'); print('\n'.join(str(p.relative_to(e)) for p in (e/'regular-review-a292-recovery2').glob('*')))
