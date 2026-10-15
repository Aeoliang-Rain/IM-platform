from pathlib import Path
import json,hashlib,subprocess
R=Path.cwd();E=Path(__file__).parent;SHA='a292f516f622651ae62595163e479c13fff78c1d'
J=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/verification-history.json').read_text('utf-8-sig'));d=Path(J['external_research_run'])
rows=[]
prior=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/regular-review-b5ea135/backend/prior-live-inspection.json').read_text('utf-8-sig'))
for c in J['commands']:
 if 'go_live.py' not in str(c.get('argv')):continue
 assert c['exit_code']==0
 blobs=[]
 saved=next(x for x in prior if x['command_id']==c['command_id'])
 for which in ['stdout','stderr']:
  p=d/c[which+'_blob'];actual=hashlib.sha256(p.read_bytes()).hexdigest()
  expected=next(x['stored_sha256'] for x in saved['blobs'] if x['path']==str(p))
  assert actual==expected
  blobs.append({'which':which,'actual_stored_sha256':actual,'expected_prior_sealed_stored_sha256':expected,'recorded_raw_sha256':c[which+'_sha256'],'equal_raw_hash':actual==c[which+'_sha256'],'redaction_declared':c['secret_redaction_applied'],'unredacted_raw_output_available':actual==c[which+'_sha256']})
 raw=(d/c['stdout_blob']).read_text('utf8');lines=raw.splitlines()
 rows.append({'command':c,'stored_blobs':blobs,'observed_skips':[s for s in lines if 'SKIP' in s],'disposition':[s for s in lines if 'DEFERRED_BY_HUMAN' in s],'pass_lines':[s for s in lines if 'PASS' in s][-8:],'fresh_runtime':False})
changed=subprocess.check_output(['git','diff','--name-only','7700645',SHA,'--','backend','tests/clients/errors/go_live.py']).decode().splitlines();assert not changed
script=(R/'tests/clients/errors/go_live.py').read_text('utf8');assert 'DB_TEST_ENABLE' in script
(E/'prior-go-live-binding.json').write_text(json.dumps({'observed_prior_commands':rows,'server_source_range':'7700645..'+SHA,'server_source_changed':changed,'current_runner_sha256':hashlib.sha256((R/'tests/clients/errors/go_live.py').read_bytes()).hexdigest(),'qualification':'Prior controlled disposable PG/NATS evidence exact recorded blob hashes verified; unchanged server source since initialcandidate7700645. Not freshly rerun; ordinary fresh Go tests independently run in server helper with explicit live SKIPs. DEFERRED friend403 remains notPASS.'},indent=2),encoding='utf8')
print('PASS prior stored/redacted liveGo output hashes/current unchangedserver binding; rawredacted stdout unavailable; observedprior',len(rows),'commands, no fresh PG/NATS claim')
