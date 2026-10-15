import pathlib,json,sys
r=pathlib.Path.cwd()
if sys.argv[1]=='authority':
 t=(r/'spec/architecture/frozen-architecture.md').read_text(encoding='utf-8')
 import re
 for s in re.split(r'(?=<a id="section-)',t):
  if re.match(r'<a id="section-(2-3|3|5|6|7|10|11|12|13|14|18|21)(?:"|-)',s):print(s)
 for p in sorted((r/'spec/architecture/decisions').glob('*.md')):
  if any(p.name.startswith('ADR-'+n) for n in ['0003','0005','0006','0008','0009','0010','0011','0012']):print('\nFILE',p);print(p.read_text(encoding='utf-8'))
else:
 i=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text(encoding='utf-8'))
 for f in i['files']:
  p=f['path']
  if p.startswith(tuple('clients/'+x+'/' for x in ['shared','desktop','mobile'])) and (sys.argv[1]=='all' or sys.argv[1] in p):
   print('\nFILE',p)
   b=(r/p).read_bytes()
   if b'\0' in b:print('BINARY',len(b));continue
   for n,l in enumerate(b.decode('utf-8').splitlines(),1):print(f'{n}: {l}')
