---
task_id: LOOP1-ERROR-HANDLING-001
title: 无意义防御与静默兜底治理、全量生产代码纠正
status: done
owner: /root/admin_error_close (accepted-product administrative records)
stage: S2
gate: S2
---

# Goal

落实2026-10-13 Human完整请求：实现 → 常规独立Review → 新独立错误处理审查 → GitHub CI；全量审查当前所有生产代码并按现有权威最小修复，保留有当前依据的必要处理。排除SQLite写入失败和相关草稿保护。

# Inputs

- spec/architecture/README.md -> baseline.md -> frozen-architecture.md（核对SHA；§2.3/§3/§5/§6/§7/§10 SRC-01..07/§11/§12..14/§18/§21）；适用approved ADR-0003/0005/0006/0008/0009/0010/0011/0012。
- spec/governance/minimality.md、execution-boundaries.md、independent-review.md、technology-selection.md；research/README.md与已接受Instrumentation Epoch。
- spec/domain/与spec/invariants/所有当前Auth/Conversation/Messaging/Sync输入；contracts/errors/、http/、websocket/、database/及适用golden fixtures只读。
- spec/acceptance/client-gui.md、client-supplement.md及现有Go、Send、Sync验收。不得削弱既有验收。
- Human原文及Recorder：C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/prompt.txt，P-ERROR-AUDIT-20261013。

# Technology Authorization

沿用canonical与已接受ADR的Go、React/TypeScript、Tauri必要Rust、Android Kotlin/Compose；无新依赖/框架/runtime。该任务不授予新技术或产品架构权限。
client_language: TypeScript
client_language: Kotlin
client_language: Rust
client_framework: React
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

# Dependencies

- LOOP1-CLIENT-I18N-001的产品及行政闭环独立接受、protected integration、actual-main验证与安全同步。新恢复Agent必须核对external final seal再激活；不能仅依done字段。

# Allowed Paths

allowed_paths is a hard write boundary and never an architecture exemption. Java placeholder remains a non-business SRC-06 transport skeleton; exact catch repair only, not S3 activation. Independent authority assessment found the task-scope guard omitted the already accepted exact exception. Add only that exact path to task checking, retain source/business/expiry guards and negative controls.

