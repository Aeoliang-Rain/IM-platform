from pathlib import Path
import json,sys,hashlib
R=Path.cwd();I=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text('utf-8-sig'))
files=[x for x in I['files'] if x['path'].startswith(('clients/shared/','clients/web/'))]
for f in files[int(sys.argv[1]):int(sys.argv[2])]:
 p=R/f['path'];b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==f['sha256'];print('\nFILE '+f['path'])
 if p.suffix=='.json':
  j=json.loads(b);print(json.dumps(j if p.name!='package-lock.json' else {'name':j.get('name'),'lockfileVersion':j.get('lockfileVersion'),'root':j['packages'][''],'packages':len(j['packages'])},ensure_ascii=False))
 elif p.suffix=='.png':print('PNG asset signature '+str(b[:24]))
 else:print(b.decode('utf-8-sig'))
