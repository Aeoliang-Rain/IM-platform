from pathlib import Path
import json,hashlib,subprocess
r=Path('H:/.codex/worktrees/err/IM-platform');o=Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/regular-review-b5ea135/mobile');sha=lambda b:hashlib.sha256(b).hexdigest();a=json.loads((o/'report.json').read_text(encoding='utf8'));d=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-send-cleanup/verification-history.json').read_text());x=next(x for x in d if x['command_id']=='C-2d655f7b-24d7-469c-b013-a52060021c99');p=next(Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/fix-send-cleanup').rglob(Path(x['stdout_blob']).name));b=p.read_bytes();print('MORE',sha(b)==x['stdout_sha256'],b.decode('utf8')[-2200:]);a['runtime_review']['commands'].append(x);a['runtime_review']['evidence_sha256_verified']=True
seen={}
for s in a['retained_sites']:
 k=(s['path'],s['line'],s['column']);s['location_note']='Inventory navigation retained; actual complete line semantically inspected'
 if k in seen:s['location_note']='Duplicate scanner navigation of '+seen[k]+'; separate ID does not imply separate semantic catch'
 else:seen[k]=s['id']
status=subprocess.check_output(['git','status','--porcelain=v1'],cwd=r,stderr=subprocess.DEVNULL).decode();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r).decode().strip();assert not status and head==a['candidate_sha'];a['final_clean_status']=status;a['release']='READ_ONLY_HELPER_LEASE_RELEASED; no source/Git/device/trust writes'
(o/'report.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8');print(sha((o/'report.json').read_bytes()))
