import json, hashlib, pathlib, subprocess, datetime
root=pathlib.Path('H:/.codex/worktrees/err/IM-platform')
out=pathlib.Path(__file__).parent
sha='a292f516f622651ae62595163e479c13fff78c1d'
baseline='35bd6f5f1091503f95a0282f730ed04233b0b6ea'
(out/'empty-ignore').write_text('',encoding='utf-8')
def git(*args):return subprocess.check_output(['git','-c','core.excludesFile='+str(out/'empty-ignore'),*args],cwd=root,text=True).strip()
assert git('rev-parse','HEAD')==sha
assert pathlib.Path(git('rev-parse','--show-toplevel')).resolve()==root.resolve()
assert git('status','--porcelain=v1')==''
inv=json.loads((root/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text(encoding='utf-8'))
notes={
'backend/go/core/auth.go':'Core exclusively owns session mutation. Login bcrypt mismatch alone is credential denial; malformed stored hash produces explicit500. Secondary session reads preserve errors rather than declaring invalid auth. newSession locks user before absent slot creation; refresh locks slot; logout revalidates locked identity. Transactions commit before auth/204 success; UUID and internal serialization fail rather than empty result. Successful search ErrNoRows alone returns empty. Cookie/query secret restrictions remain.',
'backend/go/core/http.go':'Core assembly imports shared and pgx only; constructs local Auth handler and private message/history adapters. No Gateway implementation dependency or business placed in root.',
'backend/go/core/message.go':'Core holds session and member authorization, locks sequence row, checks existing request sender/content, commits sequence/message/one Outbox atomically. No success ACK before commit. Unknown new/existing commit confirmation preserves errors.Is original root and uncertainty marker;503 leaves timeout/retry/Sync resolution. Tested P0001/ErrTxCommitRollback alone establish new-message rejection.',
'backend/go/core/outbox.go':'Actual query/scan/rows/recipient/publish/flush/update/commit failures return. Known NATS connection/timeout and net.Error return to existing tick with unpublished data; other failures return to root fatal. No independent retry machinery. Core owns recipients; NATS does not become persistence truth.',
'backend/go/core/social.go':'Successful zero rows are empty friends; scan/iteration/database faults fail before response. Ordered user locks serialize reversed pairs. Session is rechecked after locks. Existing canonical direct must have exactly two active pair members; conflict is explicit409. Friend/direct/membership/user events/Outbox share transaction.',
'backend/go/core/sync.go':'Public request/correlation/auth/type/fields/positive limit validation follows exact Sync contract. Opaque HMAC user cursor bound to account; lock ordering and revalidation preserve committed prefixes and retired sessions. Rows/query/decode/commit failure emits non-success; authoritative bad metadata/gap panics. Cap100 limits pages only. Numeric scanner peek end sentinel is consumed by outer ReadByte, so underlying reader fault is not turned into successful page. Private history remains read-only authorized transaction.',
'backend/go/gateway/gateway.go':'Gateway performs upgrade/bind/read-only validation/registry/proxy/fanout. Exact ADR0010 Tauri origin exception preserves default other origins. send closes failed connection outside mutex; once/done cleanup prevents continuing accepted socket. Known auth rejection differs from unknown DB bind failure closure. Forward records uncertain origin and suppresses invented rejection after transport/non200/malformed ACK. Retry/Sync resolves durable uncertainty. Fanout filters exact user and valid frame; no member business implementation.',
'backend/go/gateway/http.go':'Shared/nonbusiness assembly, subscriptions and public reverse proxy. Subscription/flush/URL parsing errors return startup failure. Invalid transport event does not become business state. Go Gateway imports no Core internals and makes no database writes.',
'backend/go/gateway/session.go':'Read-only authoritative slot validation returns secondary lookup faults. Safety watch closes when authority cannot be established; conservative REVOKED is connection retirement. Only exact committed revocation identity allows LOGOUT/REPLACED reason; failed/missing reason query cannot claim successful Session or invented logout.',
'backend/go/main.go':'Role/config/dependency assembly only, accepted root whitelist. Root starts selected service. Unknown Outbox dispatcher error causes process exit; cancelled owner shutdown is distinguished. Startup/listen failures terminate without credential detail. No Auth/session-write business in root.',
'backend/go/shared/config.go':'Shared support strictly decodes operator settings, rejects trailing/unknown/incomplete fields and read/credential faults. Relative secret-file resolution remains internal support. Read-only file cleanup after checked decode does not pretend valid settings on failure.',
'backend/go/shared/security.go':'Shared crypto/token primitives only: entropy and signing errors return; parse verifies exact header/signature/claims/expiry and classifies known invalid token. HMAC hash.Hash Write cannot return an error. No Session database repository or service reverse import.',
'backend/go/shared/infra.go':'Nonbusiness GET-only health; returned fmt writer failure ends this probe with disconnected response, does not certify durable product operation. Wrong method405. No application data or hidden business.',
'backend/go/plugin-host/http.go':'Existing shared health-only nonbusiness placeholder. No S4 WASM/plugin execution or cross-service business.',
'backend/java/InfraPlaceholder.java':'SRC-06 nonbusiness health/upgrade skeleton. Listener accept is outside per-client IOException catch. Scoped client IO/malformed line closes socket then accepts next. Runtime/digest/programming exceptions escape main. No Spring/business activation; javac and actual normal/IO/original exception controls rerun.',
'contracts/database/migrate.py':'Independent psql runner ON_ERROR_STOP, nonzero RuntimeError exits1. State/checksum/already applied is based on actual psql output; advisory lock and transaction protect canonical migration. Destructive down gated. Read-only review did not run migrations.',
'contracts/database/migrations/0001_initial.up.sql':'Read canonical schema: slot PK/epoch, pair uniqueness, member PK, message request+seq uniqueness, one logical Outbox index, plugin immutable identity triggers. SQL exceptions abort. Authority bytes unchanged against baseline; no execution.',
'contracts/database/migrations/0001_initial.down.sql':'Read reverse dependency drops; failure aborts surrounding runner transaction. Bytes unchanged. Destructive rollback not executed.',
'backend/go/Dockerfile':'Existing build/runtime stages and go download/build propagate failures; no shell ignore or new dependency.',
'backend/go/config.example.json':'Existing operator example locates external credentials and internal endpoints. Loader checks values; no runtime fake-secret fallback.',
'backend/go/go.mod':'Existing approved Go crypto/pgx/Gorilla/NATS and transitive stack unchanged by task. No technology selection introduced.',
'backend/go/go.sum':'Module-integrity data read; no executable recovery. Exact baseline bytes unchanged.',
'backend/java/Dockerfile':'Existing javac/JRE placeholder build; build/start failures stop process. No Java business runtime addition.',
'deploy/Caddyfile':'Existing TLS localhost proxy only; no plaintext public fallback or auth-query rewrite. Bytes unchanged.',
'deploy/README.md':'Existing one-profile/infrastructure/development documentation read. Historical development trust option not exercised. Canonical security still governs production. Independent migration ownership preserved.',
'deploy/compose.yaml':'Existing persistent PG, core NATS, successful migration + health dependencies; exact selected profile roles. Proxy-only public port and readonly external config retained. No deployment mutation or secret access.',
'deploy/migrate.Dockerfile':'Independent canonical Python/psql migration image. Failure propagates command exit. No migration run.',
'tools/build_language_packs.py':'Pure offline resources parse and exact key/locale/placeholder parity enforce artifact equality. Owned temp/atomic replacement rejects unknown output. finally cleanup does not print PASS after fault. Regex is syntax rather than fallback. Actual verify freshly passes; no publication.',
}
files=[]
for e in inv['files']:
 if e['path'].startswith('clients/'):continue
 p=e['path'];raw=(root/p).read_bytes();h=hashlib.sha256(raw).hexdigest();assert h==e['sha256'],p
 if p.endswith('.gitkeep'):
  assert raw==b'\n';note='Exact LF-only empty placeholder verified individually. No runtime, catch, imports or activated future responsibility.'
 else:note=notes[p]
 files.append(dict(path=p,sha256=h,bytes=len(raw),semantic_read='full current source/data',inspection=note,result='NO_ACTIONABLE_FINDING'))
grounds={
'RH001':('newSession failed DB/entropy/revocation operation or finished commit','Frozen4.1/7.3 AUF-I-001/002','Rollback retires transaction; no session success until Commit. pgx rollback after Commit is harmless ErrTxClosed.'),
'RH002':('refresh slot/query/token/update/commit failure','Frozen4.1/7.1 AUF-D-003','Rollback prevents partial credential rotation; failure response, no auth success.'),
'RH003':('logout slot/revocation/Outbox/commit failure','Frozen7.1 AUF-D-008','Rollback retains atomic revoke and204 is reached only after commit.'),
'RH004':('send precommit failure or failed commit confirmation','Frozen5.1 MSG-I-002/003','Rollback cleanup never implies ACK; commit uncertainty retains marker and original cause for503/retry/Sync.'),
'RH005':('Outbox publication/flush/query/update failure','Frozen5.2 MSG-D-006','Failed uncommitted published_at is rolled back; known transport retries existing tick, unknown propagates to fatal dispatcher.'),
'RH006':('friends scan/iteration error or successful completion','AUF-D-006 HTTP friends contract','Rows resource closed; scan and Rows.Err failure precede response. Empty friends only follows successful zero rows.'),
'RH007':('friend/direct/members/events/commit failure','Frozen4.2 AUF-I-006','Rollback prevents partial friendship; transaction success only after Commit.'),
'RH008':('optional decimal regex group literal','Frozen11.5 Sync integer contract','Regex syntax only, no exception or runtime default. Integrality validation rejects bad field.'),
'RH009':('optional exponent regex group literal','Frozen11.5 Sync integer contract','Regex grammar only; exponent magnitude handled boundedly with exact integrality/cap.'),
'RH010':('user Sync lock/auth/DB/decode/commit failure','Frozen11.5 SP-I-004','Read transaction cleanup; no successful page/cursor on failure, invariant defect panics.'),
'RH011':('conversation Sync auth/member/DB/commit failure','Frozen11.5 SP-I-001','Read transaction cleanup releases locks; authoritative gaps panic and no false page published.'),
'RH012':('private history auth/query/scan/iteration/commit failure','Frozen5/6.4 MSG-I-004','Read-only transaction retired, failure non-success, response only after successful Commit.'),
'RH013':('native ws.Close failure/already closed socket','Frozen7.2 AUF-I-003/004','once closes done and underlying socket; registry cleanup/watch retirement follows. Cannot keep failed accepted connection active.'),
'RH014':('revocation frame write failure','Frozen7.2 AUF-I-004','send itself closes on failure, registry removed and explicit close follows. No revoked live socket.'),
'RH015':('unauthenticated message refusal write fails','Frozen7.2 AUF-I-003','send closes and serve returns with deferred cleanup. No accepted business operation.'),
'RH016':('auth refusal ACK write fails','Frozen7.2 WSS AuthAck','send closes; caller returns and registry remains unbound/retired.'),
'RH017':('pre-Core construction failure rejection socket write fails','Frozen5.1 WSS message error','No Core request sent; failed attempt rejected. send closes failure rather than continuing accepted socket.'),
'RH018':('readonly HTTP response close completion/error','Frozen5/7.4 MSG-I-002','Response body retired after read. No false durable result from close; malformed/unconfirmed reply remains uncertain for retry/Sync.'),
'RH019':('Core ACK forwarding websocket write fails','Frozen5.1/5.2 MSG-I-002','send closes connection. Durable outcome unchanged and timeout/retry/Sync recovers missed confirmation.'),
'RH020':('event fanout recipient websocket write fails','Frozen5.2 MSG-D-006/007','send closes failed peer; other recipients independent, persistent truth recoverable via Sync.'),
'RH021':('root-owned pool teardown','Frozen3.3 SRC-02','pgx pool Close returns no error; resource release only, no fake operation outcome.'),
'RH022':('root-owned NATS connection teardown','Frozen3.3 SRC-02','NATS Close returns no error; teardown only and fatal paths already terminate process.'),
'RH023':('readonly config file close after checked reads','Frozen3.3 SRC-03','No writes or durability assertion. Open/Decode/secret read failures already return before valid settings.'),
'RH024':('accepted client IO/timeout/malformed request line','Frozen10 SRC-06','Scoped try resource closes client; next accept legal. accept is outside catch; unknown runtime/digest failure escapes, no fake health.'),
'RH293':('missing psql/nonzero/checksum/state or destructive gate RuntimeError','Frozen11.4 canonical migration runner','Explicit stderr and return1; no applied/pending successful exit for caught failure.'),
'RH294':('Kotlin resource key escape regex literal','ADR0012 Frozen6.6','Regex syntax only; pure data parsing followed by strict resource parity, faults propagate.'),
'RH295':('Kotlin resource value escape regex literal','ADR0012 Frozen6.6','Regex syntax only; malformed/mismatched extracted data cannot pass equality/validation.'),
}
sites=[]
for e in inv['retained_sites']:
 if e['path'].startswith('clients/'):continue
 lines=(root/e['path']).read_text(encoding='utf-8').splitlines();assert e['source'].strip() in lines[e['line']-1].strip(),e['id']
 fault,basis,recovery=grounds[e['id']]
 sites.append(dict(e,concrete_fault=fault,current_basis=basis,true_recovery=recovery,trigger=fault,current_authority=basis,recovery=recovery,result='REGEX_SYNTAX_NOT_FALLBACK' if e['id'] in ['RH008','RH009','RH294','RH295'] else 'RETAINED_JUSTIFIED'))
assert len(files)==39 and len(sites)==27
events=[json.loads(x) for x in (out/'research/runs/R-REGULAR-A292-SERVER-R2/events.jsonl').read_text(encoding='utf-8').splitlines()]
commands=[e['data'] for e in events if e['event_type']=='command_finished']
report=dict(candidate_sha=sha,baseline=baseline,branch=git('branch','--show-current'),diff_range=baseline+'..'+sha,actor='/root/regular_review_a292_recovery2/server_regular',role='fresh_regular_review_helper',independence='Fresh context; no participation in implementation, Fix, or specialized review. Previous server partial is navigation only; every conclusion below independently checked against exact current source.',file_count=39,retained_count=27,files=files,retained_sites=sites,findings=[],verdict='PASS_BOUNDED_SERVER_REGULAR_REVIEW',clean_before=True,clean_after=True,commands=commands,limits=['This is the 39-file/27-site server subset, not full Task/Gate acceptance. Parent owns complete review/minimum checks and remaining client scope.','Fresh go ordinary suite executes relevant local controls but DB_TEST_ENABLE is unset; all live PG/NATS SKIP lines explicitly are unexecuted, not PASS. Existing controlled live evidence is prior, not freshly repeated.','First recorded go test failed because Recorder runs root cwd; explicit go -C backend/go repaired with fresh count=1. Failed command remains immutable.','Ordered startup and direct semantic reads were outside command Recorder. prospective_resume prestart incomplete; command verification from startup onward recorded where possible. No complete prospective trace claim.','No main/source/CI/services/devices/trust changes. External review evidence/cache only. No new specialist role claim.'])
(out/'coverage.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'files':39,'sites':27,'findings':0,'coverage_sha256':hashlib.sha256((out/'coverage.json').read_bytes()).hexdigest()}))
