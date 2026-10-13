import pathlib,json,sys
r=pathlib.Path('H:/.codex/worktrees/err/IM-platform')
d=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text(encoding='utf8'))
if sys.argv[1]=='sites':
 for s in d['retained_sites']:
  if s['path'].startswith('clients/mobile/'): print(s['id'],s['path'],s['line'],s['column'],s['source'])
else:
 for p in sys.argv[1:]:
  print('\nFILE',p);print((r/p).read_text(encoding='utf8'))
