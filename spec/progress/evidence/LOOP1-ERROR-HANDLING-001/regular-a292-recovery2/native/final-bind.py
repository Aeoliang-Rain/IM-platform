import pathlib,json,hashlib,subprocess
out=pathlib.Path(__file__).parent;repo=pathlib.Path.cwd();fixroot=pathlib.Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/fix-cause-read');run=fixroot/'research/runs/R-ERROR-CAUSE-READ-FIX';ev=[json.loads(l)for l in (run/'events.jsonl').read_text().splitlines()];bindings=[]
for cid in ['C-aae68e51-bd47-4d1f-9f0a-51fa62fe2a2a','C-c2dcfa92-07fa-4cd4-9c83-1e265280abf4']:
 start=next(x['data']for x in ev if x['event_type']=='command_started'and x['data']['command_id']==cid);end=next(x['data']for x in ev if x['event_type']=='command_finished'and x['data']['command_id']==cid)
 for s in ['stdout','stderr']:assert hashlib.sha256((run/end[s+'_blob']).read_bytes()).hexdigest()==end[s+'_sha256']
 output=(run/end['stdout_blob']).read_text();assert 'INSTRUMENTATION_RESULT: sdkInt=34'in output and 'INSTRUMENTATION_CODE: -1'in output and 'INSTRUMENTATION_RESULT: result=PASS'in output
 expected=['assertions=69','readAssertions=33','contiguousReadAssertions=18']if'mobile'in start['argv']and'send-mobile'not in start['argv']else['assertions=66','sendReadAssertions=21'];assert all(x in output for x in expected);bindings.append({'start':start,'finish':end,'observed':expected})
q=json.loads((fixroot/'negative-control-qa.json').read_text());assert hashlib.sha256((repo/'clients/mobile/app/src/androidTest/kotlin/im/platform/client/sync/ContiguousReadChecks.kt').read_bytes()).hexdigest()==q['current_source_sha256'];assert hashlib.sha256((fixroot/'owned-final-android-build-artifacts/clients_mobile_app_build/outputs/apk/androidTest/debug/app-debug-androidTest.apk').read_bytes()).hexdigest()==q['current_test_apk_sha256']
protected=json.loads((repo/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read/protected-read-scope.json').read_text());nativeproof=[]
for x in protected['proof']:
 if not x['path'].startswith(('clients/desktop/','clients/mobile/')):continue
 b=(repo/x['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==x['candidate_sha256'];old=subprocess.check_output(['git','show',protected['against_baseline']+':'+x['path']]);old=old.replace(b'\r\n',b'\n');now=b.replace(b'\r\n',b'\n')
 if x['byte_equal_baseline']:assert old==now
 else:
  start=now.index(b'    fun contiguous(');end=now.index(b'    fun conversationIds()',start);oldstart=old.index(b'    fun contiguous(');oldend=old.index(b'    fun conversationIds()',oldstart);assert now[:start]+now[end:]==old[:oldstart]+old[oldend:]
 nativeproof.append(x['path'])
result={'sha':'a292f516f622651ae62595163e479c13fff78c1d','native_protected_checked':nativeproof,'priorFix_commands':bindings,'current_QA_source_sha256':q['current_source_sha256'],'current_final_test_apk_sha256':q['current_test_apk_sha256'],'limits':'Previous actual Fix runtime independently read/hash bound; not this reviewer execution. Send preserved testAPK later replaced by Sync builds, command/output hashes establish prior66+21 execution, not a newAPK source attestation. Initial3malformedchecks unreliable; only correctedfinal18 accepted as supporting evidence. Broad Rust/native prior evidence not freshly rerun.'}
(out/'runtime-scope-binding-final.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

