from pathlib import Path
import json,hashlib,subprocess
R=Path('H:/.codex/worktrees/err/IM-platform')
O=Path('C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/error-audit-a292/server')
def write(n,x): (O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True).strip()
i=json.loads((R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/production-inventory.json').read_text())
head=git('rev-parse','HEAD');assert head=='a292f516f622651ae62595163e479c13fff78c1d'
assert git('rev-parse','--show-toplevel').replace('\\','/')==str(R).replace('\\','/')
assert not git('status','--porcelain')
files=[f for f in i['files'] if f['path'].startswith(('backend/','deploy/','contracts/database/'))];assert len(files)==36
coverage=[]
for f in files:
 p=f['path'];b=(R/p).read_bytes();h=sha(b);assert h==f['sha256'],p
 if p.endswith('.gitkeep'): result='Exact placeholder bytes inspected; no executable handling or implemented business.'
 elif p.endswith('.go'):result='Full file read with call-chain/import inspection. Core owns transactions and durable ACK; Gateway owns validation/proxy/connection retirement; shared contains support; main assembles roles. Errors fail via return, safe failed response or panic. No speculative future mechanism.'
 elif p.endswith('.java'): result='Full transport skeleton read: accept outside IOException catch, try-with-resources per socket, IOException failure retires request; unchecked failure propagates. Compiled actual handle fault controls independently executed.'
 elif p.endswith('migrate.py'):result='Full executable migration runner read: ON_ERROR_STOP subprocess failure raises; atomic transaction and advisory lock; explicit down authorization; caught RuntimeError prints failure and exits1; other errors propagate. No false migration success.'
 elif p.endswith('.sql'):result='Full canonical SQL read only: checks/foreign keys/uniques/triggers reject violation, atomic migration runner owns commit. No exception suppression; no schema or write change authorized.'
 else:result='Full declaration/configuration/document text read, build and role wiring reconciled: build failure exits Docker stage; compose requires successful migration and healthy dependencies; TLS only publishes proxy; no hidden runtime fallback.'
 coverage.append(dict(path=p,sha256=h,bytes=len(b),inventory_sha256=f['sha256'],full_read=True,result=result,issues=[]))
write('coverage.json',dict(candidate=head,baseline=i['baseline'],branch=git('branch','--show-current'),git_root=git('rev-parse','--show-toplevel'),clean=True,file_count=36,files=coverage))
G={
'RH001':('newSession abort/commit rollback cleanup','Frozen4.1/7.3 AUF-I-001/002 atomic slot replacement','Uncommitted slot/revocation changes roll back; committed transaction is already closed. pgx rollback failure closes connection rather than publishing success; original named err preserved.'),
'RH002':('refresh transaction abort/closed transaction','Frozen7.1 refresh rotation AUF-D-004','Token rotation cannot publish success until Commit; rollback releases pending state and connection; primary failure still writeError.'),
'RH003':('logout transaction failure/closed transaction','AUF-D-008/AUF-I-006 Frozen7.1','Session/revocation event remain one transaction; failed logout returns failure, successful204 requires commit; deferred rollback cannot undo committed success.'),
'RH004':('send atomic transaction fails or uncertain commit','MSG-I-002/003 Frozen5.1','No success ACK before commit; rollback clears uncommitted sequence/message/outbox; unknown commit retains uncertainty and original root.'),
'RH005':('Outbox publish/scan/flush/update/commit batch failure','MSG-D-006 Frozen5.2','Failed batch returns error, deferred rollback keeps unpublished event replayable; confirmed network failures retry existing tick. Unknown failure exits dispatcher/process.'),
'RH006':('friend query iteration failure/normal completion','AUF-D-005/006 and pgx row ownership','Rows close; Scan and rows.Err separately checked before successful list. Failure never converted to empty friends.'),
'RH007':('friend/direct/member/event transaction failure','AUF-I-005/006 Frozen4.2','Deferred rollback clears partial state; error response retained; commit precedes201/200.'),
'RH008':('Regexp optional fraction syntax, inventory navigation false-positive','Sync contract mathematical integer acceptance','No catch/default behavior: ? denotes optional regexp group in declaration. Same line also indexed by RH009; retain distinct original record identity.'),
'RH009':('Regexp optional exponent syntax, inventory navigation false-positive','Sync contract mathematical integer acceptance','No catch/default behavior: ? denotes optional regexp group in declaration; not a swallowed exception.'),
'RH010':('user Sync read transaction failure/normal commit','ADR0008 Frozen11.5 committed prefix/auth locks','Rollback releases locks, failed query/decode never yields success page or nextCursor; invariant corruption panics; rows are closed/transaction retirement closes them on panic.'),
'RH011':('conversation Sync read failure/normal commit','ADR0008 Frozen11.5 SP-I-001/004','Rollback releases session/member locks; no successful page on Scan/iteration/commit error; authoritative gaps panic rather than emit partial history.'),
'RH012':('private history read transaction failure','MSG-I-006 SP-I-001 Frozen5/11','Rollback releases read locks; authorizeMessage and all row/commit errors fail; successful page requires commit.'),
'RH013':('websocket close after read/write/revoke retirement','Frozen7.2 active connection lifecycle','done closed exactly once before raw Close. Gorilla Close error cannot reopen connection or yield ACK; caller is already retired and no operation resumes success.'),
'RH014':('session.revoked frame write fails','AUF-I-004 Frozen7.2','send itself closes done/socket on WriteJSON failure; unconditional close then remains idempotent; no active revoked connection survives.'),
'RH015':('prebind AUTH_REQUIRED rejection write fails','AUF-I-003 MSG-I-006','send failure retires connection; serve returns in either result; unauthenticated send cannot reach Core or persist.'),
'RH016':('auth rejection write fails','Frozen7.2 binding rejection','send failure retires; every caller returns after rejection; no transition to bound/normal success.'),
'RH017':('private forwarding preparation rejection write fails','MSG-I-002 canonical rejected ACK no persistence','JSON encoding/request construction occurs before Core transport; rejection represents no committed Core operation. send failure closes, so not a successful ACK.'),
'RH018':('private HTTP response body close after decoding or bad response','MSG-I-002 uncertainty protection; net/http body resource','Read/decode/status failure leaves origin uncertain and emits no success/rejection; Close retires response and cannot turn failed decode into ACK. Read-only response close errors do not establish commit outcome.'),
'RH019':('decoded canonical ACK socket write fails','MSG-I-002 and Frozen5.1','Core result already obtained; send closes failed connection; client timeout/retry/Sync convergence remains required, no false delivered success.'),
'RH020':('local fanout websocket write fails','MSG-D-006/007 Frozen5.2','send retires failed socket; other independent recipients continue, failed delivery is recoverable via existing Sync. No persistence duplicated.'),
'RH021':('process database pool retirement','SRC-02 root resource ownership','Close has no error return; normal return cleanup closes pool. Fatal exit terminates process and OS releases resources; no live failed process pretends ready.'),
'RH022':('process NATS connection retirement','SRC-02 and Frozen5.2','Close has no error return, connection retired on normal return. Fatal exits terminate process; persistent Outbox remains source for next start.'),
'RH023':('readonly runtime configuration file close','SRC-03 config support','Close of already consumed readonly descriptor cannot manufacture bytes or change decoded config; open/read/decode/credential/parse failures already return explicit error.'),
'RH024':('malformed/truncated/timed-out request socket IOException','SRC-06 exact Java non-business transport skeleton','Accepted socket try-with-resources closes before logging and next request; IOException is failed operation, no fake reply. accept listener failure and unchecked internal exceptions lie outside catch and propagate.'),
'RH293':('migration psql/checksum/concurrency/destructive guard RuntimeError','Frozen11.4/17 migration atomicity','psql ON_ERROR_STOP raises, main prints explicit error and returns1; SQL connection exit rolls back uncommitted changes, startup gated service_completed_successfully. Other exception classes propagate.'),
}
records=[]
for ordinal,s in enumerate(i['retained_sites'],1):
 if not s['path'].startswith(('backend/','deploy/','contracts/database/')):continue
 lines=(R/s['path']).read_text().splitlines();matches=[n+1 for n,l in enumerate(lines) if s['source'].strip() in l]
 assert matches,(s['id'],s['path']);line=min(matches,key=lambda n:abs(n-s['line']));fault,req,rest=G[s['id']]
 records.append(dict(composite_key=f"{ordinal}|{s['path']}|{s['id']}",original_ordinal=ordinal,original_id=s['id'],path=s['path'],original_line=s['line'],original_column=s['column'],current_line=line,current_column=s['column'],current_source=lines[line-1],source_sha256=sha((R/s['path']).read_bytes()),executable=s['id'] not in ('RH008','RH009'),specific_fault=fault,present_requirement=req,actual_restored_or_failed_state=rest,decision='RETAINED_WITH_PRESENT_GROUND' if s['id'] not in ('RH008','RH009') else 'NAVIGATION_NON_HANDLING',issues=[]))
assert len(records)==25
write('retained-grounds.json',dict(candidate=head,records_count=25,records=records))
write('navigation-addendum.json',dict(candidate=head,observed_paths=[
 dict(path='backend/go/core/auth.go',sites='authenticate two secondary lookups; login bcrypt; decode/writeJSON/writeError; search ErrNoRows',assessment='Only ErrNoRows and actual bcrypt mismatch project known business outcomes. Unknown lookup/hash errors propagate to failed safe response. JSON encode/entropy panic. Search no-row is true absence; DB failure is never empty result.'),
 dict(path='backend/go/core/message.go',sites='newMessageCommitError/sendMessage/commitMessage',assessment='Only confirmed rollback or testedP0001 permits known failed commit. Unknown commit is multi-%w preserving uncertainty marker and original error;503 no rejection. Precommit DB/entropy/internal failure has failed ack, not success; required protocol projection preserves no committed message meaning.'),
 dict(path='backend/go/core/outbox.go',sites='RelaySessionRevocations/relaySessionBatch',assessment='Only NATS connection/disconnect/timeout, deadline or net.Error retry pending batch. Every other error returns and main fatal exits. No log-only continuation of programming error; no new retry abstraction.'),
 dict(path='backend/go/core/sync.go',sites='syncFailure/syncInput/syncInteger/syncJSONNumber/authoritative scans',assessment='Unknown servers return non2xx503 per ADR0008. Malformed external bodies reject400; panic on authoritative invalid metadata/gaps. Number saturation is exact min(limit,100)/afterSeq cap, not fake empty data. peek end sentinel is followed by outer ReadByte preserving nonEOF input failure.'),
 dict(path='backend/go/gateway/gateway.go',sites='serve/watch/forward/fanout',assessment='Malformed external frames close; unknown bind error closes without invalid-token classification. watch failures retire live binding with conservativeREVOKED, not inventedLOGOUT/REPLACED; db authority checked on subsequent bind. Forward transport/malformed Core responses preserve uncertain origin and suppress rejection/ACK. fanout rejects malformed external bus bytes without declaring delivery success, Sync supplies durable completeness.'),
 dict(path='backend/go/gateway/session.go',sites='authenticate/revocationReason',assessment='Unknown lookup propagates; only exact current bound-user/session committed revocation suppliesLOGOUT/REPLACED. Missing/query/error/unknown reason uses conservative local retirement; no fabricated business reason.'),
 dict(path='backend/go/main.go',sites='configuration/dependency/dispatcher/listener Fatal',assessment='Fatal generic text intentionally safe projections avoid secret material; process exits1 rather than logs-and-continues. Source of failure remains operation boundary; no successful startup fallback.'),
 dict(path='backend/go/shared/security.go',sites='UUID/RandomToken/Sign/Parse',assessment='Entropy/sign errors return; unknown internal callbacks not enclosed by catch. Malformed/tampered/expired external token gives explicit known protocol auth rejection; HMAC Write cannot fail by library contract.'),
 dict(path='backend/java/InfraPlaceholder.java',sites='main/handle',assessment='IOException catch only surrounds accepted request. Socket failure cleanup complete; listener accept outside. Runtime/crypto/internal exceptions propagate. Java remains infra skeleton with no S3 business activation.')]))
write('prior-binding.json',dict(candidate=head,server_diff_since_initial=git('diff','--name-only','7700645..HEAD','--','backend/go','backend/java','deploy','contracts/database'),qualification='No server product source change in range. Prior controlled PG/NATS is historical corroboration only, not fresh runtime/independent acceptance. Current suite uses DB_TEST_ENABLE unset; every SKIP is unavailable, not PASS. friend403 remains DEFERRED_BY_HUMAN.'))
print('PASS independent server coverage36 + original composite25 mappings/hash/root/clean assertions; no source findings')
