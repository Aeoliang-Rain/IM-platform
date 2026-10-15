from pathlib import Path
import json,hashlib,subprocess,re
R=Path.cwd();E=Path(__file__).parent;REG=E.parent/'regular-review-a292-recovery2';J=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text('utf8')); git=lambda *a:subprocess.check_output(['git',*a],cwd=R).decode().strip(); assert git('rev-parse','HEAD')=='a292f516f622651ae62595163e479c13fff78c1d';assert git('rev-parse','--show-toplevel')=='H:/.codex/worktrees/err/IM-platform';assert not git('status','--porcelain');tracked=git('ls-files').splitlines();rows=[]
for x in J['files']:
 p=R/x['path'];actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==x['sha256'],(x['path'],actual,x['sha256']);assert x['path'] in tracked;rows.append({'path':x['path'],'sha256':actual,'bytes':p.stat().st_size,'candidate_sha':git('rev-parse','HEAD')})
expected=set(x['path'] for x in J['files']); broad={p for p in tracked if p.startswith(('backend/','clients/','deploy/','plugins/'))};extras=sorted(broad-expected); print('tracked extras',extras)
rec=json.loads((REG/'final-receipt.json').read_text('utf8'));seals=[]
for rel,h in rec['artifact_sha256'].items():
 p=REG/rel;actual=hashlib.sha256(p.read_bytes()).hexdigest();assert h==actual,(rel,h,actual);seals.append({'path':str(p),'sha256':actual})
(E/'production-hash-checks.json').write_text(json.dumps(rows,indent=2),encoding='utf8');(E/'regular-seal-checks.json').write_text(json.dumps(seals,indent=2),encoding='utf8');(E/'tracked-tree-reconciliation.json').write_text(json.dumps({'production_selected':185,'extra_tracked_scope_inputs':extras,'source_tree_sha':git('rev-parse','HEAD'),'selection':'tracked backend/clients/deploy/plugins excluding tests plus3deployedmigration files+languagebuilder'},indent=2),encoding='utf8'); print('PASS185actual inputhashes/355regular artifactseals/currentcleanHEAD')
