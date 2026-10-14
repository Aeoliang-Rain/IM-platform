import pathlib,json,hashlib
repo=pathlib.Path.cwd();root=pathlib.Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/fix-cause-read');j=json.loads((root/'final-receipt.json').read_text());q=json.loads((root/'negative-control-qa.json').read_text());run=root/'research/runs/R-ERROR-CAUSE-READ-FIX'
checks=[]
for key,folder in [('artifact_sha256',root),('source_evidence_sha256',repo/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read')]:
 for k,v in j[key].items():
  p=folder/k;assert p.exists();assert hashlib.sha256(p.read_bytes()).hexdigest()==v;checks.append(str(p))
assert j['sha']=='a292f516f622651ae62595163e479c13fff78c1d';p=repo/'clients/mobile/app/src/androidTest/kotlin/im/platform/client/sync/ContiguousReadChecks.kt';assert hashlib.sha256(p.read_bytes()).hexdigest()==q['current_source_sha256'];print('SOURCE QA currenthash',q['current_source_sha256']);print(p.read_text())
events=[json.loads(x)for x in (run/'events.jsonl').read_text().splitlines()]; print('eventkeys',events[0].keys());print('LASTEVENT',events[-1])
for e in events:
 d=e.get('data',{})
 if 'native.py' in str(d.get('argv',[])) or d.get('command_id')==q['actual_final_command_id']:print(e)
for p in root.rglob('*.apk'):
 h=hashlib.sha256(p.read_bytes()).hexdigest();print('APK',str(p),h,'finalQA match',h==q['current_test_apk_sha256'])
for h in json.loads((root/'verification-history.json').read_text()):
 if any('native.py' in x for x in h['argv']):
  print('PRIORLOCAL',h['argv'],h.get('exit_code',h.get('exit')),h.get('duration_ms'))
  if 'stdout_blob' in h:
   for stream in ['stdout','stderr']:
    p=run/h[stream+'_blob'];assert hashlib.sha256(p.read_bytes()).hexdigest()==h[stream+'_sha256'];print(p.read_text(encoding='utf-8')[-1800:])
print('SEALED',len(checks),'LIMIT priorfix runtime evidence; no fresh execution')
pathlib.Path(__file__).with_name('prior-runtime-binding.json').write_text(json.dumps({'sha':j['sha'],'seals_verified':checks,'qa':q,'classification':'prior Fix execution evidence, freshly read/hash checked; not this reviewer runtime'},indent=2))
