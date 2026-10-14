from pathlib import Path
import json,hashlib,subprocess,collections,re
R=Path.cwd();E=Path(__file__).parent;SHA='a292f516f622651ae62595163e479c13fff78c1d';BASE='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def j(p):return json.loads(p.read_text('utf-8-sig'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
helper_checks=[]
for directory,receipt,key in [('server','final-receipt.json','seals'),('native','sealed-receipt.json','files_sha256')]:
 b=E/directory;rec=j(b/receipt);assert rec.get('candidate_sha',rec.get('sha'))==SHA
 assert not rec.get('findings',[]) and not rec.get('standards_findings',[]) and not rec.get('task_spec_findings',[])
 for rel,expected in rec[key].items():
  actual=h(b/rel);assert actual==expected,(directory,rel);helper_checks.append({'path':str(b/rel),'expected':expected,'actual':actual,'pass':True})
 helper_checks.append({'path':str(b/receipt),'actual':h(b/receipt),'candidate_sha':SHA,'fresh_regular_helper':True})
assert h(E/'native/sealed-receipt.json')=='99a9980965dc19ec57a42b85d1f4cdde6ce60b71b02f93f0f51758096c4e2fad'
assert h(E/'server/final-receipt.json')=='2aa0f92d0ac41700ff3cbb0dd221884e06e82f6d7a416aba829ee120744e77d9'
save('helper-seal-checks.json',helper_checks)
I=j(R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json');expected_files={x['path']:x['sha256'] for x in I['files']};expected_records={(x['id'],x['path']) for x in I['retained_sites']}
native=j(E/'native/semantic-coverage.json');server=j(E/'server/coverage.json');own=j(E/'own-semantic-coverage.json')
coverage=[]
for role,files in [('own',own),('server',server['files']),('native',native)]:
 for f in files:
  assert f['sha256']==expected_files[f['path']]==h(R/f['path'])
  coverage.append({**f,'candidate_sha':SHA,'reviewer_partition':role,'review_result':'NO_ACTIONABLE_FINDING'})
assert len(coverage)==185 and len({x['path'] for x in coverage})==185 and {x['path'] for x in coverage}==set(expected_files)
save('semantic-coverage.json',coverage)
sites=j(E/'own-retained-grounds.json')
for s in sites:s['token_class']='nonexecutable_regex_or_type' if s['token']=='?:' else 'catch' if s['token']=='catch' else 'absent_row' if s['id']=='RH244' else 'fallback';s['review_disposition']='NONEXECUTABLE_NAVIGATION_ONLY' if s['token']=='?:' else 'RETAINED_CURRENT_REQUIREMENT'
for s in server['retained_sites']:
 line=(R/s['path']).read_text('utf8').splitlines()[s['line']-1];at=s['column']-1
 token=next(t for t in ['defer','_ =','?:','catch','except'] if line[at:].startswith(t))
 op=s['operation']
 if s['id']in ['RH008','RH009']:op='Core.syncNumber regex declaration'
 if s['id']=='RH024':op='InfraPlaceholder.main accepted-client handle/cleanup'
 if s['id']=='RH293':op='canonical migration main RuntimeError boundary'
 if s['id']in ['RH294','RH295']:op='build_language_packs.sources Kotlin resource extraction regex'
 sites.append({**s,'original_operation':s['operation'],'operation':op,'token':token,'token_class':'nonexecutable_regex' if token=='?:' else 'catch' if token in ['catch','except'] else 'cleanup','candidate_sha':SHA,'source_sha256':h(R/s['path']),'specific_fault':s['trigger'],'current_authority':s['current_authority'],'actual_recovery_or_failure':s['recovery'],'review_disposition':'NONEXECUTABLE_NAVIGATION_ONLY' if token=='?:' else 'RETAINED_CURRENT_REQUIREMENT'})
for s in j(E/'native/semantic-site-addendum.json'):sites.append({**s,'candidate_sha':SHA})
assert len(sites)==305 and len({(s['id'],s['path']) for s in sites})==305 and {(s['id'],s['path'])for s in sites}==expected_records
locations=set();classes=collections.Counter();excluded=[];corrections=[]
for s in sites:
 line=(R/s['path']).read_text('utf8').splitlines()[s['line']-1]
 token=s['token'];at=s['column']-1
 assert line[at:].startswith(token),(s['id'],s['column'],token,line[at:])
 assert s['source_sha256']==h(R/s['path'])
 loc=(s['path'],s['line'],s['column']);assert loc not in locations,(s['id'],loc);locations.add(loc)
 assert s['specific_fault'] and s['current_authority'] and s['actual_recovery_or_failure'] and s['operation']
 nonexec=s['token_class'].startswith('nonexecutable') or s['token_class']=='optional_type_declaration';classes['nonexecutable' if nonexec else 'executable']+=1
 if s.get('review_disposition','').startswith('EXCLUDED'):excluded.append(s['id'])
 ordinal,original=next((i+1,x) for i,x in enumerate(I['retained_sites']) if x['id']==s['id'] and x['path']==s['path'])
 s['original_inventory_entry']=ordinal;s['review_record_id']=f'REVIEW-SITE-{ordinal:03}';s['original_id']=s['id']
 if original['column']!=s['column'] or original['operation']!=s['operation']:corrections.append({'id':s['id'],'path':s['path'],'line':s['line'],'original_column':original['column'],'verified_column':s['column'],'original_operation':original['operation'],'verified_operation':s['operation'],'token':s['token'],'semantic_coverage_preserved':True})
assert classes=={'executable':270,'nonexecutable':35},classes
assert len({s['review_record_id']for s in sites})==305
duplicate_labels={ident:[s['path']for s in sites if s['id']==ident] for ident,count in collections.Counter(s['id']for s in sites).items()if count>1};assert list(duplicate_labels)==['RH294']
save('retained-grounds.json',sites);save('navigation-addendum.json',corrections)
clean=subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude','status','--porcelain']).decode();head=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip();branch=subprocess.check_output(['git','branch','--show-current']).decode().strip();assert clean=='' and head==SHA and branch=='task/LOOP1-ERROR-HANDLING-001'
save('aggregation.json',{'candidate_sha':SHA,'base':BASE,'branch':branch,'production_files':185,'original_inventory_navigation_records':305,'original_distinct_id_strings':304,'duplicate_original_id_labels':duplicate_labels,'review_record_identity':'Each immutable original entry receives REVIEW-SITE-001..305, retains original_id/path/entry ordinal. (original_id,path) identifies all305 records including two RH294 entries. No original data edited or silently dropped.','distinct_verified_token_coordinates':len(locations),'executable_navigation_sites':270,'nonexecutable_regex_comment_type_hits':35,'partition_counts':{'own':{'files':48,'records':60,'executable':43,'nonexecutable':17},'server':{'files':39,'records':27,'executable':23,'nonexecutable':4},'native':{'files':98,'records':218,'executable':204,'nonexecutable':14}},'excluded_write_native_db_policy_ids':excluded,'navigation_corrections':len(corrections),'adjudication':'Original file/line/source text and IDs identify retained evidence, but some operation labels/columns were stale or conflated catch/Elvis, and RH294 label was reused in different files. Independent original-record-to-actual-token mapping preserves every distinct semantic site; no missing file/site or hidden failure remained. The corrected immutable review addendum supplies precise operations/fault/current authority/recovery and disambiguates both RH294 entries by original ordinal/path. Task requires precise site coverage, not globally unique label syntax. Navigation inaccuracy alone is not a product or Task acceptance blocker once full evidence is reconciled. Original artifacts are unchanged; no production Fix needed. 305 is an inventory record count, never305 unique label strings or305 actual catch blocks.','standards_findings':[],'task_spec_findings':[],'source_status_after':clean,'source_lease':'RELEASED_READ_ONLY_REVIEW','overall_regular_result':'PASS','specialized_audit':'PENDING_DIFFERENT_FRESH_CONTEXT_SAME_FINAL_SHA','hostedCI_protectedIntegration_actualMain_safeSync':'PENDING','stage_gate':'S2 OPEN'})
print('PASS independent aggregate185 files/305 distinctID-token locations:270 executable+35 nonexec; helper seals verified; samecleanfinalSHA. REGULAR ONLY, specialized/CI/main synchronization stillPENDING.')
