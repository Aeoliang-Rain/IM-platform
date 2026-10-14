from pathlib import Path
import json,hashlib,subprocess,re
R=Path.cwd();E=Path(__file__).parent
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
# Fresh integrity checking of durable prerequisite facts does not reuse any candidate verdict.
prior=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/regular-review-b5ea135/prerequisite-seals.json').read_text('utf-8-sig'))
checks=[{'path':z['path'],'expected':z['sha256'],'actual':h(Path(z['path'])),'pass':h(Path(z['path']))==z['sha256']} for z in prior]
save('prerequisite-seals.json',checks);assert all(z['pass'] for z in checks)
fix=E.parent/'fix-cause-read';receipt=json.loads((fix/'final-receipt.json').read_text('utf-8-sig'))
assert receipt['candidate_sha']=='a292f516f622651ae62595163e479c13fff78c1d' and receipt['git_status']=='' and receipt['source_lease']=='RELEASED'
seals=[]
for group,where in [('artifact_sha256',fix),('source_evidence_sha256',R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read')]:
 for p,expected in receipt[group].items():seals.append({'path':str(where/p),'actual':h(where/p),'expected':expected,'pass':h(where/p)==expected})
save('fix-final-seal-checks.json',seals);assert all(z['pass'] for z in seals)
auth=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read/authority-inputs.json').read_text('utf-8-sig'))
authchecks=[{'path':z['path'],'actual':h(R/z['path']),'expected':z['sha256'],'pass':h(R/z['path'])==z['sha256']} for z in auth]
save('authority-input-checks.json',authchecks);assert all(z['pass'] for z in authchecks)

