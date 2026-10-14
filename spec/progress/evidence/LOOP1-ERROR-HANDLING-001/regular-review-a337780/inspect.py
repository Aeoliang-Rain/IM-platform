import pathlib,json,subprocess,hashlib,sys
root=pathlib.Path('H:/.codex/worktrees/err/IM-platform'); out=pathlib.Path(__file__).parent
base='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def git(*a):return subprocess.check_output(['git',*a],cwd=root)
inv=json.loads((root/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text('utf8'))
nav=json.loads((root/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-appearance-read/current-navigation.json').read_text('utf8'))
if sys.argv[1]=='collect':
 rows=[]
 for f in inv['files']:
  p=f['path'];b=git('show','HEAD:'+p);h=hashlib.sha256(b).hexdigest();assert h==f['sha256'],p
  rows.append({'path':p,'sha256':h,'bytes':len(b),'kind':f['kind']})
 (out/'source-inputs.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 keys=set()
 for n in nav['records']:
  key=(n['original_ordinal'],n['path'],n['original_id']);assert key not in keys;keys.add(key)
  b=git('show','HEAD:'+n['path']);assert hashlib.sha256(b).hexdigest()==n['source_sha256']
  if n['executable']:
   line=b.decode('utf8').splitlines()[n.get('current_line',n.get('line'))-1];assert line==n.get('current_source',b.decode('utf8').splitlines()[n.get('current_line',n.get('line'))-1]),(key,line,n.get('current_source',b.decode('utf8').splitlines()[n.get('current_line',n.get('line'))-1]))
 (out/'navigation-inputs.json').write_text(json.dumps(nav,indent=2,ensure_ascii=False),encoding='utf8')
 (out/'full.diff').write_bytes(git('diff','--binary',base,'HEAD'))
 (out/'production.diff').write_bytes(git('diff',base,'HEAD','--',*[r['path'] for r in rows]))
 print('PASS',len(rows),len(keys),'exact source hashes and navigation coordinates; full diff saved')
elif sys.argv[1]=='read':
 start,end=map(int,sys.argv[2:4]);fs=inv['files'][start:end]
 for i,f in enumerate(fs,start):
  print('\nFILE',i,f['path']);b=git('show','HEAD:'+f['path'])
  if b'\0' in b:print('BINARY',len(b));continue
  print(b.decode('utf8'))
elif sys.argv[1]=='nav':
 a,b=map(int,sys.argv[2:4])
 for n in nav['records'][a:b]: print(n['composite_key'],n.get('current_line',n.get('line')),n.get('current_source',b.decode('utf8').splitlines()[n.get('current_line',n.get('line'))-1]),'FAULT',n['specific_fault'],'GROUND',n['present_requirement'],'RESTORE',n['actual_restored_or_failed_state'])


