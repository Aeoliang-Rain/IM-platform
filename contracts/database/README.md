# Canonical PostgreSQL schema

`migrations/0001_initial.up.sql` plus additive `0002_group_operations.up.sql` are the ordered shared schema for Go and Java profiles.
Run the migration before application startup, using a normal PostgreSQL `psql`
client and libpq connection settings (`PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`,
and secure credential handling outside the command line):

```text
python3 contracts/database/migrate.py status
python3 contracts/database/migrate.py up
python3 contracts/database/migrate.py down --allow-data-loss
```

The runner applies each SQL file and its checksum ledger entry in one transaction
under a PostgreSQL advisory transaction lock. Applied SQL is immutable. Each down
invocation rolls back only the highest applied version and requires explicit data-loss acknowledgement;
release rollback still requires a backup and compatibility assessment.

`sessions` is one row per `(user_id, client_type)` slot. A replacement login must
rotate `session_id`, increment `session_epoch`, and revoke the old session in one
transaction. The server must validate both session ID and epoch against PostgreSQL.
The database constraints reject duplicate normalized friendship and DIRECT pairs,
request IDs and sequence numbers within a Conversation, and duplicate logical
`message.created` outbox events. Message authorization, sequence allocation,
matching Outbox insertion, friend/direct/membership/sync transaction assembly, and
post-commit ACK remain application transaction obligations. A unique constraint
alone cannot prove those multi-row operations occurred atomically.

With a disposable PostgreSQL database configured through libpq variables, run
`python3 -m unittest discover -s tests/database -v`. The integration test uses
an isolated temporary schema and exercises forward, uniqueness, and rollback.

## 0002 group operation receipts

The standalone runner is the only DDL entrypoint. `up` applies the entire pending
ordered prefix (empty→0001→0002 or existing0001→0002) and ledger entries in one
transaction under the original advisory transaction lock481233001. `status`
prints each version and rejects unknown/gapped ledger or checksum mismatch;
`up`/`down` validate the same state before work and recheck the complete observed
prefix/digests under the lock. A stale concurrent invocation fails explicitly
without effects; rerunning inspects current state and is reentrant. PostgreSQL or
internal failures propagate nonzero, never empty state or success.0001 SQL bytes
and its historical SHA256 of UTF8 universal-newline text remain unchanged.

`group_operation_receipts` stores only current group CREATE/ADD original targets
and committed results: actor, type, request, conversation, sorted distinct UUID
target array, sorted distinct actual-added array and original operation record
timestamp. CREATE(actor,request) is unique across conversations; ADD identity is
(actor,conversation,request), separated by operation. Existing conversation
create uniqueness and membership PK remain. Original create targets cannot be
reconstructed after later additions. CREATE result includes creator+targets;
ADD result contains only actual additions, including an empty array for an
already-member operation. Targets exclude actor and contain1..100 raw-normalized
distinct IDs;100 is an individual HTTP operation transport boundary, not total
group capacity. Array checks retain canonical order/uniqueness and result subset.

Core remains responsible for current authoritative Session/active GROUP/member,
each target's actor friendship even on replay, CREATE conversation identity,
original status/body replay and conflict, and atomic business/receipt/all affected
user Sync+Outbox assembly. Database constraints alone do not prove those rules.
No receipt/table authorizes user queries or changes message ACK/Sync semantics.
The HTTP authority and fixtures are `contracts/http/group.openapi.json` and
`contracts/fixtures/group/`; backend/client implementation follows separate
independent contract acceptance. Existing DIRECT/Auth/WSS/ACK/Sync remain valid.

`down --allow-data-loss` at level0002 drops only the receipt table/helper and
its ledger row, retaining0001 business/group/member/message/Outbox data. A second
explicit down at level0001 retains the historical full schema drop. Re-up after
0002 rollback recreates an empty receipt table; it cannot recover old retry
identities. Production rollback therefore requires stopped group writers,
release compatibility assessment and backup/restore of receipts covering all
outstanding original-request retries. Do not serve new group endpoints across
receipt loss or present rollback as safe transparent retry. Old0001 services and
fixtures continue to work with additive0002 or after0002 rollback. Destructive
release decisions are outside an ordinary application startup.

With real disposable PostgreSQL and libpq configuration, set `DB_TEST_ENABLE=1`
and run `python3 -m unittest discover -s tests/database -p test_migrations.py -v`.
The existing compatibility job executes this suite with PostgreSQL16 and psql;
the Go job independently invokes the same runner `up`. Tests cover empty→0002,
real existing0001 data/ledger upgrade, reentry, mismatch/unknown ledger rejection,
two real runners waiting on the original lock, stale-state failure, pending-batch
rollback, original-result receipts and staged down/re-up plus old fixtures.
Absent PostgreSQL/psql or disabled tests are unexecuted, never migration PASS.

Existing0001 GROUP rows may lack original receipts; no earlier public group-create
HTTP route existed. Their read/send and future authorized ADD compatibility stay
intact. If a CREATE identity already exists without a verifiable original result,
the new POST must fail as a server operation and preserve the missing-result
cause. It cannot prove different targets, return a fabricated409 conflict, guess
the old targets/result, or backfill a success. Unexpected missing new receipts
likewise fail; no legacy-marker/backfill mechanism is added.409 is only for
verified receipt identity with different canonical targets. See positive/negative
contract vectors; actual Core behavior remains a later independently reviewed
product slice.
