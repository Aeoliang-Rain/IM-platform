import pathlib,json,hashlib,subprocess,sys
O=pathlib.Path(__file__).parent;R=pathlib.Path('H:/.codex/worktrees/err/IM-platform')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude',*args],cwd=R,text=True).strip()
assert git('rev-parse','HEAD')=='b5ea1350cd1909582029c6258d17b37f5354e594'
assert git('status','--porcelain')==''
report=json.loads((O/'report.json').read_text(encoding='utf-8'))
records=[{'path':str(p),'sha256':h(p),'bytes':p.stat().st_size} for p in sorted(O.rglob('*')) if p.is_file() and p.name!='sealed-receipt.json']
run=O/'research/runs/R-ERROR-REGULAR-B5EA135-BACKEND'
summary=json.loads((run/'summary.json').read_text(encoding='utf-8'))
value={'candidate_sha':git('rev-parse','HEAD'),'base':report['base'],'branch':git('branch','--show-current'),'root':git('rev-parse','--show-toplevel'),'status_porcelain':'','role':report['role'],'actor':report['actor'],'result':report['result'],'files':report['file_count'],'inventory_retained_sites':27,'additional_sites':35,'artifact_seals':records,'research_summary':summary,'recorder_is_not_product_acceptance':True,'full_prospective_trace':False,'no_write_release':report['writer_release'],'next':'Parent full regular Review; different uninvolved specialized audit still required before hosted CI. No integration/main synchronization claimed.'}
(O/'sealed-receipt.json').write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'receipt':str(O/'sealed-receipt.json'),'sha256':h(O/'sealed-receipt.json'),'result':value['result'],'files':value['files']}))
