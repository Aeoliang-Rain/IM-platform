import json,hashlib,pathlib,sys,subprocess
R=pathlib.Path('H:/.codex/worktrees/err/IM-platform')
O=pathlib.Path(__file__).parent
E=R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='runtime':
 h=json.loads((E/'verification-history.json').read_text(encoding='utf-8'))
 print(type(h).__name__)
 rows=h if isinstance(h,list) else h.get('commands',h.get('history',[]))
 for row in rows:
  if any('go_live' in str(x) or 'errors/java' in str(x) or 'go test' in str(x) for x in row.values()):
   print(json.dumps(row,ensure_ascii=False))
elif sys.argv[1]=='authority':
 text=(R/'spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')
 for section in ['2.3','5.2','7.3','12','14']:
  pos=text.index('### 2.3 ') if section=='2.3' else text.index('<a id="section-'+section.replace('.','-')+'"')
  end=text.find('<a id=',pos+10)
  print(text[pos:end])
elif sys.argv[1]=='state':
 for args in [['rev-parse','HEAD'],['rev-parse','--show-toplevel'],['status','--porcelain'],['diff','--name-only','35bd6f5..HEAD','--','backend','deploy','plugins','contracts','tools/build_language_packs.py']]:
  p=subprocess.run(['git','-c','core.excludesFile=.git/info/exclude',*args],cwd=R,capture_output=True,text=True,check=True)
  print(args,p.stdout,p.stderr)
 print('canonical',sha(R/'spec/architecture/frozen-architecture.md'))
