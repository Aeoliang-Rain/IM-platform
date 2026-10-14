from pathlib import Path
import json,sys
r=Path.cwd();e=Path(__file__).parent;fs=json.loads((e/'root-selected.json').read_text('utf8'))
for x in fs:
 p=r/x['path']
 if '/application/' in x['path'] or x['path'].endswith(('appearance.ts','language.ts','main.tsx','logo.png','package-lock.json')): continue
 print('\nFILE '+x['path']+'\n'+p.read_text('utf-8-sig'))
