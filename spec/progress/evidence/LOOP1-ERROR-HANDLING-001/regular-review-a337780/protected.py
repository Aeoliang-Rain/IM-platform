import pathlib,json,hashlib,subprocess
root=pathlib.Path('H:/.codex/worktrees/err/IM-platform');out=pathlib.Path(__file__).parent;base='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def blob(rev,p):return subprocess.check_output(['git','show',rev+':'+p],cwd=root)
data=json.loads((root/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-appearance-read/protected-inputs.json').read_text('utf8'))
rows=[]
for r in data['proof']:
 p=r['path'];b=blob('HEAD',p);h=hashlib.sha256(b).hexdigest();old=blob(base,p)
 same=b==old
 if not same:
  assert p in ['clients/shared/protocol-sdk/src/storage/repository.ts','clients/mobile/app/src/main/kotlin/im/platform/client/storage/Repository.kt'],p
  delta=subprocess.check_output(['git','diff',base,'HEAD','--',p],cwd=root).decode('utf8');(out/(('shared' if '/shared/' in p else 'android')+'-repository.diff')).write_text(delta,encoding='utf8')
 assert h==r['candidate_sha256'],p
 rows.append({'path':p,'sha256':h,'whole_baseline_equal':same})
assert len(rows)==65 and sum(r['whole_baseline_equal'] for r in rows)==63
(out/'protected-verification.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
receipt=out.parent/'fix-appearance-read-recovery/final-receipt.json';h=hashlib.sha256(receipt.read_bytes()).hexdigest();assert h=='c273da4701118e3fc6ffcd829ccbb7bbb0c174c4619106667ff787736f78cf42'
print('PASS65 protected hashes:63 whole baseline equal;2 explicit only-read diffs saved; supplied recovery receipt hash verified')
