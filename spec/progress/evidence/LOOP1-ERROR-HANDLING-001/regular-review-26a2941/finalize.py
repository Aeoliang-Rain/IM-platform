import json,hashlib,subprocess,datetime
from pathlib import Path
E=Path(__file__).parent;R=Path('H:/.codex/worktrees/err/IM-platform');SHA='26a2941024c561d711d0d572b82f0f0f7a46d984';BASE='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def dig(p):return hashlib.sha256(p.read_bytes()).hexdigest()
py='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
def recorder(*a):return subprocess.check_output([py,'-Xutf8','-B',str(R/'tools/research/recorder.py'),*a,'--repo',str(R),'--research-root',str(E/'research'),'--run-id','R-REGULAR-26A2941']).decode()
helper=[]
for d,name,key in [('server','artifact-seal.json','artifacts'),('native','seal.json','files')]:
 seal=load(E/d/name)
 for x in seal[key]:assert dig(E/d/x['path'])==x['sha256'],(d,x['path'])
 helper.append(dict(path=d+'/'+name,sha256=dig(E/d/name),verified_entries=len(seal[key])))
coverage=load(E/'own-semantic-coverage.json')+load(E/'server/coverage.json')+load(E/'native/files.json')
assert len(coverage)==185 and len({x['path'] for x in coverage})==185
expected={x['path']:x['sha256'] for x in load(E/'input-coverage.json')}
for x in coverage:assert x['sha256']==expected[x['path']]
sites=load(E/'own-retained-grounds.json')+load(E/'server/retained-sites.json')+load(E/'native/tokens.json')
def identity(x):return x.get('identity',x.get('composite_identity',x.get('composite_key')))
assert len(sites)==306 and len({identity(x) for x in sites})==306
save('semantic-coverage.json',coverage);save('retained-grounds.json',sites)
findings=load(E/'native/findings.json');assert len(findings)==1 and findings[0]['line']==43
save('findings.json',findings)
events=[json.loads(x) for x in (E/'research/runs/R-REGULAR-26A2941/events.jsonl').read_text().splitlines()]
commands=[x['data'] for x in events if x['event_type']=='command_finished']
save('command-history.json',commands)
limits=['Fresh live PostgreSQL/NATS command never started: automatic escalation reviewer timed out twice. Prior Fix full DB_TEST_ENABLE1 suite is hashsealed historical corroboration only; no new livePASS. No owned container/image/listener was created by this failed-to-dispatch command.',
 'Existing Windows architecture skip1 is explicit; ordinary Go DB-disabled integrations are not integration PASS. Prior live friend403 Human-deferred runtime case remains unexecuted and not canonicalPASS.',
 'Recorder prospective_resume truthful delegated summary; early startup direct reads/mistyped gitdiff and later direct source reads/web lookup/preparation not fully instrumented. Structural validity is not full trace or Task/Gate acceptance.',
 'Own evidence script initially mismatched heterogeneous navigation fields then gitshow filename-too-long; preserved failures, corrected by actual Git ls-tree objectIDs/cat-file without source edits. First client fixture omitted Mobile pure resource inputs; failure preserved, exact bytes copied, Web retry PASS without weakened assertions.',
 'Source-level Rust standard-library producer proof plus four actual compiled TS consumer controls. No Windows ACL fault incidence measured and no native Rust/Android/device/trust/installedGUI rerun claimed.',
 'Earlier sealed client native APK/SQLx/Rust/TLS evidence qualifies unchanged byte-bound historical corroboration only. No hosted CI, protected integration, actual-main or main sync performed.']
save('limitations.json',limits)
recorder('record-event','--event-type','instrumentation_warning','--data-json',json.dumps(dict(warnings=limits,early_direct_gitdiff_exit1='bad revision a2929',direct_navigation_read_keyerrors='three exploratory compact dump fields absent; not product failures',automatic_approval='timeout twice, command did not dispatch')))
recorder('record-event','--event-type','review_finished','--data-json',json.dumps(dict(result='FAIL',candidate_sha=SHA,findings=['F-APPEARANCE-EXISTS-DEFAULT'],files=185,tokens=306,next_action='fresh Fix then NEW regular then DIFFERENT NEW specialized on new SHA; no CI')))
finished=recorder('finish-run','--result','FAIL');validation=recorder('validate-run')
save('research-validation.json',json.loads(validation));(E/'research-finish.txt').write_text(finished,encoding='utf8')
status=subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude','-C',str(R),'status','--porcelain']).decode()
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip();assert head==SHA and not status
receipt=dict(result='FAIL',role='NEW fresh independent REGULAR Review',identity='/root/regular_review_26a2941',independence='Root and two fresh regular helpers never implemented/fixed this candidate, never specialized audited; all three ineligible SAME SHA specialized role. Prior SHA verdicts not inherited.',candidate_sha=SHA,baseline=BASE,branch='task/LOOP1-ERROR-HANDLING-001',diff_range=BASE+'..'+SHA,root=str(R),clean_before=True,clean_after=True,source_lease='RELEASED',production_files=185,semantic_coverage='semantic-coverage.json',tree_reconciliation='tree-reconciliation.json',current_distinct_navigation_coordinates=306,executable=271,nonexecutable=35,original_duplicate_label='RH294 kept by ordinal/path; 306 record counts never306catches',retained_grounds='retained-grounds.json',additional_server_boundaries=25,supplemental_non_navigation_finding='F-APPEARANCE-EXISTS-DEFAULT',findings=findings,protected='65 checked:63wholebaseline+2HumanREAD-only contiguous methods/SAME SQL and allotherbytes; all65a292equal',minimality='One local Outbox join predicate is required by actual current locked pgx multiaddress producer; no new framework/categories/deps. Appearance repair requires only literal read NotFounddefault vs existing error, no framework or SQLite/draft change.',authority='Frozen efbe04c7, current approved ADRs/domain/invariants/contracts accepted; no authority or contract change; runtime/import/native business boundaries inspected.',fresh_checks='Frozen/PDF, archall, planning,82architecturetests1WindowsSkip, Development/cleanAcceptance, actual realpgxRelay mixed/internal/network/18 classificationcontrols, ordinaryGo,race,vet; exact-source external sharedWebDesktop compile/sharedSendSync/literalnativeRead/cleanup/unknown/contiguous; Webbehaviorappearancecompiledrenderer/i18n and deterministiclanguagepack.',commands=commands,helper_seals=helper,limits=limits,research='R-REGULAR-26A2941 finished FAIL structural validation PASS only; incomplete direct/prestarttrace disclosed',next_exact_action='fresh Fix Fappearance only in Task allowed native path; new finalSHA requires NEW regular and DIFFERENTNEWspecialized. No push/CI triggering PR before bothPASS. Hosted/integration/actualmain/sync allPENDING; Taskreview/S2OPEN.',task_acceptance='PENDING',stage_gate='S2 OPEN',main_sync='PENDING_NOT_PERFORMED',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
receipt['artifact_sha256']={p.relative_to(E).as_posix():dig(p) for p in E.rglob('*') if p.is_file() and not any(z in p.parts for z in ['fixture','go-cache','npm-cache']) and p.name!='final-receipt.json'}
save('final-receipt.json',receipt)
print('FAIL regular finalSHA',SHA,'F-APPEARANCE-EXISTS-DEFAULT P2 line43; sealed185/306/65; source lease RELEASED; receipt',dig(E/'final-receipt.json'))
