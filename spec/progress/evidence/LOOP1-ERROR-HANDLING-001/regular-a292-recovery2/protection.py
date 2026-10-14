from pathlib import Path
import json,hashlib,re,subprocess,fnmatch
R=Path.cwd();E=Path(__file__).parent;sha='a292f516f622651ae62595163e479c13fff78c1d';base='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def git(*a):return subprocess.check_output(['git','--no-replace-objects',*a],cwd=R)
def h(x):return hashlib.sha256(x).hexdigest()
inv=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text('utf-8-sig'))
checks=[]
for f in inv['files']:
 b=(R/f['path']).read_bytes();checks.append({'path':f['path'],'inventory_hash_match':h(b)==f['sha256'],'sha256':h(b)})
save('inventory-checks.json',checks)
assert all(c['inventory_hash_match'] for c in checks)
protect=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read/protected-read-scope.json').read_text('utf-8-sig'))
pr=[]
for f in protect['proof']:
 p=f['path'];a=git('show',base+':'+p);b=git('show',sha+':'+p);row={'path':p,'baseline_sha256':h(a),'candidate_git_sha256':h(b),'whole_equal':a==b}
 if p.endswith('repository.ts') or p.endswith('/Repository.kt'):
  pattern=rb'  async contiguous\(.*?(?=  async conversationIds\()' if p.endswith('.ts') else rb'    fun contiguous\(.*?(?=    fun conversationIds\()'
  ma=re.search(pattern,a,re.S);mb=re.search(pattern,b,re.S)
  assert ma and mb,(p,'method markers')
  sql_a=re.findall(rb'"(SELECT [^"]+)"',ma.group());sql_b=re.findall(rb'"(SELECT [^"]+)"',mb.group())
  row.update(outside_method_equal=a[:ma.start()]+a[ma.end():]==b[:mb.start()]+b[mb.end():],read_SQL_same=bool(sql_a) and sql_a==sql_b,read_SQL=sql_b[0].decode() if sql_b else None,authorized_exception=True)
 pr.append(row)
save('protected-checks.json',pr)
assert sum(z['whole_equal'] for z in pr)==63 and all(z['whole_equal'] or z.get('outside_method_equal') and z.get('read_SQL_same') for z in pr)
task=(R/'spec/tasks/review/LOOP1-ERROR-HANDLING-001.md').read_text('utf8')
scope=task.split('# Allowed Paths',1)[1].split('# Acceptance',1)[0]
patterns=re.findall(r'^- `([^`]+)`',scope,re.M)
paths=git('diff','--name-only','--no-renames',base,sha).decode().splitlines();bad=[p for p in paths if not any(fnmatch.fnmatchcase(p,z) for z in patterns)]
save('scope-checks.json',{'range':base+'..'+sha,'paths':paths,'outside_allowed':bad,'authority_unchanged':not any(p.startswith(('contracts/','spec/architecture/','spec/domain/','spec/invariants/')) for p in paths)})
assert not bad,bad

