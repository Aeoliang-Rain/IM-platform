import pathlib,json,hashlib,subprocess
r=pathlib.Path.cwd();ext=pathlib.Path(__file__).parent;root=ext.parent.parent
mapping=json.loads((ext/'retained-map.json').read_text(encoding='utf-8'))
for v in mapping:
 if v['path'].startswith('clients/shared/'):
  ls=(r/v['path']).read_text(encoding='utf-8').splitlines();line=ls[v['line']-1];id=v['id'];start=v['original_column']-1
  if id in ['RH236','RH237','RH240','RH241','RH242','RH247']:
   v.update(token=line[start:start+2] if line[start:start+2]=='?:' else '?',token_class='regex_syntax',executable=False,disposition='NON_EXECUTABLE_RECORD',specific_fault='No runtime fault: exact regex quantifier/noncapturing-group token; original lexical record preserved.',actual_recovery_or_failure='Regex syntax only, not a caught-error fallback or compatibility path.')
  elif id=='RH244':v.update(token='if',column=line.index('if')+1)
  elif id in ['RH238','RH243','RH248']:v.update(token='??',column=line.index('??')+1)
  else:
   positions=[i for i in range(len(line)) if line.startswith('catch',i)];v.update(token='catch',column=min(positions,key=lambda x:abs(x-start))+1)
  assert line[v['column']-1:].startswith(v['token']),(id,v['column'],v['token'])
(ext/'retained-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
nd=root/'regular-review-a292-recovery2/native';seal=json.loads((nd/'sealed-receipt.json').read_text(encoding='utf-8'));checks=[]
for name,expected in seal['files_sha256'].items():
 p=nd/name;actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==expected,name;checks.append(dict(path=str(p),sha256=actual))
qa=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read/negative-control-qa.json').read_text(encoding='utf-8'));src=r/'clients/mobile/app/src/androidTest/kotlin/im/platform/client/sync/ContiguousReadChecks.kt';actual=hashlib.sha256(src.read_bytes()).hexdigest();assert actual==qa['current_source_sha256'];text=src.read_text(encoding='utf-8');assert 'repo.contiguous(conversation); null' in text
apk=root/'fix-cause-read/owned-final-android-build-artifacts/clients_mobile_app_build/outputs/apk/androidTest/debug/app-debug-androidTest.apk';assert hashlib.sha256(apk.read_bytes()).hexdigest()==qa['current_test_apk_sha256']
run=root/'fix-cause-read/research/runs/R-ERROR-CAUSE-READ-FIX';events=[json.loads(x) for x in (run/'events.jsonl').read_text(encoding='utf-8').splitlines()];bound=[]
for command in ['C-aae68e51-bd47-4d1f-9f0a-51fa62fe2a2a','C-c2dcfa92-07fa-4cd4-9c83-1e265280abf4']:
 e=next(e for e in events if e['event_type']=='command_finished' and e['data']['command_id']==command);d=e['data'];assert d['exit_code']==0
 for kind in ['stdout','stderr']:assert hashlib.sha256((run/d[kind+'_blob']).read_bytes()).hexdigest()==d[kind+'_sha256']
 bound.append(d)
(ext/'prior-native-binding.json').write_text(json.dumps(dict(seal_entries=checks,qa_source=str(src),qa_sha256=actual,apk=str(apk),apk_sha256=qa['current_test_apk_sha256'],prior_commands=bound,limit='Prior actual Fix Android run, NOT specialist device execution. Final corrected18 only; initial3 assertion QA unreliable. Rust inspected source/native registration/lock families and prior bounded evidence only, no new Rust/native installation/device/TLS runtime.'),indent=2),encoding='utf-8')
print('PASS239 exactcoordinates; executable',sum(v['executable'] for v in mapping),'nonexecutable',sum(not v['executable'] for v in mapping),'prior native seal',len(checks),'QA source/APK/2actualpriorcommands outputhashes verified')
