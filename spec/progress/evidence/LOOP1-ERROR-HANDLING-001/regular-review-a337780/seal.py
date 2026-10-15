import pathlib,json,hashlib,subprocess,datetime
out=pathlib.Path(__file__).parent;root=pathlib.Path('H:/.codex/worktrees/err/IM-platform')
def git(*args):return subprocess.check_output(['git',*args],cwd=root).decode().strip()
status=git('status','--porcelain=v1');assert status=='';sha=git('rev-parse','HEAD');assert sha=='a337780de5f2ab5d2c8cd43d93c66dac06d53a53';branch=git('branch','--show-current');assert branch=='task/LOOP1-ERROR-HANDLING-001'
meta=json.loads((out/'research/runs/R-ERROR-REGULAR-A337780/metadata.json').read_text('utf8'));events=[json.loads(x) for x in (out/'research/runs/R-ERROR-REGULAR-A337780/events.jsonl').read_text('utf8').splitlines()]
commands=[e for e in events if e.get('event_type') in ['command_started','command_finished']]
(out/'recorded-command-history.json').write_text(json.dumps(commands,indent=2,ensure_ascii=False),encoding='utf8')
files=[]
for p in sorted(out.rglob('*')):
 if p.is_file() and p.name not in ['final-receipt.json','final-receipt.sha256']:
  files.append({'path':p.relative_to(out).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
r={'result':'FAIL','reviewer':'/root/regular_review_a337780','fresh_independent':True,'candidate_sha':sha,'branch':branch,'assigned_root':str(root),'resolved_git_root':git('rev-parse','--show-toplevel'),'diff_base':'35bd6f5f1091503f95a0282f730ed04233b0b6ea','clean_committed_checkout':True,'status':status,'source_lease':'RELEASED','candidate_or_main_writes':False,'push_or_ci':False,'findings':['F-ANDROID-SUPPRESSED-UNKNOWN P2','F-RETAINED-GROUND-MISMATCH P2'],'coverage':{'hashes':185,'composite_navigation_coordinates':307,'executable':272,'nonexecutable':35,'protected':65,'whole_baseline_equal':63,'read_mapper_only_exceptions':2,'whole_semantic_review_complete':False,'reason':'Reproducible failure; no whole-scope PASS claimed'},'test_scope':'Exact production SyncHttps on current JVM with controlled existing connection factory; not Android emulator acceptance','recorder_run':'R-ERROR-REGULAR-A337780','instrumentation_result':'finished structural validation only; direct read/prep gaps disclosed','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'artifacts':files}
p=out/'final-receipt.json';p.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf8');h=hashlib.sha256(p.read_bytes()).hexdigest();(out/'final-receipt.sha256').write_text(h+'\n',encoding='ascii');print(str(p));print(h);print('clean source lease RELEASED; artifacts',len(files))
