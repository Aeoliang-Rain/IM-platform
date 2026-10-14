import pathlib,sys,json,hashlib,re
fs=json.loads(pathlib.Path(__file__).with_name('selected.json').read_text())
for i in range(int(sys.argv[1]),int(sys.argv[2])):
 p=pathlib.Path(fs[i]['path']); b=p.read_bytes(); assert hashlib.sha256(b).hexdigest()==fs[i]['sha256']; print('\nFILE',i,str(p),'HASH',fs[i]['sha256'])
 try:
  s=b.decode('utf-8')
  if p.name=='Cargo.lock':
   print('LOCK PACKAGE/DEPENDENCY DECLARATIONS');print('\n'.join(v for v in s.splitlines() if not v.startswith(('checksum =','source ='))))
  elif p.name=='package-lock.json':
   j=json.loads(s);print('JSON lockVersion',j['lockfileVersion']);print(json.dumps({k:{a:b for a,b in v.items() if a not in ['integrity','resolved']}for k,v in j['packages'].items()},indent=2))
  else:print('\n'.join(str(n)+': '+v for n,v in enumerate(s.splitlines(),1)))
 except UnicodeError:print('BINARY',len(b),b[:24].hex())
