from pathlib import Path
import json,hashlib,subprocess
R=Path.cwd();O=Path(__file__).parent
H=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/verification-history.json').read_text('utf-8-sig'))
d=Path(H['external_research_run']);rows=[]
for c in H['commands']:
 if 'go_live.py' not in str(c.get('argv')):continue
 assert c['exit_code']==0
 hashes={}
 for which,expected in [('stdout','c7ade5f6cb98bfd398a9f88c51efef5124ef68b4ca5ca24ff13796dffeff785e'),('stderr','e5685ace54caf40f634e3e3d39371d7e9a84ccd1d0dd3009641265a334b732b1')]:
  p=d/c[which+'_blob'];actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==expected
  hashes[which]={'path':str(p),'actual_stored_sha256':actual,'recorded_raw_sha256':c[which+'_sha256'],'stored_matches_recorded_raw':actual==c[which+'_sha256']}
 lines=(d/c['stdout_blob']).read_text().splitlines()
 rows.append({'command':c,'verified_stored_hashes':hashes,'observed_skip_lines':[l for l in lines if 'SKIP' in l],'deferred_human_lines':[l for l in lines if 'DEFERRED_BY_HUMAN' in l],'observed_summary':[l for l in lines if 'PASS actual disposable' in l or 'Owned integration' in l],'fresh_runtime':False})
assert len(rows)==1
assert not subprocess.check_output(['git','diff','--name-only','7700645..HEAD','--','backend','deploy','contracts/database','tests/clients/errors/go_live.py']).strip()
(O/'prior-live-verified.json').write_text(json.dumps({'candidate':'a292f516f622651ae62595163e479c13fff78c1d','rows':rows,'independently_verified':'Stored prior redacted output hashes and no server/runner/deploy/schema delta since770 verified. Prior live test result is historical corroboration only; no new PG/NATS execution claimed. Unredacted raw stdout is unavailable.'},indent=2)+'\n')
print('PASS prior stored outputs exact hashes; source/build/config/runner unchanged since770; not fresh runtime')
