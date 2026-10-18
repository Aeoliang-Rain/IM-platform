"""Standalone ordered PostgreSQL migrations via psql/libpq; run before either profile.

up applies all pending versions atomically. down rolls back only the highest
version, with explicit data-loss acknowledgement and release compatibility review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
MIGRATIONS = ROOT / 'migrations'
VERSIONS = ('0001_initial','0002_group_operations')
LOCK = 481233001


def psql(sql: str, *, capture: bool = False) -> str:
    proc = subprocess.run(['psql','-X','-v','ON_ERROR_STOP=1','-q','-A','-t'],
                          input=sql,text=True,capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or f'psql exited {proc.returncode}')
    if not capture and proc.stdout.strip():
        print(proc.stdout.strip())
    return proc.stdout.strip()


def migration_sql(version: str, direction: str) -> str:
    return (MIGRATIONS/f'{version}.{direction}.sql').read_text(encoding='utf8')


def checksum(version: str) -> str:
    # Exactly the historical0001 algorithm: UTF8 text after universal newlines.
    # Raw SQL bytes remain immutable; never substitute raw-byte digest in ledger.
    return hashlib.sha256(migration_sql(version,'up').encode('utf8')).hexdigest()


def applied() -> dict[str,str]:
    exists = psql("SELECT to_regclass('schema_migrations') IS NOT NULL;",capture=True)
    if exists == 'f':
        return {}
    if exists != 't':
        raise RuntimeError('unexpected schema_migrations existence result')
    output = psql("SELECT version || E'\\t' || checksum FROM schema_migrations ORDER BY version;",capture=True)
    known = {}
    for line in output.splitlines():
        version,digest = line.split('\t')
        if version in known:
            raise RuntimeError('duplicate migration ledger version')
        known[version] = digest
    validate_ledger(known)
    return known


def validate_ledger(known: dict[str,str]) -> None:
    if set(known) != set(VERSIONS[:len(known)]):
        raise RuntimeError('migration ledger is not a known ordered prefix')
    for version,digest in known.items():
        if digest != checksum(version):
            raise RuntimeError(f'{version}: applied migration checksum differs from canonical SQL')


def transaction(direction: str, known: dict[str,str]) -> tuple[str,list[str]]:
    validate_ledger(known)
    versions = list(VERSIONS[len(known):]) if direction == 'up' else (list(VERSIONS[len(known)-1:len(known)]) if known else [])
    expected = json.dumps(known,sort_keys=True,separators=(',',':'))
    prelude = (
        'BEGIN;\n'
        f'SELECT pg_advisory_xact_lock({LOCK});\n'
        'CREATE TABLE IF NOT EXISTS schema_migrations ('
        'version text PRIMARY KEY, checksum text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now());\n'
    )
    # Compare all inspected rows/digests again under the same transaction lock.
    # A stale concurrent invocation fails explicitly and changes nothing; a
    # subsequent invocation inspects the actual committed prefix and is reentrant.
    guard = f'''DO $migration_guard$ BEGIN
      IF (SELECT COALESCE(jsonb_object_agg(version,checksum),'{{}}'::jsonb) FROM schema_migrations)
         <> '{expected}'::jsonb THEN
        RAISE EXCEPTION 'migration state changed concurrently';
      END IF;
    END $migration_guard$;
'''
    body = []
    for version in versions:
        body.append(migration_sql(version,direction))
        if direction == 'up':
            body.append(f"INSERT INTO schema_migrations(version,checksum) VALUES ('{version}','{checksum(version)}');")
        else:
            body.append(f"DELETE FROM schema_migrations WHERE version='{version}' AND checksum='{checksum(version)}';")
    return prelude+guard+'\n'.join(body)+'\nCOMMIT;\n',versions


def run(direction: str) -> None:
    if not shutil.which('psql'):
        raise RuntimeError('psql is required; set PGHOST/PGPORT/PGUSER/PGDATABASE as needed')
    known = applied()
    sql,versions = transaction(direction,known)
    if not versions:
        print('migrations: already applied' if direction == 'up' else 'migrations: already rolled back')
        return
    psql(sql)
    for version in versions:
        print(f'{version}: {direction} complete')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('direction',choices=('up','down','status'))
    parser.add_argument('--allow-data-loss',action='store_true',help='required for destructive highest-version rollback')
    args = parser.parse_args()
    try:
        if args.direction == 'down' and not args.allow_data_loss:
            raise RuntimeError('down drops canonical schema/receipts; pass --allow-data-loss only after backup/compatibility review')
        if args.direction == 'status':
            if not shutil.which('psql'):
                raise RuntimeError('psql is required')
            known = applied()
            for version in VERSIONS:
                print(f"{version}: {'applied' if version in known else 'pending'}")
        else:
            run(args.direction)
        return 0
    except RuntimeError as exc:
        # Known external psql/ledger failure exits nonzero with its cause. Parsing
        # and programming errors remain uncaught; no empty/fake-success fallback.
        print(f'migration error: {exc}',file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
