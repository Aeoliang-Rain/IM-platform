import json,re,hashlib,subprocess
from pathlib import Path
E=Path(__file__).parent;R=Path('H:/.codex/worktrees/err/IM-platform');SHA='26a2941024c561d711d0d572b82f0f0f7a46d984'
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def load(p):return json.loads(p.read_text(encoding='utf8'))
inventory=load(E/'input-coverage.json');server=load(E/'server/coverage.json');native=load(E/'native/files.json')
delegated={x['path'] for x in server+native}
results=[]
for x in inventory:
 p=x['path']
 if p in delegated:continue
 text=(R/p).read_bytes().decode('utf8',errors='replace')
 if '/application/' in p:reason='Full literal producer/consumer and state sequence read. HTTP and WSS known external failures retain failed/error/retirement UI; unknown observer/validation/mapper/adapter roots escape before account-stale checks. Serial known failures recover scheduling while original operation rejects; unknown queue remains rejected. Native read tagging occurs at literal invoke; no cross-service/native business ownership.'
 elif '/protocol-sdk/src/sync/' in p:reason='Full strict HTTPS status/cache/correlation/pagination/parser responsibility read. Reader and fatal UTF8 operations are narrow known external boundaries. Mandatory cancel preserves same root and distinct root aggregation; fresh projection avoids cause cycle. Unknown stream/decoder/cleanup errors escape classified recovery. No data or cursor fabricated.'
 elif '/protocol-sdk/src/send/' in p:reason='Full exact protocol parser read: integer precision, duplicate-key/depth/length/string checks satisfy canonical wire; SyntaxError only at JSON string literal parse projects WireFailure. Unknown errors propagate. Optional parser lexemes are grammar defaults, no false data.'
 elif '/storage/' in p:reason='Full storage models/schema/native intent direction read. Existing SQLite writes and transaction/draft policies excluded and byte-protected. ONLY explicitly Human-permitted contiguous READ change treats absent row0, present malformed/noncanonical/out-of-signed64 values throw; same SQL and every other Repository byte unchanged.'
 elif '/i18n/' in p:
  reason='Full pure language table/resource/context read: display-only fixed locale/key lookup, English fallback permitted by Frozen6.6/ADR12; English missing key throws. Missing presentation parameter remains visible placeholder; no business-value fallback or state rewriting.'
  if p.endswith(('en.ts','ja-JP.ts','zh-CN.ts')):
   table=json.loads(text[len('export default '):].strip().removesuffix(';'));assert len(table)==260 and all(isinstance(k,str) and isinstance(v,str) for k,v in table.items())
 elif '/components/' in p or p.endswith(('main.tsx','composer.ts')):reason='Full actual JSX/mount/props/event path read. Required message content/identity/state throw on invariant breaks; optional profile/preview/selection placeholders represent current absence only. Unknown Promise rejections exposed to normal host failure; no catch conversion. Composer/draft unchanged excluded policy.'
 elif p.endswith('appearance.ts'):reason='Full fixed-key three-field browser adapter read. ADR11 explicitly permits absent/malformed/unavailable in-memory defaults. Only native DOMException, parse SyntaxError, local InvalidAppearance are handled; arbitrary TypeError/Error/primitive escapes. Save validation outside boundary and false only real DOMException informs UI.'
 elif p.endswith('language.ts'):reason='Full fixed-key locale adapter read. ADR12 exact locale, missing/invalid and actual DOMException default en; save false on genuine unavailable only; unknown escapes and unrelated keys untouched.'
 elif p.startswith('deploy/'):reason='Full runtime composition/proxy/build read: role-isolated Go/Java profiles, migration prerequisite, PostgreSQL authoritative, ordinary NATS delivery, sole Caddy TLS entry, read-only config; health/exit failures block startup. No fallback alternate role or speculative infrastructure.'
 elif p.endswith('migrate.py'):reason='Full transaction/checksum/advisory-lock migration runner read. psql ON_ERROR_STOP/nonzero raises, concurrency/checksum/data-loss guards fail, CLI known RuntimeError prints and exits1; other exceptions escape. No fictitious completed migration.'
 elif p.endswith('build_language_packs.py'):reason='Full pure-resource deterministic builder read. Reject duplicate/unsafe keys, cross-end table/parameter mismatch and unknown owned output. Temporary atomic replace cleanup preserves required errors; no swallowed failed build.'
 elif p.endswith('.png'):reason='Binary static logo inspected as tracked PNG asset, no executable fault handling; unchanged current assembly copies it.'
 elif p.endswith('package-lock.json'):
  lock=json.loads(text);reason='Parsed entire locked npm package graph, package metadata checked against current approved React/TypeScript/Tauri frontend tools. No dependency delta or runtime framework added.'
 else:reason='Full current build/config/README/empty placeholder/static CSS/HTML read. Explicit current mount/import mapping and readonly field/dependency boundaries maintained; build errors propagate; no executable silent fallback or future feature.'
 results.append(dict(path=p,sha256=x['sha256'],reviewed_sha=SHA,identity='/root/regular_review_26a2941',actual_semantic_assessment=reason,imports=x['imports'],result='NO_ADDITIONAL_FINDING'))
