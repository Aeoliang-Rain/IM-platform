import json,hashlib,subprocess,re
from pathlib import Path
ROOT=Path('H:/.codex/worktrees/err/IM-platform')
OUT=Path(__file__).parent
E=ROOT/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-outbox-mixed'
SHA='26a2941024c561d711d0d572b82f0f0f7a46d984'
BASE='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def digest(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude','-C',str(ROOT),*args])
def save(name,v):(OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
objects={}
for entry in git('ls-tree','-rz',SHA).split(b'\0'):
 if entry:
  metadata,path=entry.split(b'\t',1);objects[path.decode()]=metadata.split()[2].decode()
assert git('rev-parse','HEAD').decode().strip()==SHA
assert not git('status','--porcelain')
inventory=json.loads((E/'production-hashes.json').read_text(encoding='utf8'))
coverage=[]
for entry in inventory:
 p=entry['path']; raw=(ROOT/p).read_bytes();blob=git('show',SHA+':'+p)
 assert digest(raw)==entry['sha256'],p
 assert raw==blob,p
 text=raw.decode('utf8',errors='replace')
 imports=re.findall(r'(?:import|from|use)\s+[^\n]+',text)
 coverage.append(dict(path=p,sha256=digest(raw),git_blob_equal=True,bytes=len(raw),imports=imports))
assert len(coverage)==185 and len({x['path'] for x in coverage})==185
nav=json.loads((E/'current-navigation.json').read_text(encoding='utf8'))['records']
tokens=[]
for x in nav:
 line=x.get('line',x.get('current_line'));col=x.get('column',x.get('current_column')); token=x['token']
 text=(ROOT/x['path']).read_text(encoding='utf8').splitlines()[line-1]
 assert text[col-1:col-1+len(token)]==token,(x['composite_identity'],line,col,token,text)
 assert digest((ROOT/x['path']).read_bytes())==x['source_sha256']
 tokens.append(dict(identity=x.get('composite_identity',x.get('composite_key')),path=x['path'],line=line,column=col,token=token,executable=x['executable'],source=text,sha256=x['source_sha256']))
assert len(tokens)==306 and len({(x['path'],x['line'],x['column'],x['token']) for x in tokens})==306
assert sum(x['executable'] for x in tokens)==271
protected=json.loads((E/'protected-inputs.json').read_text(encoding='utf8'))['proof']
proof=[]
for x in protected:
 p=x['path'];now=git('show',SHA+':'+p);base=git('show',BASE+':'+p);old=git('show','a292f516:'+p)
 assert now==old and digest(now)==x['candidate_sha256'],p
 if x['byte_equal_baseline']:assert now==base,p
 else:
  assert p.endswith(('Repository.kt','repository.ts'))
  before=base.decode();after=now.decode()
  pat=r'  (?:async )?(?:fun )?contiguous\([^\n]*[\s\S]*?(?=\n  (?:async |fun ))'
  if p.endswith('.ts'):pat=r'  async contiguous\([\s\S]*?(?=\n  async conversationIds)'
  else:pat=r'    fun contiguous\([\s\S]*?(?=\n    fun )'
  a=re.search(pat,before);b=re.search(pat,after)
  assert a and b,p
  assert before[:a.start()]+before[a.end():]==after[:b.start()]+after[b.end():],p
  assert re.findall(r'SELECT[^"\n]+',a[0])==re.findall(r'SELECT[^"\n]+',b[0]),p
 proof.append(dict(path=p,baseline_equal=now==base,a292_equal=True,sha256=digest(now)))
assert len(proof)==65 and sum(x['baseline_equal'] for x in proof)==63
authority=[]
for x in json.loads((E/'authority-inputs.json').read_text(encoding='utf8'))['inputs']:
 raw=(ROOT/x['path']).read_bytes();assert digest(raw)==x['sha256'],x['path'];authority.append(x)
receipt_path=OUT.parent/'fix-outbox-mixed/final-receipt.json'
assert digest(receipt_path.read_bytes())=='e8397f3e232ce2f87ff9dc5ff6ad39f33d3e58e2fe7c49f083a032609f8ed9fe'
receipt=json.loads(receipt_path.read_text())
seals=[]
for p,h in receipt['artifact_sha256'].items():
 path=receipt_path.parent/p;assert digest(path.read_bytes())==h,p;seals.append(dict(path=str(path),sha256=h))
owned=[]
for p in receipt['owned_paths']:
 blob=git('cat-file','blob',objects[p]);assert (ROOT/p).read_bytes()==blob,p;owned.append(dict(path=p,sha256=digest(blob),git_object=objects[p]))
save('input-coverage.json',coverage);save('token-coordinates.json',tokens);save('protected-proof.json',proof);save('authority-hashes.json',authority);save('fix-seal-proof.json',dict(receipt_sha256=digest(receipt_path.read_bytes()),artifact_seals=seals,owned_gitblobs=owned))
save('tracked-tree.json',dict(candidate=SHA,tracked=git('ls-tree','-r','--name-only',SHA).decode().splitlines(),production_paths=[x['path'] for x in coverage],note='Completeness classified against actual tree by Reviewer; authority/test/evidence/tool exclusions are explicit current responsibility, not a grep catch-only inventory.'))
print('PASS exactcleanSHA185raw/blobs306distinctcoordinates271exec/35nonexec65protection63whole/2readmethods181Fixseals777ownedGitblobs')
