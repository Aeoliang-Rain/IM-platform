from pathlib import Path
import json,hashlib,subprocess,sys
r=Path.cwd();e=Path(__file__).parent;j=json.loads((r/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text('utf8')); selected=[x for x in j['files'] if not x['path'].startswith(('backend/','deploy/','clients/shared/','clients/desktop/','clients/mobile/')) and not x['path'].startswith('contracts/')]; print('root paths',len(selected)); print('\n'.join(x['path'] for x in selected)); print('root sites',sum(x['path'] in {f['path'] for f in selected} for x in j['retained_sites']));
(e/'root-selected.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
if len(sys.argv)>1:
 for x in selected:
  p=r/x['path']; print('\nFILE '+x['path']+'\n'+p.read_text('utf-8-sig'))
