import hashlib,json,subprocess,re
from pathlib import Path
R=Path('H:/.codex/worktrees/err/IM-platform')
O=Path(__file__).resolve().parent
sha='26a2941024c561d711d0d572b82f0f0f7a46d984'
def git(*args):return subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude','-C',str(R),*args],text=True).strip()
assert git('rev-parse','HEAD')==sha
assert git('status','--porcelain')==''
def h(b):return hashlib.sha256(b).hexdigest()
notes={
'backend/go/core/auth.go':'Core owns register/login/refresh/logout and authoritative session authentication. Both auxiliary session lookups return non-NoRows original faults. bcrypt only mismatch means bad credentials; malformed hashes take server failure. Entropy/JSON internal faults escape before false body. HTTP server failure is privacy-safe non-success; not auth denial. Login serializes user slot, refresh locks matching refresh row, logout locks slot/rechecks then revocation/outbox+commit. Search returns empty only exact NoRows. No premature success on SQL errors.',
'backend/go/core/http.go':'Core assembly exposes public Auth/Social/Sync and private send/history; shared health only. No Gateway import or misplaced transaction.',
'backend/go/core/message.go':'Core membership/session shared locks persist to commit; missing session/member explicit rejection. Serialized next_seq and existing logical request lookup preserve dedup. New message/outbox atomic commit precedes ACK. Unknown commit carries both original and uncertainty sentinel using two %w; only proven rejection yields MESSAGE_COMMIT_FAILED. Private adapter failure is not committed ACK.',
'backend/go/core/outbox.go':'Read full relay/batch/classifier. Every Begin/query/scan/rows/publish/flush/update/commit failure returns actual err. Deferred rollback leaves unpublished work for next existing tick; potential duplicate publish is canonical. Classifier directly unwraps; every joined child classified independently, so mixed PgError XX000+network is false. A direct net.OpError retains transport evidence through syscall wrapper; current default transport producer supplies that structure. No errors.As any-descendant shortcut. Unknown/closed-pool fault returns to main and stops process; recognized transient net/NATS/deadline retries without marker commit. No new queue/retry architecture.',
'backend/go/core/social.go':'Auth/membership decisions remain Core. list checks row scan and final rows.Err, never fake empty on fault. add locks normalized user pair then rechecks slot; friend/direct/members/events transaction. Only NoRows authorizes absent/new friend state; persisted inconsistency maps canonical FRIENDSHIP_STATE_CONFLICT. Every insert/query/event/commit failure aborts.',
'backend/go/core/sync.go':'Core public Sync parses/binds requestId, rejects query/fields/version and validates canonical session under locks. User lock prevents skipped earlier allocated metadata; cursor authenticated per user. Reads limit+1 and commits before page. Bad authoritative metadata/gap panic; read/decode/SQL faults non-success, no page/cursor. Auxiliary session DB fault propagates. Numeric normalization grounds exact positive integer cap; EOF/peek sentinel does not finish outer input loop after real reader fault: next ReadByte returns fault, invalid grammar rejects. Private history remains authorized transaction.',
'backend/go/gateway/gateway.go':'Gateway connection/protocol/transport only. Send retires on write failure before returning; all ignored send values are followed by known closed connection. Upgrade/read/protocol failure ends request/socket. UUID/decoded-map JSON internal errors panic. Auth internal DB failure closes unbound socket instead of invalid-token ACK. Watch conservatively revokes bound transport when authority unavailable; lookup reason never invents replacement/logout. Forward external transport/invalid response retains uncertain origin for timeout/retry/Sync, never fabricated committed ACK. Fanout validates event, active user binding/expiry, excludes original sender socket by request identity; no membership SQL/business.',
'backend/go/gateway/http.go':'Gateway startup subscribes and flushes NATS or fails; canonical revocation consumer and per-user fanout; public /v1 reverse proxy to Core. Existing nonbusiness infra upgrade probe. No session writes, Core import or plugin execution.',
'backend/go/gateway/session.go':'Readonly authoritative slot and auxiliary client-type lookup; non-NoRows returned as actual fault. revocationReason defaults REVOKED on unavailable/unrecognized authority but closes/revokes connection; cannot claim LOGOUT/REPLACED without recorded matching identity. Appropriate conservative safety state under AUF-I-002/004.',
'backend/go/shared/config.go':'Readonly config/credential loading returns external failures; trailing data/incomplete config/credential minimum explicit failure. No full Auth or business. Readonly close error has no mutation/commit or successful persistence claim.',
'backend/go/shared/infra.go':'Existing nonbusiness health role text and 405; failed response write means external health probe fails, no persistent effects.',
'backend/go/shared/security.go':'Only token/crypto/UUID primitives and transport types. Parse explicit malformed/signature/expiry rejection; no DB writes/auth workflows. Random failures returned; callers check. HMAC writers cannot fail by their concrete standard-library implementation.',
'backend/go/main.go':'Only config/dependency connect/Ping/role handler assembly; root imports service minimal starts. Existing startup faults fatal sanitized text; relay unknown error fatal, known parent cancel expected retirement. PostgreSQL/NATS closure after process retirement; no business routes or transaction.',
'backend/go/plugin-host/http.go':'Health-only nonbusiness placeholder; no S4 WASM/query/action behavior or runtime/dependency speculation.',
'backend/java/InfraPlaceholder.java':'Full class read. Bounded SRC-06 socket/health/upgrade skeleton only. accept outside per-peer IOException recovery. Malformed request explicitly IOException; accepted peer timeout/truncation/write/close failure closes peer via resource and logs sanitized class then listener can accept next peer. Runtime/algorithm exceptions escape main, listener closed. No business activation.',
'backend/go/Dockerfile':'Existing Go isolated build/image and role entrypoint; unchanged dependencies/runtime.',
'backend/java/Dockerfile':'Existing javac/runtime class entrypoint bounded skeleton; no new framework.',
'backend/go/config.example.json':'Role connection and credential-file names only; no credential plaintext/token or speculative configuration.',
'backend/go/go.mod':'Existing approved Go pgx/NATS/gorilla/bcrypt supporting runtime; no added dependency or coupling.',
'backend/go/go.sum':'Read complete dependency checksum manifest; no runtime handlers and unchanged task delta.'
}
inv=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-outbox-mixed/production-hashes.json').read_text())
coverage=[]
for x in inv:
 p=x['path']
 if not (p.startswith('backend/') or p.startswith('plugins/') or p.startswith('clients/shared/plugin-sdk/')):continue
 b=(R/p).read_bytes();assert h(b)==x['sha256'],p
 n=notes.get(p,'Byte-read empty placeholder only; no executable handlers/imports/fallbacks.');assert p in notes or p.endswith('.gitkeep'),p
 coverage.append(dict(path=p,sha256=h(b),candidate_sha=sha,responsibility=n,inspection='full source semantic read' if p in notes else 'empty placeholder byte read',result='NO_ACTIONABLE_FINDING'))
