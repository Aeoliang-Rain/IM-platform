# First Go group slice — local facts only

LOOP1-GROUP-001 remains active/group_product, S2 OPEN. Sole writer `/root/group_product_impl_r2` used assigned `H:/.codex/worktrees/group/IM-platform`, branch `task/LOOP1-GROUP-001`, accepted parent/main `79d39dcbd045597ccc5abd459edd388eed269254`. This is local Go verification, not full G01..G09, independent Review, Architect, hosted CI or product integration/synchronization acceptance. The already accepted first contract's five unchanged portable public originals are in `../activation/`; its relocation map explains historical paths. External coordinator binding SHA702d4f2ac7fc30eed209693defc411e7ac7fe9e3884ce3084e1a856532a3a210 remains external.

## Current implementation

Core serves CREATE `POST /v1/groups` with original 201, ADD `POST /v1/groups/{conversationId}/members` with original 200, and joined DIRECT+GROUP `GET /v1/conversations` with 200. Exact memberUserIds, canonical transport/body/query precedence, request correlation and no-store follow the frozen contract. Current Session, active GROUP/member and every target's friendship to the actor precede receipt replay/conflict. Original results/timestamps never derive from later membership. Receipt-less legacy CREATE fails retaining the missing persisted-original-result cause; existing legacy read/send and authorized ADD remain compatible.

Users lock in ascending UUID order with FOR NO KEY UPDATE, followed by Session/member/conversation duties and revalidation. A newly observed member outside the initial set triggers an unwritten rollback and sorted retry. These are required by current ADD concurrency/UserSync, while preserving existing send/logout FK KEY SHARE. Actual PostgreSQL barriers verified both lock graphs without editing Auth/Message. Business, immutable receipt and one conversation.changed/membership.changed pair with matching Outbox per current recipient commit atomically. Group revision uses existing monotonic user_sync_events.cursor_id; existing friend revision1 remains unchanged. Replay/no-op emits no metadata pair.

Snapshot rows contain only authorized active memberships and PublicUser identity, ordered by the full exclusive conversation/member tuple with true lookahead and empty terminal continuation. A page is authoritative; a whole pagination sequence is not represented as a global snapshot. The required independent from-start scan recovers lower tuples inserted behind a saved cursor.

Unknown database/commit/invariant/cancellation/response IO and cleanup errors retain their causes and fail. Only direct canonical rejections project catalog responses. A known rejection joined with actual rollback failure is not projected as 4xx. No new production hook, dependency, schema, native responsibility or generic error framework was added.

## Final source and verification

All paths below are under backend/go. Raw SHA256:

| File | SHA256 |
| --- | --- |
| core/group.go | e7b837c92b09fcab53cebf7295bcd787d1e1cb668a3ed7a152cac07cc1701f83 |
| core/group_test.go | 19a17382683320d7ad72d1687806a60c336a6373cb95e8bc5587d8a2839d45ef |
| core/http.go | f63b0772352e4ad105d4bb8123acfc692df0660ed23971a46552b4190fa589bd |
| core/social.go | 8d94af6d02c86b6995cd837eb0f12ce14c8dca0f3bfb16d7468b94d74141b65c |

Final commands, cwd backend/go, DB_TEST_ENABLE=1 and controlled own PG/NATS:

- `go test -count=1 -timeout=5m -json ./...`: exit0, native21.375s, 71 main methods/250 including subtests PASS, zero failures/skips.
- `go test -race -count=1 -timeout=5m -json ./...`: exit0, native92.156s, same71/250 PASS, zero failures/skips. Existing installed C toolchain was actually used; nothing installed.

There are14 TestGroup main methods including the existing500-member message method;13 are new,55 group results include subtests. Coverage includes exact HTTP CREATE201/ADD200/GET200 and replay bodies, boundaries/current authorization, changing-membership original results/no-op/scopes, identity and membership concurrency, nonfriend identity, revisions/Sync-Outbox identity, all CREATE/ADD write points, real deferred commit rejection/wait, Session changes during locks, logout/send FK compatibility, new-member lock-set retry and UserSync committed prefix.

The test-only existing pgx BuildFrontend IO device preserves its TLS negotiation boundary/SASL and driver. It forwards actual COMMIT and observes the real backend CommandComplete COMMIT. Before releasing EOF, an independent connection verifies the durable receipt,2 memberships,4 Sync and4 Outbox rows. The caller fails retaining unexpected EOF; normal original-request retry returns the exact durable original result without new effects. No backend reply or Commit is fabricated. Separate real httptest connections drop POST before dispatch and after real handler commit. A207-member group built with <=100-target operations verifies limit100/1, short terminal page, tuple ordering, active filtering and lower-tuple insertion recovered from start. Actual owned pgx connection closure preserves both primary rejection and real rollback `conn closed` cause.

