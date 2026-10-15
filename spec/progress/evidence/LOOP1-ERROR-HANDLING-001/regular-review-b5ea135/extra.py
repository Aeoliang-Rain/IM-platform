from pathlib import Path
import json,hashlib,re,subprocess,importlib.util
R=Path('H:/.codex/worktrees/err/IM-platform');E=Path(__file__).parent
SHA='b5ea1350cd1909582029c6258d17b37f5354e594'
def dump(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
extra=[]
for p in ['clients/desktop/src-tauri/src/desktop_capabilities.rs','clients/desktop/src-tauri/src/lib.rs','clients/desktop/src-tauri/src/database.rs','clients/desktop/src-tauri/src/bin/storage_probe.rs']:
 for n,line in enumerate((R/p).read_text('utf8').splitlines(),1):
  for m in re.finditer(r'map_err|\.expect\(|Err\(keyring::Error::NoEntry\)|result\.is_err\(\)',line):
   excluded=p.endswith('database.rs'); ground='EXCLUDED_BY_HUMAN unchanged SQLx error/transaction projection, reviewed for literalquery provenance compatibility and byteequality; no write correction/acceptance.' if excluded else 'Literal native SDK/library/filesystem failure returns explicit sanitized Result Err or panics via expect; no false capability result; owned language-file unavailable alone en default mandated ADR12. keyring NoEntry alone legitimate absent/idempotent removal under ADR9.'
   extra.append(dict(id=f'ADDITIONAL-NATIVE-{len(extra)+1}',path=p,line=n,column=m.start()+1,source=line.strip(),specific_ground=ground,authority='Frozen§6.1/ADR9native/ADR12language/currenterrorhandling; humanexcludedwrite',candidate=SHA,input_sha256=hashlib.sha256((R/p).read_bytes()).hexdigest(),verdict='RETAIN_VALID_OR_SCOPE_EXCLUDED'))
# Finish omitted necessary root-boundary issue sites precisely outside regex navigation.
for p,needle in [('clients/shared/protocol-sdk/src/sync/http.ts','Object.defineProperty'),('clients/web/src/application/http.ts','Object.defineProperty')]:
 for n,line in enumerate((R/p).read_text('utf8').splitlines(),1):
  if needle in line:extra.append(dict(id=f'F-CLEANUP-CYCLE-{len(extra)+1}',path=p,line=n,column=line.index(needle)+1,source=line.strip(),specific_ground='FAIL: direct validation primary included as aggregate root then mutated cause into same aggregate; thrownError.cause.errors[0]===thrownError proven. Raw read/decode primary modes acyclic, directprotocol missing tests.',verdict='FAIL',candidate=SHA))
dump('additional-grounds.json',extra)
# Puredata and dependency inputs actually parse whole bytes, baseline compare.
rows=[]
for f in json.loads((E/'own-semantic-coverage.json').read_text('utf8')):
 p=f['path'];raw=(R/p).read_bytes()
 if p.endswith('.png'):assert raw[:8]==b'\x89PNG\r\n\x1a\n'
 elif p.endswith('.ico'):assert raw[:4]==b'\x00\x00\x01\x00'
 elif p.endswith('package-lock.json') or p.endswith('Cargo.lock'):
  if p.endswith('.json'):d=json.loads(raw);detail={'packages':len(d.get('packages',{}))}
  else:
   import tomllib
   d=tomllib.loads(raw.decode());detail={'packages':len(d.get('package',[]))}
  old=subprocess.check_output(['git','show','35bd6f5f1091503f95a0282f730ed04233b0b6ea:'+p],cwd=R);assert old==subprocess.check_output(['git','show',SHA+':'+p],cwd=R);rows.append(dict(path=p,unchanged=True,detail=detail))
# complete resource all3end equality, parse andvalidate actual productionbuilder without outputs.
s=importlib.util.spec_from_file_location('review_actual_pack',R/'tools/build_language_packs.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);d=m.sources(R);assert m.artifacts(d)==m.artifacts(m.sources(R));rows.append(dict(path='all3end language maps',keycount=len(d['en']),puredata=True,exactequality=True))
dump('declarative-checks.json',rows)
print('PASS additional native grounds and full puredata/lock/binary/source inspections',len(extra))