grounds={
'RH001':('Aborted new session transaction','Frozen4.1 AUF-I-001/002','Rollback closes uncommitted slot+outbox; named original error remains; pgx failed rollback retires underlying connection.'),
'RH002':('Refresh query/update/commit failure','Frozen4.1/7.1 credential rotation atomicity','Rollback uncommitted refresh; response fails, no successful token rotation claim.'),
'RH003':('Logout/revocation transaction fails','AUF-D-008 and AUF-I-004','Rollback partial slot/revocation/outbox; original error failed response.'),
'RH004':('Send authorization/query/insert/commit failure','MSG-I-001/002/003','Rollback all uncommitted seq/message/outbox; uncertain commit preserves original plus uncertainty; no committed ACK.'),
'RH005':('Outbox scan/publish/flush/update/commit failure','Frozen5.2 MSG-D-006','Rollback publication markers; retry only actual known transport, otherwise explicit dispatcher failure.'),
'RH006':('Friend row iteration completion/error','AUF-A-004/005 and standard pgx rows lifecycle','Close releases rows; final rows.Err checked before success; query/scan errors failed response.'),
'RH007':('Friend transaction partial write/fault','AUF-I-005/006','Rollback friendship/direct/member/sync/outbox mutation; error response.'),
'RH008':('Optional fraction regexp syntax','Canonical11.5 exact integral JSON inputs','Nonexecutable regexp syntax, no catch/default or recovery.'),
'RH009':('Optional exponent regexp syntax','Canonical11.5 exact integral JSON inputs','Nonexecutable regexp syntax, no catch/default or recovery.'),
'RH010':('User Sync query/decode/commit fault','Frozen11.5 stable committed metadata page','Rollback read transaction; no successful page/cursor advancement; authoritative bug panic.'),
'RH011':('Conversation Sync read/commit fault','SP-I-001 Frozen11.5','Rollback read transaction; no page/gap advancement; authoritative gap panic.'),
'RH012':('Private history read fails','MSG-I-004/006 authorized history','Rollback read lock transaction; no fabricated empty page.'),
'RH013':('WebSocket close during retirement','AUF-I-004 and MSG-D-006','done closes exactly once; underlying net close already retired; no reconnection success claim.'),
'RH014':('Revocation frame cannot write','AUF-I-004','send closes failed socket; revoke additionally closes it and removes registry; no valid connection survives.'),
'RH015':('Prebind denial ACK cannot write','AUF-I-003','send closes failed socket; caller returns and deferred close; never binds.'),
'RH016':('Auth denial ACK cannot write','AUF-I-003','send closes failed socket; serve returns; no auth success.'),
'RH017':('Private send preparation denial cannot write','WSS MessageError MESSAGE_COMMIT_FAILED, MSG-I-002','send closes failed socket; preparation had no Core commit; no success ACK.'),
'RH018':('Private HTTP response body closes','MSG-D-006 and MSG-I-002 uncertain submission','Read-only body release; missing/invalid/non200 result retains uncertainty and never fabricates committed outcome.'),
'RH019':('Canonical ACK socket write fails','MSG-I-002 and SP-D-003','send closes failed connection; client timeout/retry/Sync converges same request identity.'),
'RH020':('Realtime fanout write fails','MSG-D-006 Sync completeness','send closes failed socket; durable message remains in Core; reconnect/Sync repairs delivery.'),
'RH021':('Process pool retirement','Frozen3.3 root resource assembly','pgxpool.Close has no error result; only lifecycle closure; no operation fallback.'),
'RH022':('Process NATS retirement','Frozen3.3/5.2','NATS Close has no error result; only lifecycle closure; no durable message loss claim.'),
'RH023':('Readonly configuration close','Frozen3.3 runtime config and7.4 privacy','No write/commit result is claimed, file resources closed after successful read or explicit load failure.'),
'RH024':('Accepted peer IOException','SRC-06 transport skeleton only','Accepted socket try-resource closes peer; failed request ends, listener proceeds; accept/unknown runtime/algorithm failures escape.'),
'RH306':('Joined/multiple actual pgx transport roots','Frozen5.2 repeatable Outbox anderror-handling.md','Each joined branch independently known or entire original returns. Mixed ConnectError/network/XX000 returns all roots; all-network retry next existing tick.'),
}
nav=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-outbox-mixed/current-navigation.json').read_text())['records']
ret=[]
for x in nav:
 if not x['path'].startswith('backend/'):continue
 fault,authority,recovery=grounds[x['original_id']]
 lines=(R/x['path']).read_text().splitlines();assert lines[x['current_line']-1]==x['current_source']
 ret.append(dict(composite_key=x['composite_key'],id=x['original_id'],path=x['path'],line=x['current_line'],source=x['current_source'],input_sha256=h((R/x['path']).read_bytes()),specific_fault=fault,current_authority=authority,actual_recovery_or_failure=recovery,independent_decision='RETAINED_WITH_PRESENT_GROUND' if x['executable'] else 'NONEXECUTABLE_NAVIGATION',reviewer='/root/regular_review_26a2941/server_semantics',candidate_sha=sha))