Thirteen post-source authority/contract/Development commands all exit0: Frozen, planning, all-scope architecture,88 architecture tests(one existing skip),35 CI tests(four existing skips), group verifier,29 group-contract methods(zero skip), Auth, Sync verifier/four methods, WSS, Plugin and Development. Static/control skips are separate from the zero-skip Go runtime suite. Final metadata-only controls and clean committed Acceptance are separate final handoff records. Exact commands/exits/elapsed/raw hashes are in verification-summary.json and local-originals.zip, with package-manifest.json.

## Runtime ownership and preserved failures

The execution owner strictly qualified actual127.0.0.1:63830/group_contract_20261018/group_contract_fixture/PG16.15, normalized data-v2 and root PID49572. PGPASSFILE was passed only by granted path to libpq/pgx; agent/helper never read/printed/copied its contents. Inherited PG*/DATABASE_URL were cleared; child PGOPTIONS selected only new own schema group_product_r2_e79be46910ac4016 without public fallback. Canonical runner status/up/status applied the unchanged0001+0002.

Own schema is dropped; non-own schema names/owners exactly match before and root server/PID remains qualified. Immediately before drop users/sessions/conversations/members/receipts/userSync/messages/testfunctions were0. Seven own-schema Outbox rows remained after repeated whole suites; origin unavailable, not attributed to old tests. They were removed with own schema. This report does not claim every table was0.

NATS used existing repo nats:2.10-alpine, a new owner-labelled container and dynamic127.0.0.1-only port after full existing container/volume inventory. Initial exact full-State cleanup comparison FAIL stays FAIL with raw output/diff. Differences were one container's3 mount records reordered plus advancing Health.Log Start/End. A separately named comparison retains complete mount records as sets, every other State/health result field and all volumes; it PASSed. Exact own ID/name/image/label/loopbackport was requalified, then only own container removed. No other resource/daemon/root PG was changed.

Default sandbox format/cache writes failed; authorized escalated retries succeeded. A new rollback-fault fixture omitted the existing GROUP request CHECK field, failed, then only fixture corrected. Required current.md delete/recreate was rejected by automatic approval review; completed edit is in-place Update and current remains present. One scope helper initially compared Windows path text to forward-slash text and failed; corrected representation retains the exact unique Task requirement. A first report tool could not create parent directories; only authorized new evidence directory was then explicitly created. All failures remain recorded.

Recorder R-GROUP-PRODUCT-R2-GO-20261020 is prospective but explicitly partial: assignment summary/excerpt, direct reads/tool mutations/helper authoring/communication/final packaging have declared gaps. It will honestly finish FAIL and be directly validated; final research and commit/clean receipts are separate handoff evidence. Trace is never edited. The next phase continues registered shared/Web/Desktop/Android work, real installed Windows Tauri/emulator entries, complete G01..G09 and old regressions, screenshots/Architect and final fresh dual-review/hosted/protected/actual-main/safe synchronization chain.

## Actual closure and handoff

Source commit is e145cc1b8f6f1304da86f3da4c41fbdc2ed60569, parent79/tree dd126ea6448cc721f4b976f9cb58a36587ce32a0. Its clean committed Control Acceptance exited0/native28.718s with status_entries0. Recorder actually finished FAIL/exit0, direct validate0,139events/67 command starts/67 finishes/0 unmatched. The preceding future-tense paragraph describes report creation before closure. The declared postclosure tail is one metadata/evidence handoff commit, final Control and external sealed receipt, captured separately rather than added to a finished trace.

The post-metadata Control generated one ci/check_s2_planning.cpython-313.pyc absent from the initial inventory, within its command interval, through the existing nested Frozen launcher without-B. Initial primary Python3.12 comparisons to that3.13 cache failed and are retained. The actual existing Control Python3.13.14 then verified matching magic/header and exact code-object equality with unchanged source. Original pyc was preserved outside the repository; only that qualified generated file and empty directory were removed. No CI source/cache was staged. Later Control uses only child PYTHONDONTWRITEBYTECODE=1. Handoff JSON/late ZIP/manifest bind this provenance, all probe failures, complete closed research trace and source-commit recovery. Final actual HEAD/ancestry/clean Control and final artifact bindings are in the external sealed final receipt for root to archive at the next client commit; no recursive SHA-chasing commits.
