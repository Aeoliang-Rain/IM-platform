import json,pathlib,hashlib,subprocess
R=pathlib.Path('H:/.codex/worktrees/err/IM-platform');O=pathlib.Path(__file__).parent
E=R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001'
SHA='b5ea1350cd1909582029c6258d17b37f5354e594';BASE='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude',*args],cwd=R,text=True).strip()
def save(name,data):(O/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git('rev-parse','HEAD')==SHA
assert git('status','--porcelain')==''
inv=json.loads((E/'production-inventory.json').read_text(encoding='utf-8'))
selected=[f for f in inv['files'] if f['path'].startswith(('backend/','deploy/','plugins/','contracts/')) or f['path']=='tools/build_language_packs.py']
own={
'backend/go/Dockerfile':'Single Go role-selected build; module download/build failures stop image construction; no credentials copied deliberately, no error fallback.',
'backend/go/config.example.json':'External credential filenames and private service endpoints only; incomplete/failed real config terminates main, no plaintext downgrade.',
'backend/go/core/auth.go':'Core register/login/refresh/logout/user/search; all Session and revocation writes remain here. ErrNoRows and bcrypt mismatch alone are denied/empty results; database/hash/entropy failures end HTTP operation. Deferred rollbacks, secure WEB cookie and native credential delivery remain; request ID/serialization internal failures panic.',
'backend/go/core/http.go':'Core assembly registers existing public auth/social/sync and private message/history only; shared primitives and local service functions, no Gateway business imports.',
'backend/go/core/message.go':'Core validates frame/member/exact Session under locks, serializes sequence and idempotency, writes one message/outbox atomically. Known rejection/confirmed rollback returns rejected ACK; unknown commit retains both cause and uncertainty and returns503 without rejection/success. Duplicate retry returns original tuple.',
'backend/go/core/outbox.go':'Core owns membership lookup/private user subjects. Begin/query/scan/commit failures now return; only typed network/NATS/deadline failures retry next tick with unpublished rows retained. Publish/flush precede mark-published commit. No new retry framework.',
'backend/go/core/social.go':'Core canonical pair locks, session recheck, unique direct and memberships/social event writes in one transaction; real missing target/state conflict map canonical errors, internal DB/encoding failures abort. Existing direct reuse is contract idempotency, not fake data.',
'backend/go/core/sync.go':'Core validates/correlates/authenticates before semantic body checks, opaque user-bound cursor and stable committed prefix, cap-before-conversion numbers, contiguous history and per-request membership. Unknown DB failures non2xx; authoritative invariants panic, no cursor advancement. Numeric parser sentinel is rechecked by outer input read.',
'backend/go/gateway/gateway.go':'Gateway websocket registry/read-only bind/safety check and private HTTP forwarding only. send closes failed socket; malformed external frames retire connection. Core transport/commit uncertainty sends no misleading ACK; local origin registry retains uncertain requests. Session safety closes even on unavailable database; actual revoke reason lookup conservatively defaults REVOKED. No new dependency.',
'backend/go/gateway/http.go':'Gateway subscribes existing NATS subjects, rejects subscription/flush/config failure, proxies /v1 HTTP, owns WSS admission only. Invalid external event drops to durable Sync; no Core package import. Exact Tauri origin exception remains canonical ADR10.',
'backend/go/gateway/session.go':'Gateway read-only Session identity/epoch/status/expiry checks; fallback lookup database errors propagate rather than auth denial. Safety-watch diagnostic reason defaults only on already-failed authentication and closes connection, not accepted authorization.',
'backend/go/go.mod':'Same existing gorilla/pgx/NATS/crypto modules and indirect versions; no task dependency addition or service source imports.',
'backend/go/go.sum':'Immutable lock checksum entries match unchanged module graph; no runtime catch/default behavior.',
'backend/go/main.go':'Root role/config/dependency/service assembly only. Startup dependency failure fatal; Outbox unknown returned failure fatal; shutdown cancellation excluded. Shared supports config/codec only, not Auth writes.',
'backend/go/plugin-host/http.go':'Only accepted non-business health handler; no S4 runtime or plugin bridge implementation.',
'backend/go/shared/config.go':'Operator file strict fields/EOF plus separate password/key reads and minimum secret validation; all read/config failures return, close is read-only descriptor cleanup. No service reverse imports.',
'backend/go/shared/infra.go':'Non-business health probe/method rejection; Fprintf failure means client failed receiving transport probe, no data/state mutation or fake domain recovery.',
'backend/go/shared/security.go':'Only entropy/UUID/HMAC/JWT codec/transport errors. Explicit malformed/signature/expired token rejects; cryptographic random failure returns, no credential logging. No Session/DB/business orchestration.',
'backend/java/Dockerfile':'Existing Java placeholder compilation/runtime only; compile failure stops image, no Spring/S3 product implementation.',
'backend/java/InfraPlaceholder.java':'Exact SRC06 non-business health/websocket probe. Listener accept outside IOException recovery; accepted socket closes before loop continues. Malformed request line explicit IOException; runtime/digest/internal failures propagate to main.',
'contracts/database/migrate.py':'Sole independent canonical SQL runner: psql ON_ERROR_STOP and checked return; ledger checksum, advisory lock and in-lock state guard; down requires explicit destructive flag. RuntimeError prints failure and returns1, unknown Python errors propagate; no success fallback.',
'deploy/Caddyfile':'Existing real HTTPS internal-development-CA reverse proxy; no application fallback or candidate TLS change.',
'deploy/README.md':'Unchanged operational profile/TLS/config/migration instructions. Development smoke alternative is historical infrastructure guidance, not authorization to bypass native production TLS. Warns volume removal and separate profiles.',
'deploy/compose.yaml':'Existing postgres/NATS health dependency and completed-successfully migrate gating, independent Go/Java roles, read-only config mounts, proxy-only published port. Local-development-only credential default explicitly development environment, no unavailable service fake PASS.',
'deploy/migrate.Dockerfile':'Standard Python plus psql runner; same canonical database SQL, process exit directly gates services.',
'tools/build_language_packs.py':'Existing standard-library deterministic pure-data TS/Kotlin en/ja artifact tool. Rejects duplicate/unsafe keys and parameter/data mismatch. Existing owned-output checks preserve unknown files; tempfile replacement and finally unlink retain actual failure. Does not install/download resources.',
'contracts/database/migrations/0001_initial.up.sql':'Read-only unchanged public authority: slot, pair/direct, request/seq, one message outbox uniqueness; plugin immutable/delete triggers; session/user low-frequency events. No error code or schema rewrite.',
'contracts/database/migrations/0001_initial.down.sql':'Unchanged dependency-ordered destructive rollback SQL; execution gated by migrate explicit flag/compatibility review. SQL failure aborts transaction, no ignore.',
}
coverage=[]
for f in selected:
 p=f['path'];raw=(R/p).read_bytes();assert digest(raw)==f['sha256'],p
 description=own.get(p)
 if description is None:
  assert p.endswith('/.gitkeep') and raw==b'\n',p
  description='Exact newline-only placeholder inspected; no executable behavior or implemented future service/plugin mechanism.'
 coverage.append({'path':p,'candidate_sha':SHA,'sha256':digest(raw),'bytes':len(raw),'changed':git('diff','--name-only',BASE,SHA,'--',p)!='','semantic_inspection':description,'imports_responsibility_minimality':'PASS against canonical SRC01-SRC07; no speculative responsibility/dependency introduced','verdict':'PASS','findings':[]})
sites=[]
def ground(s,trigger,authority,recovery,verdict='PASS_RETAINED'):
 p=s['path'];line=s['line'];column=s['column'];actual=(R/p).read_text(encoding='utf-8').splitlines()[line-1]
 assert actual.strip()==s['source'].strip(),(s['id'],actual)
 return {'id':s['id'],'path':p,'line':line,'column':column,'candidate_sha':SHA,'sha256':digest((R/p).read_bytes()),'actual_source':actual,'trigger':trigger,'authority':authority,'actual_recovery_or_failure':recovery,'verdict':verdict,'own_source_inspection':True}
grounds={
'RH001':('newSession exits before commit or succeeds with committed transaction','Frozen§4.1/§7 Session atomic replacement; AUF-I-002','Rollback cleans live transaction; postcommit ErrTxClosed is harmless; failed primary operation is returned and no authResponse reached'),
'RH002':('refresh DB/entropy failure before rotate-token commit','Frozen§7.1 and AUF session contract','Rollback leaves credential state atomic; error response ends request; after commit no live transaction to rollback'),
'RH003':('logout/revocation transaction fails before commit','AUF-D-008 and Frozen§7.1','Rollback prevents partial status/outbox changes; failed logout remains non204; committed logout has no live rollback'),
'RH004':('message authorize/sequence/write/outbox/commit failure','MSG-I-002/003 and Frozen§5.1','Rollback prevents uncommitted message/outbox ACK; primary error preserved; unknown commit remains503 not rejection'),
'RH005':('batch publish/query/update/commit failure','Frozen§5.2 and MSG-D-006','Rollback leaves uncommitted publication marks pending; next accepted transport tick may replay duplicate; unknown errors end dispatcher'),
'RH006':('friend listing iteration/scan ends or fails','Core ownership Frozen§3.1/SRC01; canonical friends response','pgx rows.Close has no error result; rows.Err and Scan errors handled before JSON; descriptor release does not fake empty success'),
'RH007':('friend/add transaction failure or committed completion','AUF-I-005/006 atomic pair/direct/member/event','Rollback aborts partial social changes before errors; postcommit rollback is idempotent close'),
'RH008':('Optional decimal subexpression in literal JSON-number regex','ADR0008 accept mathematical integer/cap-before-conversion','Noncapturing regex group syntax only; not a catch/default/error recovery', 'PASS_NON_HANDLING_FALSE_POSITIVE'),
'RH009':('Optional exponent subexpression in literal JSON-number regex','ADR0008 accept mathematical integer/cap-before-conversion','Noncapturing regex group syntax only; parsed values separately prove integrality', 'PASS_NON_HANDLING_FALSE_POSITIVE'),
'RH010':('user page locking/DB/event/commit failure','Frozen§11.5 stable committed prefix and contracts/http/sync.openapi.json','Rollback closes transaction; failed page never writes successful data/nextCursor'),
'RH011':('conversation page session/membership/query/commit failure','Frozen§11.5 membership/gap-free ordering; SP-I-001','Rollback releases locks; primary error non2xx, no page/cursor emitted'),
'RH012':('private history operation failure before commit','Frozen§5/§6 Sync gap recovery; MSG-I-004','Rollback drops read transaction and retains primary failure; no partial history success'),
'RH013':('retiring already-failed/closed websocket','Frozen§3.1 Gateway lifecycle and §7.2','done closes exactly once; gorilla connection Close releases underlying network resource; prior failed write remains failure; Close return cannot resume socket'),
'RH014':('session.revoked notification write fails','AUF-I-004; Frozen§7.2 revocation and close','send closes on failure; revoke also explicitly closes and registry was removed; stale connection cannot remain authorized'),
'RH015':('prebind rejected message ACK write fails','AUF-I-003 prebind restrictions','send closes; serve immediately returns with deferred retirement; rejected operation never persists'),
'RH016':('auth rejection response write fails','Canonical WSS AuthAck rejection; Frozen§7.2','send itself retires connection and caller serve returns; no valid binding accepted'),
'RH017':('local forward-preparation rejection ACK write fails','Canonical WSS MessageError MESSAGE_COMMIT_FAILED','send closes on failure; forward returns on failed preparation, not claimed committed'),
'RH018':('Core HTTP response read finished or fails','Frozen§5 ACK uncertainty and Gateway routing responsibility','http client response descriptor closes after forwarding; close does not cancel persisted state or replace unknown HTTP outcome; client retry/Sync resolve'),
'RH019':('validated Core ACK cannot be written to originating WSS','MSG-I-002 durable ACK; Frozen§6.2 retry identity','send closes; durable server result remains, client timeout/retry/Sync converge original identity'),
'RH020':('NATS created event write fails to one recipient socket','Frozen§5.2 lossy/duplicate realtime plus Sync','send retires only failing connection; continues other sockets; no server commit rollback or false recipient delivery guarantee'),
'RH021':('main natural cleanup of database pool','SRC02 entry assembly lifecycle','pgxpool Close is void; closes pool, no caught business failure. log.Fatal exits process, so no claimed successful cleanup on fatal path'),
'RH022':('main natural cleanup of NATS connection','SRC02 entry assembly lifecycle','NATS Close is void resource shutdown; no ignored error status or business recovery claim'),
'RH023':('configuration read-only descriptor closes after decode','SRC03 configuration support','read-only os.File close cannot conceal failed decode/read (already returned); no write durability or fallback config'),
'RH024':('accepted peer read/write/timeout/malformed request IOException','Frozen SRC06 Java non-business transport skeleton','try-with-resources retires socket; failed request printed class only; listener continues independent peers. accept, RuntimeException and digest exceptions propagate'),
'RH293':('known runner RuntimeError: psql exit/config/ownership/concurrent/checksum refusal','Frozen§11.4 migrations sole owner and canonical SQL','stderr plus exit1 prevents Compose completed_successfully; does not catch arbitrary Python exception or claim migration complete'),
'RH294':('first Kotlin string regex noncapturing group','ADR0012 pure-data TS/Kotlin equivalent resources','Regex syntax matching escaped source string only; parse errors/duplicate keys/mismatch raise; no exception handling', 'PASS_NON_HANDLING_FALSE_POSITIVE'),
'RH295':('second Kotlin string regex noncapturing group','ADR0012 pure-data TS/Kotlin equivalent resources','Regex syntax only; no fake empty table: equality and nonempty validate reject omissions', 'PASS_NON_HANDLING_FALSE_POSITIVE'),
}
for s in inv['retained_sites']:
 if s['path'] in {x['path'] for x in coverage}:
  sites.append(ground(s,*grounds[s['id']]))
assert len(sites)==27
save('source-coverage.json',coverage);save('retained-sites.json',sites)
additional=[]
def add(p,line,trigger,authority,recovery):
 actual=(R/p).read_text(encoding='utf-8').splitlines()[line-1]
 additional.append({'id':'BK-ADDITIONAL-'+str(len(additional)+1).zfill(3),'path':p,'line':line,'column':len(actual)-len(actual.lstrip())+1,'sha256':digest((R/p).read_bytes()),'candidate_sha':SHA,'actual_source':actual,'trigger':trigger,'authority':authority,'actual_recovery_or_failure':recovery,'verdict':'PASS_RETAINED','inventory_navigation_omission':True})
add('backend/go/core/auth.go',115,'Malformed/disallowed HTTP body','Canonical HTTP validation errors','decode returns400; transport parse failure cannot create valid request')
add('backend/go/core/auth.go',136,'HTTP body write failure after valid marshal','Frozen§3 Gateway/Core external transport','request ends; caller client sees failed/partial transport, no fabricated retry/success data')
add('backend/go/core/auth.go',140,'Unexpected DB/hash/etc error reaches HTTP boundary','Frozen§7.4 secrets and canonical non2xx failure','fixed500 response ends operation, hides credentials/cause from public client, never normal auth status')
add('backend/go/core/auth.go',275,'No existing Session row on first login','AUF-D-001/003','ErrNoRows alone clears absent lookup, creates first atomic slot; other errors return')
add('backend/go/core/auth.go',525,'Authenticated search returns no user','Canonical user search semantics','only ErrNoRows returns users[]; failed DB remains non2xx')
add('backend/go/core/message.go',23,'Commit rejected by confirmed rollback/deferred trigger vs lost confirmation','MSG-I-002; contracts/websocket README','known no-commit can reject; others dual-wrap uncertainty and original cause then503')
add('backend/go/core/message.go',93,'Known precommit failure before durable ACK','WSS MessageError MESSAGE_COMMIT_FAILED','error maps failing rejected send; never committedACK. Unknown commit has earlier separate503 branch')
add('backend/go/core/outbox.go',29,'Typed network/NATS outage or batch timeout','Frozen§5.2 replayable Outbox','original batch failed; rollback retains pending events; next existing500ms tick retries; unknown errors return fatal')
add('backend/go/core/sync.go',43,'Huge positive JSON number exponent','ADR0008 exact cap-before-conversion','integer overflow saturates cap, negative overflow rejects; no input-loss acceptance of fractional value')
add('backend/go/core/sync.go',83,'Unknown Sync server/database failure','contracts/http/sync.openapi.json failure=non2xx','503 Sync unavailable, never successful empty page or cursor advance')
add('backend/go/core/sync.go',169,'Initial literal user cursor0','ADR0008 initialCursor0','legitimate start sentinel only; other malformed/foreign tokens false')
add('backend/go/core/sync.go',554,'number Peek error or end of token','ADR0008 bounded numeric body parser','0 sentinel ends parse; next outer syncJSON ReadByte reobserves nonEOF error and rejects body; EOF alone is normal termination')
add('backend/go/core/sync.go',559,'ReadByte used after successful Peek','Existing bounded parser responsibility','single owner buffer already has byte; ignored read status cannot encounter a new external read on this consume')
add('backend/go/gateway/gateway.go',107,'Websocket upgrade rejects external request','Frozen§7.2 WSS handshake','gorilla emits HTTP handshake failure; serve returns no connection')
add('backend/go/gateway/gateway.go',120,'WSS peer transport/JSON failure','Canonical envelope/§7.2','serve returns and closes/de-registers; internal map marshal errors separately panic')
add('backend/go/gateway/gateway.go',170,'Bind Session validation fails internally','AUF-I-003; no false auth denial','shared.Error only canonical auth.reject; other error closes without claiming token invalid')
add('backend/go/gateway/gateway.go',220,'Safety-watch Session/expiry/database validation fails','Frozen§7.3 authoritative validation plus existing live DB failure close fixture','derive conservative reason then revoke/close; failure never retains authorized connection')
add('backend/go/gateway/gateway.go',269,'Local envelope RawMessage marshal rejects invalid payload','Canonical MessageSend shape','reject/no Core request; current serve validated RawMessage makes internal marshal normally impossible')
add('backend/go/gateway/gateway.go',274,'Private Core request cannot be built','SRC04 authorized internal HTTP boundary','reject before sending; coreURL operator startup URL parsed; no false durableACK')
add('backend/go/gateway/gateway.go',281,'HTTP to Core transport fails; commit status unknown','MSG-I-002 and Frozen§6.2 FAILED=unconfirmed','noACK, keep origin, client timeout/retry/Sync resolves; never rejected after potentially committed send')
add('backend/go/gateway/gateway.go',287,'Non200/malformed/unrelated Core ACK','Canonical correlated committed/rejectedACK','drop untrustworthy ACK, preserve uncertain origin; no invented commit result')
add('backend/go/gateway/gateway.go',311,'Malformed external NATS event','Frozen§5.2 realtime transient loss plus Sync','drop fanout; durable Core state remains; valid Sync recovers missing message')
add('backend/go/gateway/http.go',28,'Malformed NATS revocation payload','Frozen§7.3 NATS optimization not sole authority','no fabricated revoke; readonly safety watch/bind still enforce DB authority')
add('backend/go/gateway/session.go',68,'No recognized reliable cause after failed validation','Frozen§7.2/§7.3 plus existing DB-failure/expiry safety tests','REVOKED closes conservative unsafe connection; not fabricated committed REPLACED/LOGOUT reason')
add('backend/go/gateway/session.go',72,'Revocation provenance lookup unavailable','Same existing conservative safety closure requirement','returns REVOKED while session already failing; does not assert known business cause or healthy state')
add('backend/go/main.go',28,'No IM_CONFIG_FILE env override','SRC02 assembly and deploy read-only config mount','uses fixed existing /run/im-config/config.json, failed read fatal; not fake empty config')
add('backend/go/shared/config.go',42,'Trailing content/read/config decode failure','SRC03 strict operator config','returns failed config, startup fatal, no defaults replacing failure')
add('backend/go/shared/security.go',85,'Malformed/unverifiable/unusable externally supplied token','Canonical AuthError token checks and AUF-I-007','return AUTH_TOKEN_INVALID/EXPIRED with no sensitive data; entropy signing failures not reclassified')
add('backend/go/shared/infra.go',20,'Transport health response write fails','SRC03 accepted non-business health probe','no persisted effect or domain success; request ends, remote gets transport failure')
add('contracts/database/migrate.py',28,'psql stderr empty on nonzero status','Frozen§11.4 and ON_ERROR_STOP runner','diagnostic exit status fallback only; still RuntimeError and exit1')
add('contracts/database/migrate.py',46,'Schema ledger/table/version absent','Canonical migration ownership and ledger','actual absence becomes pending; psql failure raises before result interpretation')
add('contracts/database/migrate.py',57,'Already applied canonical digest','Frozen§11.4 repeatable standalone migration','idempotent no-op only verified checksum; conflicting digest refused')
add('tools/build_language_packs.py',82,'Owned temporary artifact replace fails','Minimality + existing deterministic artifact scope','finally removes own leftover only; replace/cleanup exceptions propagate, noPASS print')
add('deploy/compose.yaml',9,'No development password override','Existing isolated Loop1 Compose infrastructure','explicit local-development-only credential default; does not mask DB connectivity/migration failure')
add('deploy/compose.yaml',36,'Same migration development password override absent','Existing isolated Compose fixture config','same password as database; migration nonzero blocks app roles')
save('navigation-addendum.json',additional)
runtime_root=O.parents[1]/'implementation-research/runs/R-ERROR-IMPLEMENTATION-20261013'
hist=json.loads((E/'verification-history.json').read_text(encoding='utf-8'))['commands']
runtime=[]
for row in hist:
 if any(x.endswith(('errors/go_live.py','errors/java.py')) for x in row['argv']):
  item={'argv':row['argv'],'exit_code':row['exit_code'],'duration_ms':row['duration_ms'],'command_id':row['command_id'],'fresh_run_by_reviewer':False,'blobs':[]}
  for channel in ['stdout','stderr']:
   p=runtime_root/row[channel+'_blob'];raw=p.read_bytes();h=digest(raw)
   # Recorder raw output digest is not necessarily stored redacted digest.
   item['blobs'].append({'path':str(p),'stored_sha256':h,'recorded_raw_sha256':row[channel+'_sha256'],'equal':h==row[channel+'_sha256'],'redaction_declared':row['secret_redaction_applied']})
   if channel=='stdout':
    text=raw.decode('utf-8');item['actual_runtime_markers']=[l for l in text.splitlines() if 'PASS actual' in l or 'PASS compiled' in l or '--- SKIP' in l or 'DEFERRED_BY_HUMAN' in l or 'Owned integration' in l]
  item['assessment']='Prior implementation actual runtime evidence supports unchanged candidate backend bytes; not fresh exact-head acceptance. Go fixture drives DB_TEST_ENABLE=1 disposable PG/NATS; no false counted deferred friend403. Java harness invokes actual private handle and static accept/catch proof, not live listener network IO integration.'
  runtime.append(item)
save('prior-live-inspection.json',runtime)
save('report.json',{'result':'PASS','role':'fresh regular Review backend helper','actor':'/root/regular_review_b5ea135/backend_review','candidate_sha':SHA,'base':BASE,'branch':git('branch','--show-current'),'root':git('rev-parse','--show-toplevel'),'clean_status':git('status','--porcelain'),'file_count':len(coverage),'retained_inventory_site_count':len(sites),'additional_navigation_site_count':len(additional),'findings':[],'independence':'Fresh context; no candidate implementation/Fix/prior Review; regular role only and not eligible as specialized auditor','limitations':['No runtime tests/builds/resource mutation performed by helper; prior exact backend production hashes unchanged after original implementation run, hosted finalSHA acceptance remains required.','Recorder prospective_resume marks incomplete pre-start; direct source/authority inspection after start outside recorder disclosed, no complete prospective trace claimed.','Delegated prompt registered with default source human inadvertently; it is a parent delegation summary, not the original Human full prompt. Immutable original registration preserved with disclosure.','Two external authority extraction ValueError failures and failed rg wildcard navigation retained; corrected command rerun; no product finding from tooling failure.','Only39 selected production files covered by helper; parent owns remaining client/governance candidate and full acceptance decision.'],'writer_release':{'no_source_git_device_trust_writes':True,'no_build_outputs':True,'external_evidence_only':True,'no_owned_runtime_resource':True,'lease':'READ_ONLY_RELEASED'},'canonical_sha256':digest((R/'spec/architecture/frozen-architecture.md').read_bytes()),'inventory_sha256':digest((E/'production-inventory.json').read_bytes())})
print(json.dumps({'files':len(coverage),'sites':len(sites),'additional':len(additional),'result':'PASS'}))