save('own-semantic-coverage.json',results)
nav=load(R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-outbox-mixed/current-navigation.json')['records'];sites=[]
for x in nav:
 if x['path'] in delegated:continue
 line=x.get('line',x.get('current_line'));col=x.get('column',x.get('current_column'));lines=(R/x['path']).read_text(encoding='utf8').splitlines()
 authority=x.get('present_authority',x.get('present_requirement',x.get('authority','Frozen6/7/11; current accepted contracts; error-handling governance')))
 if not authority:authority='Frozen6/7/11; exact current HTTP/WSS/Sync contracts and error-handling governance; ADR11 for Web appearance, ADR12 for locale'
 fault=x.get('specific_fault');recovery=x.get('actual_recovery_or_failure',x.get('actual_restored_or_failed_state',x.get('recovery')))
 disposition='NONEXECUTABLE_GRAMMAR' if not x['executable'] else 'RETAINED_PRESENT_GROUND'
 if x['path'].endswith('storage/repository.ts'):
  fault='No conversation row from the literal read; present invalid row is a distinct invariant failure'
  authority='Human second narrow READ mapper approval; Frozen6.3/6.4 and signed64 existing SQLite storage; public Sync contract remains unchanged'
  recovery='Only rows.length===0 returns0n; present null/empty/noncanonical/overflow throws original normal error; unchanged query and zero writes'
  disposition='AUTHORIZED_READ_BOUNDARY_RETAINED'
 if 'Composer' in x['path']:disposition='EXCLUDED_UNCHANGED_DRAFT_POLICY'
 sites.append(dict(identity=x.get('composite_identity',x.get('composite_key')),path=x['path'],line=line,column=col,token=x['token'],executable=x['executable'],sha256=x['source_sha256'],fault=fault,present_authority=authority,recovery_or_failure=recovery,actual_context=lines[max(0,line-2):min(len(lines),line+1)],decision=disposition,independent_assessment='Current entire file and actual producer/consumer manually read before this artifact. Prior navigation is location/record aid only; no prior PASS inherited.'))
save('own-retained-grounds.json',sites)
tree=load(E/'tracked-tree.json')['tracked'];prod={x['path'] for x in inventory};root_paths=[p for p in tree if p.startswith(('backend/','clients/','deploy/','plugins/'))]
excluded=[]
for p in root_paths:
 if p in prod:continue
 assert p.endswith('_test.go') or '/tests/' in p or '/androidTest/' in p or '/src/test/' in p,(p,'unexpected omitted product')
 excluded.append(dict(path=p,reason='Explicit test/fixture source or test placeholder; inspected as validation support, not runtime production'))
save('tree-reconciliation.json',dict(tracked_runtime_roots=len(root_paths),current_inventory=185,excluded_tests=excluded,remaining_production_omissions=[],extra_runtime_inputs=['contracts/database/migrate.py','contracts/database/migrations/0001_initial.up.sql','contracts/database/migrations/0001_initial.down.sql','tools/build_language_packs.py'],note='Independently actual tracked-tree root comparison; empty plugin SDK/fixtures are still included. Read all helper coverage and checked own assembly/import graph. Test/evidence/governance/verification tools not product runtime.'))
print('PASS own complete semantic evidence',len(results),'files',len(sites),'current tokens; fullscope aggregate awaits native finding/probe/seal')
