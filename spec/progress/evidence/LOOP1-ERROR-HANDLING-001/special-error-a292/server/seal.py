from pathlib import Path
import hashlib,json,subprocess
O=Path(__file__).parent;R=Path.cwd()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
commands=[];runs=[]
for rid in ['R-ERROR-SPECIAL-SERVER-A292','R-ERROR-SPECIAL-SERVER-A292-SUPPLEMENT2']:
 D=O/'research/runs'/rid;events=[json.loads(l) for l in (D/'events.jsonl').read_text().splitlines()];starts={e['data']['command_id']:e['data'] for e in events if e['event_type']=='command_started'}
 for e in events:
  if e['event_type']=='command_finished':
   c={**starts[e['data']['command_id']],**e['data'],'run_id':rid}
   c['stdout_stored_sha256']=sha(D/c['stdout_blob']);c['stderr_stored_sha256']=sha(D/c['stderr_blob'])
   c['skipped_case_lines']=[s for s in (D/c['stdout_blob']).read_text().splitlines() if '--- SKIP:' in s]
   commands.append(c)
 runs.append({'run_id':rid,'event_count':len(events),'finished':events[-1]['event_type']=='run_finished','summary_sha256':sha(D/'summary.json'),'events_sha256':sha(D/'events.jsonl'),'complete_prospective_trace':False})
(O/'command-history.json').write_text(json.dumps(commands,indent=2)+'\n')
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();status=subprocess.check_output(['git','status','--porcelain'],text=True).strip();assert head=='a292f516f622651ae62595163e479c13fff78c1d' and not status
files={}
for p in O.rglob('*'):
 if not p.is_file() or p.name=='final-receipt.json' or any(s in ['go-cache','go-tmp','java-classes'] for s in p.relative_to(O).parts):continue
 files[str(p.relative_to(O)).replace('\\','/')]=sha(p)
receipt={'actor':'/root/error_audit_a292/server_special','role':'fresh specialized audit helper, not implementation/fix/regular','result':'PASS_SERVER_SCOPE_NO_FINDINGS','candidate':head,'baseline':'35bd6f5f1091503f95a0282f730ed04233b0b6ea','branch':'task/LOOP1-ERROR-HANDLING-001','git_root':'H:/.codex/worktrees/err/IM-platform','final_git_status':status,'coverage_inputs':36,'original305_records_mapped':25,'five_specialized_classes_inspected':True,'recorders':runs,'artifact_sha256':files,'limits':['Every fresh DB-dependentSKIP unexecuted, notPASS; prior actualPG/NATS historicalstoredhash verified only.','Prior stdout storedredactedSHA c7ade5 differs recordedraw27354; unredactedraw unavailable.','Java sixcontrols actualcompiledhandle withSocketadapter not deployment/TLS proof.','Both owntraces incompleteprestart/directreads; structural validation only.','Finalreceipt assembly direct afterfinish. Initial rejected supplementalrun emptydirectory retained, no rewritten rawtrace.','No fulltask/Gate/CI/main synchronization acceptance.'],'mutations':'External evidence/cache/classes only; repository/git/main/device/CI untouched'}
(O/'final-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('SEALED',len(files),'artifacts;receiptsha256',sha(O/'final-receipt.json'),'candidate',head,'clean',not status)
