import pathlib,json,hashlib,subprocess,re
r=pathlib.Path.cwd();ext=pathlib.Path(__file__).parent;base='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def h(b):return hashlib.sha256(b).hexdigest()
i=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text(encoding='utf-8'));fs=[f for f in i['files'] if f['path'].startswith(('clients/shared/','clients/desktop/','clients/mobile/'))]
out=[]
for f in fs:
 p=f['path'];b=(r/p).read_bytes();assert h(b)==f['sha256'],p
 out.append(dict(path=p,sha256=h(b),bytes=len(b),responsibility=f['responsibility'],inspection='Independent read of production responsibility, real imports and failure/default/control paths; configuration/assets bound and nonexecutable data differentiated.',result='NO_NEW_IN_SCOPE_ERROR_HANDLING_FINDING'))
pr=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/protected-inputs.json').read_text(encoding='utf-8'));ps=[]
for f in pr['files']:
 p=f['path'];a=subprocess.check_output(['git','show',base+':'+p]);b=(r/p).read_bytes();equal=a==b
 if not equal:
  if p.endswith('repository.ts'):pat=rb'  async contiguous\(.*?\n  }'
  elif p.endswith('Repository.kt'):pat=rb'    fun contiguous\(.*?(?=    fun conversationIds)' 
  else:raise AssertionError(p)
  ma=re.search(pat,a,re.S);mb=re.search(pat,b,re.S);assert ma and mb
  assert a[:ma.start()]+a[ma.end():]==b[:mb.start()]+b[mb.end():],p
  qa=re.findall(rb'"SELECT[^"\n]*"',ma.group());qb=re.findall(rb'"SELECT[^"\n]*"',mb.group());assert qa==qb,p
 ps.append(dict(path=p,baseline_sha256=h(a),candidate_sha256=h(b),whole_equal=equal,only_authorized_contiguous_mapper=not equal))
assert len(ps)==65 and sum(p['whole_equal'] for p in ps)==63
fix=ext.parent.parent/'regular-review-a292-recovery2/fixture';matches=[]
for f in fs:
 p=f['path'];q=fix/p
 if q.is_file() and not p.endswith(('Cargo.lock','package-lock.json')):
  assert q.read_bytes()==(r/p).read_bytes(),p;matches.append(p)
(ext/'coverage.json').write_text(json.dumps(out,indent=2),encoding='utf-8');(ext/'protected-verification.json').write_text(json.dumps(ps,indent=2),encoding='utf-8');(ext/'fixture-binding.json').write_text(json.dumps(matches,indent=2),encoding='utf-8');print('PASS',len(fs),'candidate hashes;',len(ps),'protected63whole2method SQL unchanged; fixture matched',len(matches))