assert len(ret)==25
functions=[]
for p,n in notes.items():
 if not p.endswith(('.go','.java')):continue
 text=(R/p).read_text(); names=[(i,line.strip()) for i,line in enumerate(text.splitlines(),1) if line.startswith('func ') or 'static void handle(' in line or 'static void main(' in line]
 for i,name in names:functions.append(dict(path=p,line=i,handler=name,read_evidence=n,result='NO_ACTIONABLE_FINDING'))
report=dict(role='regular review readonly server helper',identity='/root/regular_review_26a2941/server_semantics',fresh_context=True,implemented_or_fixed=False,specialized_same_sha_eligible=False,candidate_sha=sha,baseline_sha='35bd6f5f1091503f95a0282f730ed04233b0b6ea',branch=git('branch','--show-current'),git_root=git('rev-parse','--show-toplevel'),clean_status=git('status','--porcelain'),canonical_sha=h((R/'spec/architecture/frozen-architecture.md').read_bytes()),result='NO_ACTIONABLE_SERVER_FINDING',findings=[],coverage_count=len(coverage),retained_navigation_count=len(ret),handler_count=len(functions),minimality='Existing responsibilities only; one local recursive predicate required by actual pgx multiaddress joined roots. No new dependency/public symbol/config/table/worker/retry scheme. Existing cleanup, atomicity, unknown commit, conservative session retirement retained.',limitations=['Parent runs fresh minimum architecture baseline and Go tests; helper does not claim own test execution or hosted acceptance.','Scope all production backend/plugin placeholders; client logic reviewed by other helpers.','Initial mandatory startup reads occurred before Recorder; prospective_resume trace incomplete. First direct Python command used legacy Python2 and failed; no hidden successful outcome.','Registered prompt is honest delegation summary, not full original Human prompt; original parent prompt not claimed captured.','Some commands after Recorder start were direct source inspections, explicitly incomplete trace.','PowerShell5 authority read briefly produced mojibake; ADR0008 and operative canonical sections reread using UTF8 Python.','Artifact generation hashes current files and does not substitute semantic proof; exact source manually inspected before authoring these decisions.'])
for name,data in [('coverage.json',coverage),('retained-sites.json',ret),('handler-reads.json',functions),('report.json',report)]:
 (O/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps(dict(coverage=len(coverage),sites=len(ret),handlers=len(functions),result=report['result'])))
