import pathlib,json,re,hashlib,subprocess,tomllib
fs=json.loads(pathlib.Path(__file__).with_name('selected.json').read_text());base='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
for i in [6,43,45,86,87,88,89]:
 p=pathlib.Path(fs[i]['path']);b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==fs[i]['sha256'];before=subprocess.check_output(['git','show',base+':'+p.as_posix()]);assert b.replace(b'\r\n',b'\n')==before.replace(b'\r\n',b'\n')
 if i==6:
  j=tomllib.loads(b.decode());print(p,'packages',len(j['package']),'lockversion',j['version'],'unchangedacceptedbaseline rootpackage',[x for x in j['package'] if x['name']=='im-client-storage'])
 elif i==89: print(p,'PNG header',b[:24].hex(),'size',len(b),'unchangedbaseline')
 else:
  s=b.decode();lines=s.splitlines();pat=r'^\s*"[A-Za-z0-9._]+"\s*(?::|to)\s*"(?:[^"\\]|\\.)*",?$';data=[v for v in lines if re.fullmatch(pat,v)];other=[(n,v)for n,v in enumerate(lines,1)if not re.fullmatch(pat,v)];assert len(data)>250
  print(p,'ALL',len(data),'literal-only mappings validated individually; unchanged acceptedbaseline; nondata',other)