- `backend/java/InfraPlaceholder.java`
- `ci/check_architecture.py` (exact SRC-06 task-scope exception and current native-language narrow failure boundary only)
- `tests/architecture/test_source_boundaries.py`
- `tests/architecture/test_client_technology.py` (native language boundary positive/negative controls; retain all phase/key/enum/write protections)
- `AGENTS.md`
- `spec/governance/minimality.md`
- `spec/governance/independent-review.md`
- `spec/governance/error-handling.md`
- `spec/tasks/TASK_TEMPLATE.md`
- `spec/handoff/agent-context.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-ERROR-HANDLING-001/**`
- `spec/progress/checkpoints/*error-handling*.md`
- `spec/tasks/backlog/LOOP1-ERROR-HANDLING-001.md`
- `spec/tasks/ready/LOOP1-ERROR-HANDLING-001.md`
- `spec/tasks/active/LOOP1-ERROR-HANDLING-001.md`
- `spec/tasks/review/LOOP1-ERROR-HANDLING-001.md`
- `spec/tasks/done/LOOP1-ERROR-HANDLING-001.md`
- `backend/go/core/auth.go`
- `backend/go/core/http.go`
- `backend/go/core/message.go`
- `backend/go/core/outbox.go`
- `backend/go/core/social.go`
- `backend/go/core/sync.go`
- `backend/go/core/*_test.go`
- `backend/go/gateway/gateway.go`
- `backend/go/gateway/http.go`
- `backend/go/gateway/session.go`
- `backend/go/gateway/*_test.go`
- `backend/go/shared/config.go`
- `backend/go/shared/infra.go`
- `backend/go/shared/security.go`
- `backend/go/shared/*_test.go`
- `backend/go/main.go`
- `backend/go/main_test.go`
- `backend/go/plugin-host/http.go`
- `backend/go/plugin-host/*_test.go`
- `backend/go/tests/**`
- `clients/web/src/application/*.ts`
- `clients/web/src/ui/appearance.ts`
- `clients/web/src/ui/language.ts`
- `clients/web/src/ui/main.tsx`
- `clients/web/src/ui/components/Shell.tsx`
- `clients/web/src/ui/components/Messages.tsx` (current required message content/identity and three-state invariant)
- `clients/web/src/ui/components/FriendsPanel.tsx` (clear prior search completion on query edit only)
- `clients/desktop/src/application/send.ts`
- `clients/desktop/src/application/accountSend.ts`
- `clients/desktop/src/application/sync/*.ts`
- `clients/desktop/src/application/ui/*.ts`
- `clients/desktop/src/ui/components/Messages.tsx` (existing required row content/state/logical identity; no storage/Composer change)
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Messages.kt` (same present invariant responsibility)
- `clients/desktop/src/ui/components/Shell.tsx`
- `clients/desktop/src/ui/components/WindowBar.tsx`
- `clients/desktop/src/ui/main.tsx`
- `clients/desktop/src-tauri/src/desktop_capabilities.rs`
- `clients/desktop/src-tauri/src/lib.rs`
- `clients/desktop/src-tauri/src/main.rs`
- `clients/shared/protocol-sdk/src/send/wire.ts`
- `clients/shared/protocol-sdk/src/sync/*.ts`
- `clients/shared/protocol-sdk/src/storage/repository.ts` (Human exception: ONLY contiguous read mapper, unchanged SQL/all other bytes)
- `clients/mobile/app/src/main/kotlin/im/platform/client/storage/Repository.kt` (Human exception: ONLY contiguous read mapper, unchanged SQL/all other bytes)
- `clients/mobile/app/src/main/kotlin/im/platform/client/send/*.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/sync/*.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Preferences.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/send/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/sync/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/**`
- `tests/clients/send/**`
- `tests/clients/sync/**`
- `tests/clients/web/behavior.mjs`
- `tests/clients/web/regressions.mjs`
- `tests/clients/web/appearance.mjs` (genuine DOMException unavailable and unknown identity proof; preserve all defaults/invalid/save assertions)
- `tests/clients/gui/auth.mjs`
- `tests/clients/gui/desktop_render.mjs`
- `tests/clients/errors/**`
- `tests/clients/i18n/compiled.mjs` (same actual DOMException/unknown identity proof; all compiled resource/default assertions retained)
- `tests/clients/i18n/verify.mjs` (known actual DOMException storage-unavailable fixture and unknown identity proofs only)
- `tests/clients/i18n/scheduling.mjs` (known native capability origin fixture; preserve order/revision assertions)
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Friends.kt` (truthful existing search success/empty/error presentation)

这是一次Human明确要求的全量错误处理审查/纠正；不是跨服务源码搬迁。Core仅Auth/IM/Sync/Outbox，Gateway仅接入/代理/连接，shared仅既有支持，UI/application/native保留现有方向。审查读范围包括git tracked全部生产源码（含无问题文件、SDK/plugin占位及必要native），写范围只允许上述现有职责的错误传播/恢复最小修正和针对性回归测试。范围不足先登记有事实依据的Task scope修订；不得为了方便扩大产品职责。

# Acceptance

- 逐文件生产源码inventory（路径、候选输入hash、职责、检查结果），不能仅grep命中或先前六项；逐项记录位置/触发/掩盖方式/最小修复/测试；每个保留catch/回退注明具体故障、现依据、真实恢复。不凑数量删除有依据保护。
- 治理、Checklist、模板、启动恢复明确未知异常/内部错误/不变量破坏沿正常链传播；操作/测试/进程明确失败，允许必要崩溃；不假成功、空数据或失真分类。不增加通用错误/日志/重试框架。
- 治理包含Human指定四个最小示例和原因；示例语义为TypeScript，原prompt的代码围栏语言不构成新增技术选择。
- pre-CI专项审查由未参与当前候选实现/Fix/常规Review的全新Agent执行；FAIL禁止push/触发候选CI的PR操作；fresh Fix → fresh常规Review → fresh专项Audit循环。任何修复新SHA，两项都审最终SHA；只在提交GitHub CI前执行，不在编辑或命令前重复。证据记录身份/独立性、SHA/branch/range/clean checkout、结果/发现/保留依据/命令和时长。
- 此环节补充canonical Review/CI而不替代；若发现冻结权威冲突先BLOCKED_BY_ARCHITECTURE/最小问题/批准冻结接受后实现，不建立第二权威。
- 必要正常和故障回归、fresh两项Review、exact-head实际必需hosted jobs、protected integration、actual-main及H:/IM-platform安全同步全部完成才done。S2 OPEN，不评估Stage Gate。

# Forbidden

不处理SQLite写入失败及草稿保护；不改storage Repository/schema/native database或Composer；唯一Human例外仅shared/mobile Repository.contiguous两个只读映射：无记录0，现有无效序号明确失败，SQL/Schema/初始化/事务/全部写入/草稿不变；不改Frozen/approved ADR/contracts/security/ACK/compatibility/invariants，不加框架/库/重试机制/未来功能。unknown主仓库work不复制、不覆盖、不提交。没有两个最终SHA审查PASS不得push或创建/更新会触发CI的PR。

# Minimality

删除吞错层，缩小已有已知故障边界，保留原错误与正常传播及有契约依据的恢复；必要的资源清理/回滚/FAILED/协议拒绝/账号隔离/提交未知保护/冻结偏好默认保留。日志后仍错误运行不算恢复。新抽象必须付当前需求依据，默认不用新抽象。

# Verification

- `tools/verify_frozen_architecture.py`; `tools/verify-loop1-ctrl-002.ps1` are the existing executable recovery entry points. No checker exemption beyond the canonical exact Java skeleton.

- Minimum baseline: python -Xutf8 -B tools/verify_frozen_architecture.py；python -Xutf8 -B ci/check_architecture.py --scope all --json；python -Xutf8 -B ci/check_s2_planning.py；bundled pwsh tools/verify-loop1-ctrl-002.ps1 -Mode Development，committed clean候选 -Mode Acceptance。tests/architecture保持实际负例。
- Go cwd backend/go：go test ./...，必要新故障注入test；DB_TEST_ENABLE=1及受控真实PG/NATS环境的适用现有Go tests，skip不计PASS。
- Web python -Xutf8 -B tests/clients/web/verify.py；shared现有build/tests和python -Xutf8 -B tools/verify_client_send.py --scope shared、tools/verify_client_sync.py --scope shared。
- Desktop现有locked TypeScript build与Send/Sync/auth/native renderer测试；需要时python -Xutf8 -B tests/clients/gui/native.py send-desktop、desktop、rust test --locked及package；无编译/运行则PENDING不是PASS。
- Android现有native.py gradle assembleDebug assembleDebugAndroidTest；真实独占Android Studio emulator执行受影响Send/Sync/错误处理instrumentation，绑定实际serial；host/mock不代替。受控fixture/资源/证书清理和原状态恢复必须记录，不读取私人数据、不TLS bypass。
- 新错误处理故障回归命令须在实现handoff登记实际命令/预期/环境：验证原异常传播、未知错误不错误归类、已知传输/协议真实失败恢复、正常行为与账户/ACK/Sync不变量。
- 每次真实命令经Recorder；首轮恢复Go默认cache权限FAIL已保留，专属cache后最低恢复PASS才进入实现。local/Recorder不是接受。

# Evidence

spec/progress/evidence/LOOP1-ERROR-HANDLING-001/，原始研究evidence独立于product acceptance。审查与CI及同步证据精确绑定SHA；旧FAIL不可重写。

# Handoff

Product accepted and safely synchronized: final product63f685d1b959b318f97d804f40af49d61aa3f273, fresh regular /root/regular_review_63f685d PASS (receipt SHA331eff21a35b60653d7618dddf7be51f38ad05d29c2b8043cbba16074b36da3e), different fresh specialist /root/error_audit_63f685d PASS (SHA598f58af70b83763eadb28fbf08a0cdf244cf731426e4b228e3b416470f122b6), exact push38732968440/PR38733066327/main38734397144 each14actual jobs success, protected PR40 main1cab3dc4c9180bfe6a6654fde028a0354faf8a4c, full tree equality and actual safe H:/IM-platform sync six checks PASS. Task moves review->done on these accepted product facts; S2 OPEN, no next task/Gate activation.

Recover from spec/progress/evidence/LOOP1-ERROR-HANDLING-001/accepted-product/acceptance.md and copy-manifest.json: current185/42changed/339(304executable35nonexecuting)/65protected, actual fixes/retained grounds, original two review reports/receipts/commands, three raw CI audits, merged PR/guard/tree/sync and all limitations. SQLite WRITE/draft excluded; only two prior Human contiguous READ mapper spans differ, SQL/all other bytes unchanged. Existing Social403 waived/unexecuted/not canonical PASS; historical native/Android59 graph reuse and specialist98starts97finishes/optional probe FAIL remain qualified. Old FAIL/history/Recorder bytes are not rewritten.

This NEW administrative candidate is administrative_closure_pending: its exact final clean SHA and local committed Acceptance/Recorder/lease RELEASED are bound by C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/admin-error-close/final-receipt.json after commit. Both NEW administrative reviews, applicable exact-head hostedCI, protected integration, actual-mainCI and second safe sync remain PENDING. No recursive own-SHA or future acceptance claim. Coordinator final discovery path C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/final-error-handling-acceptance-seal.json is PENDING, not asserted to exist/pass. Last known good productmain1cab; sole writer /root/admin_error_close owns only permitted metadata/evidence until clean release. Main782unknown/two tracked edits preserved.

# Next Action

Coordinator dispatches NEW regular then DIFFERENT NEW error specialist on SAME final administrative SHA; any Fix repeats both. BothPASS -> applicable exacthead hostedCI -> protectedmerge -> actualmainCI -> second verified safe H:/IM-platformsync -> final external seal. Stop before next task/S2 Gate. Current Task remains this done product record while administrative execution is pending.

# Historical candidate recovery records

Everything below is an immutable prior-candidate snapshot. Its Current/pending/Taskdone forbidden wording applies to its then-unaccepted candidate and does not override the accepted-product discovery above. Original text bytes below are retained intact.

Current sole Fix /root/fix_retirement_gateway; formal e186054 regular FAIL, F1/F2 repair IN_PROGRESS. Current record below and fix-retirement-gateway/handoff.md control this iteration; prior candidate-specific sections are immutable history. FinalSHA reviews/CI/integration/main/sync PENDING.

# Current retirement/Gateway Fix (2026-10-15)

Fresh sole Fix /root/fix_retirement_gateway repairs formal full regular e186054 FAIL F1-DESKTOP-RETIREMENT-CONSUMERS/P2 and F2-GATEWAY-DB-FAILURE-AS-REVOCATION/P2. Exact assigned and Git-resolved root H:/.codex/worktrees/err/IM-platform, branch task/LOOP1-ERROR-HANDLING-001, clean starting e186054d964e11755e7bc48ae71f95d1ea125f2f. Original315+receipt316archive entries verified, immutable receiptSHA0b367d78822ffb0f584b2dbf034d3a6839e6008309ef25b27cf114df0e9ccb6d. Full local repair, per-hunk test correction, authority/minimality, actual commands/limits/failures/isolation/history: spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-retirement-gateway/handoff.md.

Only2 production changes: Workspace mandatory expiry clear/logout settlement and actual same login/restore/refresh/failure-publication observer roots; Gateway safety-watch raw DB error closes without session.revoked, original unknown/internal root escapes real serve goroutine, complete known-network tree closes safely. No new error framework/cache/retry/dependency/contract/security/ACK or session.go change. Current185/339(304exec35nonexec) exact input/navigation;65protected exacte186,63accepted whole+2prior Human contiguous READ exceptions, same SQL/allotherRepo bytes. Android/Auth/Prefs/nativeDB/Repository/schema/init/transactions/all writes/Composer/drafts exacte186. No SQLite WRITE/draft issue work.

Fresh Desktop strictcompile/new39/originalowner12/parallel37/Auth PASS. Actual defaultpgx refused/mixed/internal/closedpool/knownexpiry/writefail PASS; actual disposablePG16/NATS2.10 DB_TEST_ENABLE1 fullGo noSKIP PASS, finalrace/vet PASS. Existing F2 database test now models actual defaultDial unavailable and strictly requiresclose/noJSON/notimeout; genuine expiry/replaced/logout assertions retained, exactactualclosedpoolinternal control retained. New realserve->watch child originalPgError0A000/actualserve stack strictPASS; only ownrandomschema changed, parentcheckedDROP, sharedpublic.sessions untouched, entireownedfixtureproject removed. Android59graph binds qualified prior API34owner10/HTTP32/WSS21, no unnecessary native execution. Finalstatic/Development/clean committedAcceptance/postclean and exact finalSHA in commandhistory/externalsealedreceipt; local/Recorder not acceptance.

Preserved all raw failures including initialcwd/expectedRED/newtestexpectation/live0A000+closedpool/move-crossdrive; exact current limitations/gaps in handoff. Own Recorder R-FIX-RETIREMENT-GATEWAY prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013 relatedR-REGULAR-E186054, incompleteprestart; never edits/finishes old/root runs. Lastaccepted35bd6f5; main782unknown/two tracked edits untouched. Sourcelease exclusive until final clean receipt RELEASED.

Task remains review/S2 OPEN. NEW complete regular185/339/65 then DIFFERENT NEW specialist SAMEfinalcleanSHA PENDING; anyFix repeatsboth. No push/CI-triggeringPR until bothPASS; exacthead hostedrequiredjobs/protectedintegration/actual-main/safe H:/IM-platform sync/mainSHA allPENDING. Taskdone/S2PASS forbidden. New stable localcheckpoint 2026-10-15-error-handling-retirement-gateway-review-candidate.md. Everything below is historical prior-candidate recovery, not current acceptance.

# Current refresh owner recovery (2026-10-15)

Sole source Fix actor /root/recover_refresh_owner_finish recovers disappeared /root/fix_refresh_owner_retirement. Assigned and Git-resolved root H:/.codex/worktrees/err/IM-platform; branch task/LOOP1-ERROR-HANDLING-001; base27cdd93e30a72527bba9f3b0d611b13ba860e92f. Task review/S2 OPEN. Last accepted main35bd6f5f1091503f95a0282f730ed04233b0b6ea. Final newSHA/clean Acceptance/actual Gitblob binding/Recorder structural validation/sourcelease release follow the external recover-refresh-owner-finish/final-receipt.json. These are local candidate evidence, not independent Task/Gate acceptance or main synchronization.

## Actual repairs and minimality

Fresh regular27 FAIL F-EXPIRED-REFRESH-OWNER[P1] proves actual401/session_expired+credential cleanup failure sets Auth.session null while Workspace still owns authenticated state/Sync. Only Desktop ui/workspace.ts and Android ui/WorkspaceViewModel.kt differ from27;183 other production inputs unchanged. Current refresh checks matching operation+Auth owner+generation plus the actual owner.session null fact before retiring that invalidated owner. Detach Auth, existing timer/observers and authenticated projection; close old Sync once, with no second secure credential removal. Stale completion cannot retire the newer operation/generation/account.

Desktop stop now attempts old Sync.close even when actual projection listener throws, retaining one exact root or distinct AggregateError roots; refresh retains both operation/retirement failures and a final busy=false observer failure, including falsy primitives. This small literal capture is necessary because publish may fail before the existing close. Android catches Throwable at the same literal refresh consumer so Error cannot skip actual invalidated-owner retirement; NonCancellable is confined to mandatory stop after the above active/null gate. Cancellation and unknown/Error propagate after cleanup. Distinct retirement failures use standard cause/suppressed; no original failure graph is mutated. Existing known-only failure remains honest unavailable UI, no forged success or category, dependency/framework/retry/logging mechanism added.

Auth/Preferences/Repository/storage/SQL/native DB/schema/init/transactions/all writes/Composer/drafts are unchanged from27.65 protected inputs exact27:63 whole accepted baseline plus two earlier Human contiguous READ-mapper exceptions, with SELECT SQL and all other Repository bytes unchanged. Current Fix makes no additional READ/storage exception. Frozen/approved ADR/contracts/security/ACK/compatibility/invariants unchanged.

## Actual verification and limits

Prior Fix Desktop strict compile, strengthened37 original parallel controls, new12 actual compiled Auth/Workspace controls and original Auth controls are qualified historical reuse, not new runs. Current185 hashes equal the prior post-edit input preview; old command starts24/26/28/46 and exact raw outputs/compiled graph are preserved in prior-fix-partial-raw.zip and rebound by runtime-source-bindings.json. Tests prove exact primary/cleanup roots, falsy/unknown/observer+finally roots, close once/timer stopped/no double-remove, three active gates and normal existing bind. No additional Desktop source change since those observations.

New actual Android build commands use bundled Python tests/clients/gui/native.py gradle --max-workers=1 '-Dorg.gradle.jvmargs=-Xmx768m -XX:ActiveProcessorCount=2 -Dfile.encoding=UTF-8' -Pkotlin.compiler.execution.strategy=in-process -PimSendInstrumentation=<runner> assembleDebug assembleDebugAndroidTest, once for im.platform.client.ui.RefreshOwnerInstrumentation then im.platform.client.ui.ErrorHandlingInstrumentation. Both build while the proven own emulator is closed;14.844s/8.875s exits0, runner-specific APK bytes/SHA and current full main/androidTest/build config input graph preserved externally and in *-apk-seals.json/android-build-inputs.json.

Actual exclusively owned API34 emulator5612 runs `adb -s emulator-5612 shell am instrument -w im.platform.client.test/im.platform.client.ui.RefreshOwnerInstrumentation`: checks=10/result=PASS/sdkInt=34/INSTRUMENTATION_CODE:-1. Nine original owner controls retain all assertions; added tenth verifies actual Auth.refresh normal token rotation with actual secure Preferences, no removal. Current Workspace/Auth/actual Preferences and existing Sync/Send exercise authenticated projection/owner/socket closed once, timer/observers cancelled, known/unknown/Error/close, three stale gates and real cancellation. Controlled HTTP and secure commit producers prove real Android boundary semantics, not default-provider incidence or real server/TLS credential failure.

Same current input graph and separately sealed errors APK runs original ErrorHandlingInstrumentation: result=PASS/httpCleanupChecks=32/wssCleanupChecks=21/sdkInt=34/code:-1. All original assertions retained. Earlier actual Send66+Read21/Sync69+Read33+contiguous18 remain qualified historical unchanged responsibility graphs; not newly observed here or full Go durable-ACK/installed GUI acceptance. No visual/layout change.

Fresh final tools/verify_frozen_architecture.py, ci/check_architecture.py --scope all --json, ci/check_s2_planning.py and82 tests/architecture PASS (one pre-existing Windows skip), exact argv/exit/time/output in final-static.json. Development and clean committed Acceptance/postclean results are bound by command-history.json and final external receipt. Local/Recorder results do not establish independent acceptance.

## Preserved failures and cleanup

Old R-FIX-REFRESH-OWNER remains raw immutable partial: lastseq60 command_started build-two.py, actual old exit unavailable. Old OOM/mmap/malloc/argument split/SyntaxError and controlled native9 outputs preserved; no old9APK promoted to10. Old raw/captured stdout redaction hashes are distinguished from stored blob hashes. New first install failed debug signature mismatch; only two disposable fixture packages on proven own5612 uninstalled then sealed APKs installed. Owner actual bundle10 PASS was followed by external collector FAIL because it expected println in am stdout; println belongs to device logcat. Corrected only collector to bind existing actual count/result/sdk/code, then ran remaining errors. No production/test assertion weakened or unnecessary owner rerun. One direct launcher path typo failed before Recorder started child; disclosed as a direct trace gap.

Own5612 closed, qemu absence verified, reverse/devices empty; only receipt-proven AVD removed after exact resolved-path checks. First deletion WinError5 on own pstore.bin retained; only its Windows readonly attribute33 cleared, never ACL/trust. Generated build/.gradle preserved externally. Only the adb daemon proved newly started by recovery query stopped. No private device/data/global trust/ACL/main write. Main782unknown/two tracked edits untouched.

## Current bindings and independent next action

185 current production input hashes;323 distinct composite ordinal/path/ID navigation records=288 executable+35 nonexecutable, never323 catches. Prior318 identities preserved plus five current necessary lifecycle catches; duplicate RH294 identities remain distinct. All actual source tokens/line/column/hash and inventory fault→present authority→actual recovery agree.22 actual factual grounds corrected in both current navigation and inventory: native header/menu/enum and translation display cases are distinct; Android Sync wire coercion/parser/overflow is protocol rejection; approved shared contiguous READ absent-row mapper is RETAINED_ABSENT_ROW_ONLY, not excluded unchanged. No inherited semantic-review PASS. Full new independent semantic reviews remain mandatory.

Original regular27 receipt SHAa8df4b6fe9ba3147bce44f2646d56aafd7199dc3bf92a7cf35918e16b50818fa and all211 artifacts remain byte-exact in original external directory and regular-review-27-originals.zip; per-entry SHA/bytes and archive GitOID separately bind reconstruction. Old318 metadata Gitblob OIDs/bytes are in prior-318-candidate-metadata.zip. Prior Fix raw/helpers/compiled graph sealed in prior-fix-partial-raw.zip without editing/finishing that run. Old50MB full diff is archived original once, no recursive new full diff regeneration.

New R-RECOVER-REFRESH-OWNER-FINISH prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013 relatedR-FIX-REFRESH-OWNER; direct startup/inspection/external helper preparation and truncated-authority-read gaps disclosed, no complete prospective trace or hidden-fact reconstruction. Repo command-history/snapshot is bounded before own final finish; final complete run remains external and sealed after commit. Recorder validation only verifies structure.

Coordinator next: NEW fresh complete regular185/323/65 on clean finalSHA, then DIFFERENT NEW uninvolved specialized error review SAMEfinalSHA. Any Fix repeats both. Both PASS before push/CI-triggeringPR; then applicable actual exact-head required hostedCI/protectedintegration/actual-main verification/safe H:/IM-platform sync. Taskdone/S2PASS/mainSHA/synchronization all PENDING. Sourcelease RELEASED only after final clean sealed receipt. No acceptance performed by this Fix.

# Historical pre-27 recovery handoff

Current recovery actor /root/recover_wss_desktop_fix_finish; exact assigned root H:/.codex/worktrees/err/IM-platform; branch task/LOOP1-ERROR-HANDLING-001. Final four-source repairs and185/318(283 executable35 nonexecutable)/65 exact current inputs are in spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-android-wss-cleanup/handoff.md. Last accepted main35bd6f5; final task SHA/clean Acceptance/Recorder/lease release comes from external final receipt. Main782unknown/two tracked edits untouched. Taskreview/S2OPEN; both NEW finalSHA reviews/hosted/integration/main/sync PENDING. Local proof is not acceptance.

Historical candidate-specific implementation/fix records below retain their original scope/counts and do not override this current recovery handoff or current.md. Earlier local/native outputs only qualify where exact unchanged input graphs are explicitly rebound. Current support did not complete whole185 semantic acceptance; final independent regular and specialist each cover entire current scope.

# Next Action

Coordinator dispatches fresh regular Review on final clean committed SHA, then a different fresh uninvolved error-handling audit on the SAME finalSHA. Both pending. Any Fix requires another finalSHA regularReview and new specializedAudit; no push/PR/CI trigger beforehand. After bothPASS: actual exacthead required hosted jobs, protectedintegration, actual-main and safe H:/IM-platform synchronization. No done/Stage Gate PASS yet. Owned emulator5588 closed; all task-only AVD/partialcopy cleaned after ownership checks, generated build/test outputs preserved externally. No trust/native install lease or owned backend/process remains.

# Activation 2026-10-13

+Fresh independent recovery audit PASS (39 checks), all11 external I18N seal hashes and candidate/main/CI/sync bindings verified; exactmain35bd6f5 matches assigned clean baseline. Minimum frozen/planning/architecture PASS, Acceptance PASS80controls/one documented skip with dedicated cache after preserved defaultcache permission FAIL. Authority assessment: additive subordinate pre-CI error audit preservescanonical§12, no Frozen revision/ADR required. OriginalCurrent I18Ndone and no unfinishedTask. Statebacklog→ready→active; sole fresh Implementation Agent owns task writes, root Coordinator releases writer. New current points here. AllTask acceptance/newReview/CI/integration/sync stillPENDING. RecorderparentR-ERROR-COORD-20261013 incompletepre-start; newworkerregisters ownrun.

# Human narrow boundary clarification

Human explicit answer: “允许仅修正异常边界，SQLite 写入与草稿保持不变”. Apply only native error provenance/capture boundary correction in existing Send and necessary Sync/Workspace consumers. No SQL, Repository, schema, transaction, write behavior, Composer or draft change. Preserve real rollback/closed-database/account assertions; add unknown Error/primitive/native-string-spoof observer proofs. One Send-local error-origin tag is necessary because the current mixed wrapper loses actual native-failure provenance; no generic framework/queue/retry is added. Evidence: spec/progress/evidence/LOOP1-ERROR-HANDLING-001/human-boundary-clarification.txt. Earlier rejection/restoration remains historical. Final independent Review/error audit/CI/main sync all pending.

# Fresh regular Review770 FAIL and F1 Fix (2026-10-13)

Regular Review7700645f54de613c913b306a03824c9c5dc20c09 FAIL F1[P1]: actual native Repository reads bypassed Send origin tag, leaving Sync syncing/queue rejected and history error absent. Original report/hash/checks/repro preserved at spec/progress/evidence/LOOP1-ERROR-HANDLING-001/regular-review-7700645/. Fresh /root/fix_read_origin repairs only literal native read boundary in existing accountSend accountRepository factory and three production constructor consumers; transaction/SQL/storage/Repository/nativeDB/Composer/draft unchanged. Two read fixtures invoked by original Desktop Send verifier;184production final hashes/294retained sites and65protected inputs bound. Full explanation/commands/failures/limits: spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-read-origin/handoff.md and verification-history.json.

This Fix is F1 only, not full184semantic acceptance. New final committed task HEAD requires new fresh regular Review then different fresh specialized audit on SAME finalSHA; bothPENDING. Task remainsreview/S2OPEN; nopush/CI/PR/integration/main-sync. LastGood35bd6f5. Sole Fix owns these uncommitted files until committed clean release; main782unknown/2tracked untouched. Recorder R-ERROR-READ-FIX prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013/relatedR-ERROR-REGULAR-7700645; incompleteprestart/directinspection explicitly disclosed. Actual freshDesktopcompile/Auth/literalread/SQLxread/TLSSendSync localPASS; Finalarchitectureall/tests82(oneexisting skip)/planning/frozen/Development recovery PASS in recorded commandhistory; clean committed Acceptance receipt will be external after commit. No newframework/migration or authority exception.

# Fresh regular e229 FAIL and Android read-origin Fix (2026-10-13)

Regular e2294ac0b8e4d28843ec318416e09f38c4248982 FAIL F-ANDROID-READ[P1] is durably immutable at spec/progress/evidence/LOOP1-ERROR-HANDLING-001/regular-review-e2294ac, full report/checks/hashsealed semantic coverage/retained grounds/receipt. Fresh sole /root/fix_android_read_origin repairs direct Android read provenance and preserves existing initialization projection at literal invocations only; all excluded65 inputs unchanged. New185production/302retained navigation inputs bound; final semantic acceptance still pending. Actual API34 Sync69+Read33/Send66/originalerrors, strictDesktopcompile, final architectureall/tests82(oneexisting skip)/frozen/planning/Development local PASS; verification-history.json retains original generated-output guard failure, write/adb denied attempts and explicit retries. Runtime/continuation limitations and exact boundary equivalence in fix-android-read/handoff.md and boundary-scope.txt. No private device/globaltrust/main writes; owned5590 closed, ownedAVD removed, builds preserved external. Clean committed Acceptance/Recorder receipt follows external finalSHA.

Both NEW finalSHA regularReview and different fresh specializedAudit PENDING. Task review/S2OPEN; no push/CI-triggeringPR/integration/main-sync; lastGood35bd6f5. Coordinator must allocate new fresh contexts on exact committed clean task HEAD and then applicable actual hostedCI/protectedintegration/main verification/safe sync. Recorder R-ERROR-ANDROID-READ-FIX prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013 relatedR-ERROR-REGULAR-E2294AC; initial direct readings disclosed, no raw stream edits. Fix-only evidence is neither Task nor Gate acceptance.

# Fresh regular697 FAIL and Send/cleanup-root Fix (2026-10-13)

Regular697ef28 FAIL BOTH F-SEND-READ/F-CLIENT-CLEANUP-ROOT is immutable at regular-review-697ef28/ including full seals/report/coverage/grounds/receipt/helpers/checks. Freshsole /root/fix_send_cleanup_roots repairs ONLY2literalSendreads viaexistingrepositoryRead and3mandatoryHTTPcleanup roots. Existingstoragehelper/ALLwrites/init/SQL/Repository/nativeDB/Composer/drafts unchanged;65protectedcanonicalinputs equalaccepted35bd6f5.185production inputhashes/305retainedsites (old302 plus3necessaryprimarycaptures) current, no independentfinalsemanticPASS claimed.

ActualownedAPI34Send66+newRead21/Sync69+existingRead33/originalerrors, lockedWeb strictbuild/behavior/renderer/appearance/i18n, sharedstrictbuild/originalSend/Sync and exactknownFAILED/unknownprimitive/dualcause/logoutcontrols localPASS. Details/knownfailures/limitations/resourcecleanup/method: fix-send-cleanup/handoff.md, input-checks.json, runtime-cleanup.json, verification-history.json. Nativeerroredstream sameknownroot remainsFAILED; onlydistinctroots usebuilt-inAggregateError, preservingknownclassification onlywhenbothboundaryfaults known; unknownprimary neverreclassified. Actual204nullbody vscontrolledadapterexposedemptybranch explicitly labeled. No newdeps/framework/publiccontract/write policy.

Regular Review finalSHA: PENDING; Specialized Error Audit finalSHA: PENDING. NewcleancommittedtaskHEAD delivered externally; bothNEWfreshcontexts mustreview SAMEfinalSHA, no priorPASS reusable. Next: newfreshregularReview thenDIFFERENTfreshspecialist; no push/CItriggeringPR untilbothPASS, thenexactheadhostedCI/protectedintegration/actualmain/safemain sync. Taskreview/S2OPEN, LastGood35bd6f5, synchronizedresultPENDING. RecorderR-ERROR-SEND-CLEANUP-FIX prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013/relatedR-ERROR-REGULAR-697EF28 incompleteprestart/directread factsdisclosed; finish/validateexternal aftercommit. Own5592/AVD/buildleases released/preserved; mainuntouched; sourcewriter releasesonfinalcleancandidate receipt.

# Fresh regular b5ea135 FAIL / Human READ mapper exception

Regular b5ea135 FAIL F-CLEANUP-CAUSE-CYCLE and F-CONTIGUOUS-READ-DEFAULT preserved immutable; sole fresh Fix /root/fix_cause_cycle_read_scope owns repair. Direct Human reply to Coordinator: “允许仅修正这两个只读映射”. Exact question/reply separately saved at fix-cause-read/human-read-mapper-scope.txt; Coordinator boundaries are interpretation of scope, not a new Human quote. This amendment precedes source writes. Only two contiguous READ mappers distinguish absent row zero from invalid present canonical decimal/null failure. No SQL/schema/init/transaction/write/nativeDB/Composer/draft changes. HTTP dual-known branch receives distinct projection to preserve acyclic roots. New finalSHA regular Review and different fresh specialized audit remain PENDING; no push/PR/CI/integration/main sync or Task/S2 PASS. Last accepted35bd6f5; source-only local Fix evidence follows.

# Fresh b5 repair local handoff

Both b5 findings repaired within pre-amended Human scope. Only3HTTP dual-known projections and2contiguousREAD mappings;185inputhashes/305navigation; protected63equal+2READmethod exceptions with allotherbytes/readSQL equal. No false all65unchanged statement applies to this newcandidate; older paragraphs preserve earliercandidate history. Current local lockedshared/Web/strictDesktop/literal/actualSQLx and API34 Sync69+Read33+contiguous18/Send66+Read21 PASS; finalstatic/recovery/history/failures/resources in fix-cause-read/handoff.md and verification-history.json. New finalSHA regular and DIFFERENTfreshspecialist bothPENDING, then exactheadhostedCI/protectedintegration/actualmain/safesync; no push/Taskdone/StagePASS. Taskbranch exactSHA/cleanAcceptance/Recorderreceipt external after cleancommit. LastGood35bd6f5. Own5594/5596closed/buildspreserved; mainuntouched. SoleFix sourcelease releases after finalcleanreceipt.

# Fresh specialized a292 FAIL / local Outbox mixed-root repair (2026-10-14)

Regular a292 PASS is old-candidate only; fresh specialized a292 FAIL F-OUTBOX-MIXED-CONNECT-ROOT is immutable at special-error-a292/, all332 seals verified; old regular at regular-a292-recovery2/, all355 seals verified. Sole new Fix /root/fix_outbox_mixed_roots repairs only existing Outbox transport predicate and core regression tests. Actual default pgx DNS/Dial joins IPv6 network refusal with IPv4 XX000; mixed/unknown return original complete error instead of log/retry, pure known transport continues existing pending retry/cancel. Actual regression red before fix then green, allGo/race/vet and actual disposable PG/NATS DB_TEST_ENABLE=1 localPASS. No new categories/framework/dependencies/SQL/public contracts or excluded SQLite write/draft change.

Current185 product hashes/306 precise token records (305 historical plus1 previously omitted retry boundary,271executable35nonexecutable) and all65 protected bytes equal a292:63wholebaseline +2prior permittedREADexceptions. Durable exact commands/results/failures/resources/protection/limits in fix-outbox-mixed/handoff.md and verification-history.json. Final candidate identity is exact committed task branch HEAD bound by external sealed Fix receipt; clean committed Acceptance/Recorder finish follow. Taskreview/S2OPEN/lastgood35bd6f5. Sourcewriter owns only enumerated delta until clean final receipt releases lease; main unknown work untouched.

Both NEW finalSHA fresh regular Review and DIFFERENT NEW specialized audit PENDING. Any further Fix repeats both. No push/PR/CI/integration/main sync until reviews PASS; after bothPASS exact-head actual required hostedjobs, protectedintegration, actual-main and safeH:/IM-platform synchronization remain required. Synchronization/mainSHA PENDING; no Taskdone/StagePASS. RecorderR-ERROR-OUTBOX-MIXED-FIX prospective_resume incompleteprestart, relatedR-ERROR-SPECIAL-A292; raw old streams immutable. Fourowned ephemeral projects empty/3owned migrate tags removed; no private process/device/hosts/trust write.

# Fresh regular26 FAIL and appearance read Fix (2026-10-14)

Fresh sole Fix /root/fix_appearance_read_boundary; assigned managed root H:/.codex/worktrees/err/IM-platform, task/LOOP1-ERROR-HANDLING-001. Pre-fix26a2941024c561d711d0d572b82f0f0f7a46d984; accepted lastGood35bd6f5f1091503f95a0282f730ed04233b0b6ea. CurrentTask review / S2 OPEN. No push/PR/CI/integration/main-sync by Fix.

Latest fresh regular26 FAIL F-APPEARANCE-EXISTS-DEFAULT immutable receipt01195917 and native seal42ba453f verified/copy158 sealed artifacts. Producer Path.exists turns actual metadata error into false; literal appearance_load returns normal cold/16/1, TS appearance.load/Workspace.start bypass error state. Official standard library source https://doc.rust-lang.org/std/path/struct.Path.html#method.exists documents this. Frozen6.1/ADR9 authorize app-owned appearance; ADR11 unavailable defaults only Web and ADR12 only language. No conflict/new authority needed.

Repair only current appearance read boundary: existing command delegates to one private path reader, one literal fs::read, NotFound alone retains cold/16/1; other native IO faults existing Appearance unavailable. Tuple bytes and original malformed/oversize/bounds validation unchanged. One private path helper pays current testability rent: invokes actual same reader on owned files without real app data or visible launch. No generic framework/callback/dependencies/public symbols. appearance_save and all remaining native production byte equal26. All65 protected inputs exact26 (63wholebaseline,2priorHumanREAD-only contiguous exceptions with SAME SQL/allotherRepo bytes). SQLite writes/DB/schema/init/transactions/Composer/drafts untouched. Go unchanged; prior real default mixed pgx/Relay18controls, ordinary/race/vet/live DB_ENABLE1 evidence historical only; new final SHA requires both complete reviews. Existing Human-deferred social case remains unexecuted/notcanonicalPASS.

Actual cargo test --locked --lib appearance regression RED before repair: real owned Windows invalid filename caused read nonNotFound yet old returned Ok(cold,16,1). Green actual cargo test --locked --lib -- --nocapture:3native tests PASS, including absent/valid/syntax-invalid/font-invalid/density-invalid/oversize/directory/invalidfilename8cases, unchanged language isolation and owned credential roundtrip. Owned paths removed explicitly; no ACL/identity/trust/privateappconfig changes. InvalidFilename/directory are controlled real OS IO fixtures, not an actual legitimate app_data permission-denial reproduction; source+official API proves producer permission reachability, runtime incidence unmeasured.

Fresh strict exact-source Desktop TypeScript compile/source-binding PASS. tests/clients/errors/appearance_native_reads.mjs consumes actual Rust stdout tuples/errors via controlled literal IPC and compiled appearance.load/Workspace.start:8cases and unknown identity PASS; fault marks existing load error, unknown rejects with original identity. This is actual native reader plus controlled IPC/compiled consumer proof, not installed Tauri UI/ACL acceptance. Existing compiled GUI Auth controls and current resource/language scheduling/enum/fallback/unknown controls PASS. Original assertions intact. Validation used existing source-equal external dependency fixture; regenerated ignored outputs only, no review raw/sealed artifact edits; own i18n output isolated externally.

Failure history retained: first automatic approval timeout not started, one allowed smaller retry succeeded; native first compile missing frontendDist failure, fixed by existing exact-source build; expected RED; initial i18n missing local TypeScript and incomplete old fixtureMobile failed, correct I18N_TYPESCRIPT_PACKAGE plus isolated I18N_OUTPUT_DIR succeeded. Direct startup/read/tool prep trace gaps exposed; Recorder prospective_resume incompleteprestart, truthful delegated summary, finished structural validation external after committed candidate. Local/Recorder not Task/Gate acceptance.

Production inventory185 current hashes, navigation307distinct records =305original+OutboxRH306+appearanceRH307,272executable35nonexecutable (never307catches); original duplicateRH294 composite ordinal/path/ID preserved. Existing token masks shifted one line only for native, exacttoken-coordinate verification. New boundary fault/authority/recovery explicit; all independent decisions PENDING on new finalSHA.

Minimum final verification: frozen/PDF, architecture --scope all --json, planning,82architecturetests(one existing Windows skip), Development; committed clean Acceptance/postclean and actual Gitblob checks recorded in external final receipt. Full current command argv/exit/durations/rawblobs in verification-history.json. No migration/contracts/Frozen/ADRs/security/ACK/compatibility/language or framework choice changes. Main H:/IM-platform782unknown/2tracked untouched, sync/mainSHA PENDING.

Next exact action: Coordinator new fresh regular Review on clean committed finalSHA entire185/307/65, then DIFFERENT fresh specialized audit SAMEfinalSHA. Any Fix repeats both. BothPASS then exact-head required hostedCI/protectedintegration/actualmain/safeH:/IM-platformsync; noTaskdone/S2PASS before synchronized accepted outcome.

# Interrupted appearance Fix recovery (2026-10-14)

Sole recovery Fix /root/recover_appearance_fix_finish adopted only script/hash-proven owned delta after previous actor became unavailable. Exact assigned root and pre-fix HEAD26a2941 verified. Scripts reconstruct native/current/task/checkpoint/handoff exact bytes; 185 product hashes,307 token coordinates,65 protected equal26 and158 sealed regular-review copies verified. No other writer/process found; process inventory required routine escalation. Main/GitHub untouched.

Old R-FIX-APPEARANCE-READ remains running/partial; raw research archived byte-for-byte at partial-original-research/, never finished in new identity. Recorded old final Development was exit1, not PASS: current.md lacked command/result/evidence fields. Recovery reproduces exit1 after fresh frozen/architecture/planning/82tests PASS; fields corrected and recovery rerun follows external final receipt. Old native red/green/compiled/Auth/i18n results are reused only after exact source/hash and raw-output binding; not new runtime observations. Physical ACL/installed GUI acceptance remains unclaimed. First recovery ownership audit failed only due optional nonexistent final-receipt.sha256; assumption corrected, all actual158 seals passed.

New R-FIX-APPEARANCE-RECOVERY prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013/relatedR-FIX-APPEARANCE-READ; startup direct-read/inspection gap and unavailable hidden facts disclosed. Final committed candidate/clean Acceptance/Recorder structural validation/source lease RELEASED external receipt. No independent review or acceptance claimed; both NEW regular then DIFFERENT NEW specialist on SAME finalSHA pending, followed by exact hostedCI/protectedintegration/actualmain/safe H:/IM-platformsync. Task review/S2 OPEN/lastGood35bd6f5; mainSHA/synchronization pending.

# Fresh regular a337 FAIL and Android suppressed-root Fix (2026-10-14)

Fresh sole Fix actor /root/fix_android_suppressed_roots; assigned exact root H:/.codex/worktrees/err/IM-platform, branch task/LOOP1-ERROR-HANDLING-001, pre-fix a337780de5f2ab5d2c8cd43d93c66dac06d53a53. Current Task remains review, S2 OPEN. Last accepted35bd6f5f1091503f95a0282f730ed04233b0b6ea. Clean committed finalSHA/Acceptance/Recorder/exact blobs delivered by external receipt, not acceptance or synchronization.

F-ANDROID-SUPPRESSED-UNKNOWN and F-RETAINED-GROUND-MISMATCH repaired locally only. Original fresh regular a337 FAIL remains immutable at ../regular-review-a337780/:63 artifacts plus its receipt copied byte-for-byte, receipt SHAa25308d22980cad1363686564ba1c1b9b5ea5c2454b8a6ec4bf0c1d673c8deb9. Actual staged Gitblob OIDs are bound in final external receipt. No inherited regular PASS or specialized PASS.

Actual unchanged source JVM baseline reproduced Auth read AND write IOException+unknown close projecting causefree ApiFailure; Sync IO+unknown close and actual typed SyncFailure+unknown close projecting known recovery. Link stubs only session/request construction and unused auth support; response decoder never reached for fault cases. These are controlled SDK stream producer failures, not default Android implementation incidence.

Only SyncHttps.kt/Auth.kt current resource/projection boundaries changed. Kotlin use preserves original primary/suppressed cleanup; disconnect now runs BEFORE result delivery and contributes its actual distinct failure to original.suppressed. Known primary with only actual IOException suppressed cleanup remains existing Sync transport/protocol or Auth safe failure. New known IO/wire projection references original cause, so both known roots remain exact and acyclic. Unknown primary remains original. Known typed/IO/cancellation primary with unknown suppressed root becomes standard IllegalStateException(cause=original primary); this tiny necessary wrapper prevents Workspace accepting top-level IOException/SyncFailure/ApiFailure as a recoverable category. Unknown cleanup identity remains original in primary.suppressed. No new error category/framework/public type/dependency/retry/logging. IO-only suppressed predicate is duplicated privately in each actual owner, not generic framework. Same-root disconnect guard avoids self-suppression.

Inactive Sync continuation discards only known expired result and throws mixed unknown. Cancellation cleanup always cancels its job even when disconnect fails, original mandatory disconnect claim removed exactly once through AtomicReference. Original cancellation/HTTP status/header/no-store/UTF8/resource-size/protocol behavior retained. No consumer, SQL, schema, init, transaction, writes, nativeDB, Composer or draft change.65 protected inputs exact pre-fix;63 whole accepted baseline and2 prior Human contiguous READ mapper exceptions unchanged. All other production bytes including native one-read/NotFound appearance and Go joined-Outbox classification unchanged.

New32 actual production Kotlin tests run on current JVM AND real exclusively owned API34 emulator5598. Matrix: Sync/Auth response-read and output-write plain IO, distinct dual known IO, mixed unknown close, unknown primary, mixed disconnect; typed protocol size guard + known/unknown close; normal success and known/unknown disconnect-only; real caller cancellation while blocked read, continuation becomes inactive, known-only dropped but unknown reaches CoroutineExceptionHandler. Exact roots checked through cause/suppressed identity, no cycles, targeted close once, disconnect once. Auth uses a process-scoped controlled URL handler, no real global trust/private data. Tests now run from original ErrorHandlingInstrumentation via one added call, all original assertions unchanged; standalone HttpCleanupInstrumentation retained as focused runner.

Actual old TLS Send66+Read21 and Sync69+Read33+contiguous18 PASS on same emulator with existing verifiers' owned private fixture CA and unchanged default-trust negative controls. Original errors PASS; after one-call integration errors again PASS+httpCleanupChecks32. These are controlled real Android SDK/TLS/SQLite/Coroutine executions, not Go server durable-ACK acceptance or installed default Android HTTPS cleanup incidence. No new screenshot/product visual change.

185 current production hashes;311 distinct composite navigation records=307 preserved identities+4 mandatory primary/disconnect catches,276 executable/35 nonexecutable. Three removed Auth catches truthfully mapped to current when projection tokens, not called catches; original duplicateRH294 composite ordinal/path/ID preserved. Sync URI/missing-stream/strictUTF8/failure dispatch and Auth token/stream/wire/IO/credential/restore grounds now actual fault→current authority→real failure/recovery, not generic optional UI placeholders. Full token/hash/protected verification in input-checks.json/current-navigation.json/protected-inputs.json. Local navigation is not independent whole-scope semantic acceptance.

Failures preserved: first build PowerShell split -P argument into Gradle task; corrected Python argv build succeeded. First unchanged Send direct instrumentation omitted required certificate and failed NPE; corrected original native.py verifier supplies its fixture and passes unchanged tests. First collector assumed old stripped line preserved indentation, failed; exact token comparison corrected and all311 PASS. First green harness synthetic active stream cancellation hung, terminated only verified owned JVM; no production category expansion and real caller cancellation tests preserved. Stop-Process failed, exact verified taskkill succeeded. Startup/preparation direct recording gaps and tool-truncated reads disclosed in Recorder prospective_resume, not complete trace.

Owned5598 closed, reverse rules empty, exact isolated own AVD removed, generated build/.gradle outputs preserved externally. No private app/credential/globaltrust/ACL or main writes. Original main782unknown/2tracked preserved. No push/CI/PR/integration. Recording R-FIX-ANDROID-SUPPRESSED parentR-ERROR-INTEGRATION-COORD-20261013 relatedR-ERROR-REGULAR-A337780; own finish/structural validation follows clean candidate, never Task PASS.

Next exact action: NEW fresh complete regular Reviewer185/311/65 on clean newSHA, then DIFFERENT NEW specialized error auditor SAMEnewSHA. Any Fix repeats both. Only bothPASS permits exact-head actual required hostedCI/protectedintegration/actual-main/safe H:/IM-platformsync. MainSHA/synchronization PENDING, Taskdone/S2PASS forbidden. Sole source lease RELEASED only after final clean receipt.

Final minimum frozen/architectureall/planning/82architecturetests(one existing Windows symlinkSkip) actual PASS. First final Development exit1 because new history file was not yet generated; real failure retained, history now generated and unchanged verifier rerun follows. Exact finalSHA clean Acceptance/postclean/Recorder finish externally bound.

Corrected final Development PASS. Collector raw-vs-redacted output hash assumption FAIL and both missing-history Development failures retained; corrected separate hash fields, immutable original events unchanged. Auto-review timeout before final preparation did not start; one authorized smaller retry follows. Exact finalSHA clean Acceptance/finish externally bound.

# Recovered final local Fix candidate (2026-10-15)

Sole Fix actor /root/recover_wss_desktop_fix_finish, fresh recovery of interrupted /root/fix_android_wss_cleanup. Exact assigned and Git-resolved root H:/.codex/worktrees/err/IM-platform; branch task/LOOP1-ERROR-HANDLING-001; pre-fix8f5f2b4275652d8e3fdff343d6a286ac805ad14a. Current Task review/S2 OPEN. Last accepted main35bd6f5f1091503f95a0282f730ed04233b0b6ea. Final committed SHA/clean Acceptance/Recorder structural result/sourcelease RELEASED are bound by final external receipt, not by self-acceptance. No push/PR/CI/integration/main write or sync here.

## Current scope and behavior

Exactly four production files differ from8f5: mobile/send/Wss.kt, desktop/application/ui/auth.ts and workspace.ts, mobile/ui/Auth.kt. Other181 of185 current production inputs are byte-identical. No new dependency/framework/error category, logging/retry platform, contract/schema/ACK/security/compatibility/Frozen/ADR change. Preferences implementation, Repository/SQL/init/transactions/native database/SQLite writes/Composer/drafts remain untouched. Protected65 are byte-identical8f5:63 whole accepted baseline plus two prior Human contiguous READ mapper exceptions; exact SQL/all other Repository bytes unchanged.

Fresh independent regular8f5 FAIL F-WSS-CLEANUP-ROOT-REPLACEMENT[P1]/F-WSS-RETAINED-GROUND-MISMATCH[P2] is preserved. Current WSS used finally close then ended, replacing operation primary with unknown close and skipping ended. Actual Throwable retention now preserves distinct operation/retirement/ended roots with standard fresh IllegalStateException(cause=primary,suppressed=cleanup); original graphs are not mutated. Single unknown/same root keeps identity. Synchronized private retireSocket detaches ownership before one close; public close retains only actual known IOException retirement. Finally always attempts ended. IO-only external transport still retires normally; opened/message observer IO is outside transport recovery and fails. Local retain and socket detachment address three actual current lifecycle sites and caller-close cancellation; no speculative factory/runtime.

Read-only support immutable8f5 confirmed Desktop logout Promise.all early known rejection masks later unknown secure removal, and parallel Workspace actual Repository reads mask later unknown siblings. Both current operations use standard allSettled, wait existing work, deduplicate identical roots, preserve single identity or AggregateError. Workspace failure accepts only nonempty all-known existing boundary types; mixed/unknown/empty aggregate rejects even when retired. Known-only still shows honest unavailable failure. No blanket Promise conversion or generic classifier.

Desktop refresh canonical session_expired followed by credential_remove failure lost primary. Current literal clear catch retains distinct primary/cleanup AggregateError and same-root identity. Workspace only original top-level ApiFailure triggers existing expiry action; known aggregate shows unavailable and adds no cleanup retry. Falsy primitive0/null/undefined remain roots.

Fresh support F-ANDROID-REFRESH-CLEANUP-ROOT[P2] independently reproduced actual request401/Wire session_expired then Preferences.remove commit=false IOException or unknown cleanup replacing primary. Root authorized current allowed Auth.refresh boundary before source edits. Successful clear retains exact ApiFailure and both pointer removals. Distinct roots use standard cause/suppressed without mutating originals. IO-only credential cleanup remains standard IOException, preserving existing Workspace known unavailable handling without re-expiry; unknown/Error/mixed cleanup uses ordinary IllegalStateException and propagates. No network-category borrowing, new category, Prefs change or retry. Same-root guard rethrows original.

## Verification and runtime limits

Fresh exact-source strict Desktop compilation PASS, focused literal IPC/current Workspace37 controls PASS, original Auth/workspace/appearance/native/UTF8/account retirement controls PASS. Node uses actual production compilation; link stub only forwards literal Tauri IPC, no live private credential or SQLite operations. Historical SQLx/TLS/Desktop/Go results belong to earlier unchanged responsibility graphs and are not newly observed here.

Fresh current WSS JVM21 PASS. Fresh Android Auth/Wire JVM5 PASS: normal cleanup/known IO/unknown/Error/IO-with-suppressed-unknown. One initial host fixture compile failed because its Preferences linking stub accepted Exception instead of Throwable; only the host link signature was corrected. Not product runtime incidence.

Actual exclusively owned Android API34 emulator5610: final native compile and RefreshCleanupInstrumentation5 PASS. It executes current Auth.request HTTP401/refresh/clear and actual Preferences encrypted write/read/remove. Actual SharedPreferences.commit=false exercises production IOException; controlled Editor runtime exception/Error exercise unknown roots. Normal removes two pointers and retains primary; non-expiry fails without cleanup. No real network/TLS/commit-failure incidence claim. Process URL handler belongs only to disposable instrumentation. Focused JVM additionally covers direct mixed IOException roots without Java proxy checked-exception wrapping. Original ErrorHandlingInstrumentation fresh PASS, HttpCleanupChecks32 and WssCleanupChecks21 PASS on same current source. All old assertions retained.

Old actual API34 emulator5600 Send66+Read21, Sync69+Read33+contiguous18 PASS are reused only after unchanged Send/Sync source/test graph byte checks. These graphs do not consume Auth.refresh; current changed Auth controls run fresh. runtime-source-bindings.json records exact hashes/qualification. Original native controls use owned verified TLS fixtures and unchanged default-trust negative controls, not Go durable ACK or full three-end GUI acceptance. No visual/layout change or new screenshot claim.

Own emulator5610/reverse rules/AVD and generated build outputs cleaned or preserved externally; only adb daemon proved created by this run stopped. Exact verified H-only AVD deletion recorded in recovery-runtime-cleanup.json. Prior5600 cleanup remains runtime-cleanup.json unchanged. No private device/app data/global trust/ACL or main work touched. Read-only process inventory found only our query/Recorder command lines, no surviving old worker; no process killed outside own emulator.

## Binding and preserved evidence

185 current production hashes,318 distinct ordinal/path/ID navigation=283 executable35 nonexecutable, never318 catches. Original duplicate RH294 identities remain distinct. 311 prior identities+2 WSS catches+3 Desktop parallel/projection entries+Desktop refresh catch+Android refresh catch. All exact tokens/source hashes/coordinates verified. Android RH176 is absent refresh credential before request; RH177 is repaired lifecycle catch, not copied old defect text. Other35 Desktop/Java and68 Android support ground suggestions rejudged against actual source with corrected fault→authority→outcome. Local input binding is not complete independent semantic acceptance.

All80 original regular8f5 sealed artifacts+receipt remain exact in regular-review-8f5-originals.zip and external original directory. Original full diff50,594,724 bytes preserved, not regenerated/nested again. Archive GitOID plus each ZIP entry SHA proves reconstructability; entries are not individually claimed Git blobs. Desktop support mini/addendum and Android refresh/remaining support sealed originals are archived byte-exact. remaining-support-seals.json records whole_scope_semantic_complete=false: support185 hash/311 old coordinates and133 historical public FILE markers do not prove full185 semantic coverage. No other confirmed defect; unproved Android logout stop concern is not promoted or used to expand excluded DB scope. Final reviewers must inspect full scope independently.

Interrupted R-FIX-ANDROID-WSS raw research remains running/partial unchanged, archived byte-exact with per-entry seals. Last actual seq117 refresh-bind exit1 is retained; two exact-match typos (=== vs ==) in reconstruction script were corrected only in recovery scripts, first recovery retry also failed on Workspace matcher before successful binding. Old Node WinError2 missing child finish and other unavailable facts remain unavailable. Original AVD disk failures, Gradle environment failure, fixture/account/probe errors remain raw. Old output redaction/raw hash distinctions are preserved.

recovery-command-history.json records actual old/new argv, exits, elapsed time and durable output references. Live collector snapshot cannot include its own finish; complete final stream/clean Acceptance follows external receipt. New run R-RECOVER-WSS-DESKTOP-FINISH prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013 relatedR-FIX-ANDROID-WSS. First direct read accidentally used main recovery files, read-only, then startup restarted on assigned root. Startup truncation/direct read and external script preparation trace gaps disclosed; no complete trace/hidden facts claimed. Recorder structural validity is not Task/Gate PASS.

## Next exact action

Final frozen/PDF/architectureall/planning/82 architecture tests(one existing Windows skip)/Development results and clean committed Acceptance/postclean are bound in final history/external receipt. Coordinator must dispatch NEW fresh full regular185/318/65 on final clean SHA, then DIFFERENT NEW specialized audit SAME SHA. Any Fix repeats both. Both PASS permits exact-head actual required hosted CI, protected integration, actual-main verification and safe H:/IM-platform synchronization preserving782 unknown files/two tracked edits. Taskdone/S2PASS/main synchronization remain PENDING. Source lease released only after clean committed final receipt; no stale context is independent reviewer.

Final Development first failed strict current Verification Command/Evidence line format (multiple commands/trailing punctuation); only metadata formatting corrected. Original output retained, only failed check rerun. No product/test changes.

All318 current navigation semantics now use one current field schema and exact actual line/source. Former mixed current_authority/present_requirement/restored_state/assessment/reviewer-role fields are preserved byte-exact only in historical-mixed-navigation.zip, explicitly historical. Current inventory grounds derive from the same fault/authority/recovery fields; no contradictory current aliases or inherited independent verdict remain.

Precommit first failed only a Windows slash/backslash string comparison in the external audit script. Actual Git root had already resolved to the assigned root; Path.resolve equality corrected the script and full185/318/65/seal/owned audit then passed. No root substitution or source write occurred at the failed audit. Raw failure retained.

Full staged whitespace audit returned2 because preserved raw Recorder/native outputs contain original CRLF/trailing spaces; these bytes remain exact, never normalized to pass. Test file extra blank EOF trimmed without changing logic and focused37 rerun. Product/current/task/handwritten-doc scoped whitespace check is separate, not a full raw-evidence whitespace PASS. All actual staged Git blobs must still byte-equal originals/current bytes.
