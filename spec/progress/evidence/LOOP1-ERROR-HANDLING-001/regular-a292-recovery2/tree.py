from pathlib import Path
import subprocess,json,re,hashlib
R=Path.cwd();E=Path(__file__).parent
tracked=subprocess.check_output(['git','ls-files','backend','clients','deploy','plugins']).decode().splitlines()
excluded=[];production=[]
for p in tracked:
 reason=None
 if '/androidTest/' in p:reason='Android instrumentation tests/assets, not production'
 elif '/tests/' in p:reason='Service/native test input or placeholder, not production'
 elif p.endswith('_test.go') and p!='backend/go/main_test.go':reason='Go behavior test, not production'
 if reason:excluded.append({'path':p,'reason':reason})
 else:production.append(p)
extras=['contracts/database/migrations/0001_initial.up.sql','contracts/database/migrations/0001_initial.down.sql','contracts/database/migrate.py','tools/build_language_packs.py']
production+=extras
inv=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text('utf-8-sig'))
expected={x['path'] for x in inv['files']};actual=set(production);assert expected==actual,(expected-actual,actual-expected)
imports=[]
for p in production:
 if Path(p).suffix not in ['.ts','.tsx','.kt','.rs','.go','.java','.py','.mjs']:continue
 t=(R/p).read_text('utf-8-sig')
 imports.append({'path':p,'sha256':hashlib.sha256((R/p).read_bytes()).hexdigest(),'imports':[line.strip() for line in t.splitlines() if re.match(r'\s*(import\b|from\b|use\b|mod\b|export.*from\b)',line)]})
(E/'tree-reconciliation.json').write_text(json.dumps({'tracked_root_inputs':len(tracked),'excluded_test_inputs':excluded,'independently_selected_production':production,'count':len(production),'missing_inventory':sorted(actual-expected),'inventory_overreach':sorted(expected-actual),'root_assembly_test':'backend/go/main_test.go included as canonical SRC02 whitelist support; service business tests excluded','extra_responsibility':'Canonical migration executables and deterministic language packaging are current deployment/build support, included and read-only'},indent=2),encoding='utf8')
(E/'actual-imports.json').write_text(json.dumps(imports,indent=2),encoding='utf8')
print('PASS independent trackedtree reconciliation',len(tracked),'roots minus',len(excluded),'tests plus4canonical DB/languagebuild inputs =',len(production),'inventory exact; actual imports extracted',len(imports),'codefiles')
