import pathlib,json,hashlib,subprocess,datetime
out=pathlib.Path(__file__).parent
root=pathlib.Path('H:/.codex/worktrees/err/IM-platform')
run=out/'research/runs/R-REGULAR-A292-SERVER-R2'
coverage=json.loads((out/'coverage.json').read_text(encoding='utf-8'))
events=[json.loads(s) for s in (run/'events.jsonl').read_text(encoding='utf-8').splitlines()]
commands=[]
for e in events:
 if e['event_type']=='command_finished':
  d=e['data'];start=next(x for x in events if x['event_type']=='command_started' and x['data']['command_id']==d['command_id'])
  commands.append(dict(d,argv=start['data']['argv'],started_at=start['timestamp'],finished_at=e['timestamp']))
for c in commands:
 if 'go' in c['argv'] and '-C' in c['argv']:
  body=(run/c['stdout_blob']).read_text(encoding='utf-8');c['actual_skip_lines']=[l for l in body.splitlines() if '--- SKIP:' in l];c['skipped_count']=len(c['actual_skip_lines'])
status=subprocess.check_output(['git','-c','core.excludesFile='+str(out/'empty-ignore'),'status','--porcelain=v1'],cwd=root,text=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
assert not status and head==coverage['candidate_sha']
seals={str(p.relative_to(out)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'coverage.json',out/'seal_review.py',out/'prompt.txt',*sorted(run.glob('*.json')),run/'events.jsonl',run/'diff.patch'] if p.exists()}
receipt=dict(verdict='PASS_BOUNDED_SERVER_REGULAR_REVIEW',actor=coverage['actor'],role=coverage['role'],candidate_sha=head,baseline=coverage['baseline'],branch=coverage['branch'],diff_range=coverage['diff_range'],clean_before=True,clean_after=True,production_files=39,retained_sites=27,findings=[],commands=commands,seals=seals,recorder=dict(result='STRUCTURAL_PASS',run_id='R-REGULAR-A292-SERVER-R2',capture_mode='prospective_resume',pre_recorder_trace_complete=False),limits=coverage['limits']+['First own seal command failed because git refuses NUL as excludes file; corrected to own empty external file and reran. Original failure preserved.','Direct startup and semantic tool output included truncated authority attempts; relied on bounded source reads for server logic. Recorder covers recorded tests/seals, not every direct read.','No live DB/NATS restart or runtime mutation performed; parent assesses prior sealed live evidence/source bindings.'],created_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(out/'final-receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'receipt_sha256':hashlib.sha256((out/'final-receipt.json').read_bytes()).hexdigest(),'commands':[(c['exit_code'],round(c['duration_ms'],1)) for c in commands],'clean':True}))
