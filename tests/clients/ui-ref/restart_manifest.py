"""Post-capture inventory supplement; retain original bytes and original binding facts."""
from pathlib import Path
import json,hashlib,datetime,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/screens/android-restart-4ae543f4-48a7-4b7b-bfef-d165faafa5b3'
binding=json.loads((out/'source-install-binding-before.json').read_text());proof=json.loads((out/'proofs.json').read_text());raw=(out/'resume-original.txt').read_text()
assert 'INSTRUMENTATION_RESULT: result=PASS' in raw and proof['terminated'] and proof['pidBefore']!=proof['pidAfter']
assert proof['before']['messages']==0 and proof['before']['outbox']==0 and proof['after']['messages']==1 and proof['after']['outbox']==1
for artifact in binding['artifacts'].values():assert hashlib.sha256(Path(artifact['archive']).read_bytes()).hexdigest()==artifact['sha256']
entries=[]
for path in sorted(out.rglob('*')):
 if path.is_file():
  entry={'file':str(path.relative_to(out)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
  if path.suffix=='.png':
   side=path.with_suffix('.json');assert side.exists();entry['actualCapturedState']=json.loads(side.read_text());entry.update({'serial':'emulator-5590','avd':'IMClientSend34','API':34,'language':'English/default'})
  entries.append(entry)
manifest={'task_id':'LOOP1-CLIENT-UI-REF-001','kind':'Post-capture hash/state/source inventory of completed real Android process stop/newPID/resume/original-ID retry','assembledUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assemblyHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'captureOriginalBinding':binding,'captureTimeQualification':'Original binding actualUTC is pre-run observation; precise per-PNG capture UTC unavailable. This supplement was assembled afterward and does not claim contemporaneous manifest creation. Original sidecars, raw results, process IDs and bytes retained.','fixture':json.loads((root/'spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/source-build-binding.json').read_text())['fixture'],'runtimeQualification':'Real owned Go/PostgreSQL/NATS/proxy; approved Windows fixture CA lease active; Android explicit pinned test-process CA with hostname checks, no Android root changes','proof':proof,'entries':entries,'result':'PASS local only; independent review/acceptance pending'}
target=out/'manifest.json';assert not target.exists();target.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print('PASS post-capture restart original inventory: '+str(sum(e['file'].endswith('.png') for e in entries))+' actual PNGs, exact original source/install binding and process/storage witnesses')
