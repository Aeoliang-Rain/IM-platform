from pathlib import Path
import json,hashlib,subprocess
O=Path(__file__).parent;R=Path.cwd();X=O.parents[1]/'fix-cause-read';F=X/'final-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads(F.read_text());assert f['sha']=='a292f516f622651ae62595163e479c13fff78c1d'
checks=[]
for name,h in f['artifact_sha256'].items():
 p=X/name;assert sha(p)==h;checks.append({'path':str(p),'sha256':h})
for name,h in f['source_evidence_sha256'].items():
 p=R/'spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-cause-read'/name;assert sha(p)==h;checks.append({'path':str(p),'sha256':h})
p=X/'research-finished.zip';assert sha(p)==f['recorder']['finished_archive_sha256'];checks.append({'path':str(p),'sha256':sha(p)})
pg=Path('C:/Users/21441/go/pkg/mod/github.com/jackc/pgx/v5@v5.7.6')
files=[]
for rel in ['tx.go','pgxpool/tx.go','conn.go','pgxpool/conn.go']:
 p=pg/rel;files.append({'path':str(p),'sha256':sha(p),'supporting_dependency_source_inspected':True})
assert 'tx.conn.die()' in (pg/'tx.go').read_text();assert "conn.PgConn().TxStatus() != 'I'" in (pg/'pgxpool/conn.go').read_text()
(O/'supplement.json').write_text(json.dumps({'candidate':f['sha'],'fix_final_receipt_sha256':sha(F),'fix_receipt_all_manifest_artifacts_verified':checks,'qualification':'Verified byte seals and exactcandidate binding; Fix evidence local only, not independent acceptance. Prior go stdout stored redacted hash verified, unredacted raw hash not verified or available.','pgx_sources':files,'rollback_analysis':'Actual lockedpgx5.7.6 dbTx.Rollback setsclosed, onerror die() uses cancelledctx to hardclose. poolTx.Rollback always releases then clearsconnection; Conn.Release destroysclosed/busy/nonIdle connection. Commit setsclosed and closeserror+nonidleconn. Deferredrollback cannot lose root by replacement or return uncertainconnection to reusable pool. Readonly rows cleanup failures cannot publish success.'},indent=2)+'\n')
print('PASS pgx supporting source/hash inspected and full25Fix receipt manifest artifact seals verified; no new product verdict')
