---
task_id: LOOP1-ERROR-HANDLING-001
title: 无意义防御与静默兜底治理、全量生产代码纠正
status: review
owner: fresh Fix Agent /root/fix_read_origin
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

不处理SQLite写入失败及草稿保护；不改storage Repository/schema/native database或Composer；不改Frozen/approved ADR/contracts/security/ACK/compatibility/invariants，不加框架/库/重试机制/未来功能。unknown主仓库work不复制、不覆盖、不提交。没有两个最终SHA审查PASS不得push或创建/更新会触发CI的PR。

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

Implementation review candidate in verified managed root H:/.codex/worktrees/err/IM-platform, branch task/LOOP1-ERROR-HANDLING-001, baseline35bd6f5f1091503f95a0282f730ed04233b0b6ea. Sole fresh implementer owns this task's changes; main H:/IM-platform and its782unknownfiles/2trackededits untouched. Candidate identity is the committed task-branch HEAD delivered by Git to Coordinator; production input SHA256 inventory binds actual reviewed bytes. Local verification is not independent acceptance. No migrations/contracts/Frozen/ADR/dependencies/SQL/Repository/Composer/draft changes.

Completed governance/examples/checklist/template/startup guidance and full production inventory:184paths (117logic/declaration/build entries,67data/config/assets/docs/placeholders),293retained sites with precise fault/ground/recovery and read-only excluded handling. Full details: spec/progress/evidence/LOOP1-ERROR-HANDLING-001/implementation-audit.md, production-inventory.json, verification-history.json, protected-inputs.json and runtime-cleanup.json.

Actual local PASS: disposable PG/NATS DB_TEST_ENABLE=1 allGo; ordinaryGo; Java javac actual socket fault/normal harness; Web locked build/behavior/appearance/compiled renderer; Desktop actualSQLx+verifiedTLS Send/Sync, compiledAuth/native TypeError/UTF8/stale-account/notification tests, actualRust Windows credential/atomic tests and browserrenderer; Android API34 emulator Send66/Sync69 + real unknown/UTF8/mixed-observer/message/search instrumentation; i18n original defaults/revisions/resources + unknown proofs; architecture all and82tests with one existing skip; planning/frozen. TestSocialLoop1Applicability retains original friend-add-authorization-denied DEFERRED_BY_HUMAN (runtime not executed, not canonical acceptance PASS). Prior failures remain in Recorder and handoff; no assertion deleted/weakening.

Research R-ERROR-IMPLEMENTATION-20261013 prospective_resume, prestart incomplete. Original GBK-output failure left one command_started without finished facts; outcome unavailable, disclosed and command rerun withUTF8. Parallel recorder lock error exposed, subsequent commands serialized. Run finish/structural validation are reported externally after candidate commit; structural validity is not complete prospective trace or product acceptance.

# Next Action

Coordinator dispatches fresh regular Review on final clean committed SHA, then a different fresh uninvolved error-handling audit on the SAME finalSHA. Both pending. Any Fix requires another finalSHA regularReview and new specializedAudit; no push/PR/CI trigger beforehand. After bothPASS: actual exacthead required hosted jobs, protectedintegration, actual-main and safe H:/IM-platform synchronization. No done/Stage Gate PASS yet. Owned emulator5588 closed; all task-only AVD/partialcopy cleaned after ownership checks, generated build/test outputs preserved externally. No trust/native install lease or owned backend/process remains.

# Activation 2026-10-13

+Fresh independent recovery audit PASS (39 checks), all11 external I18N seal hashes and candidate/main/CI/sync bindings verified; exactmain35bd6f5 matches assigned clean baseline. Minimum frozen/planning/architecture PASS, Acceptance PASS80controls/one documented skip with dedicated cache after preserved defaultcache permission FAIL. Authority assessment: additive subordinate pre-CI error audit preservescanonical§12, no Frozen revision/ADR required. OriginalCurrent I18Ndone and no unfinishedTask. Statebacklog→ready→active; sole fresh Implementation Agent owns task writes, root Coordinator releases writer. New current points here. AllTask acceptance/newReview/CI/integration/sync stillPENDING. RecorderparentR-ERROR-COORD-20261013 incompletepre-start; newworkerregisters ownrun.

# Human narrow boundary clarification

Human explicit answer: “允许仅修正异常边界，SQLite 写入与草稿保持不变”. Apply only native error provenance/capture boundary correction in existing Send and necessary Sync/Workspace consumers. No SQL, Repository, schema, transaction, write behavior, Composer or draft change. Preserve real rollback/closed-database/account assertions; add unknown Error/primitive/native-string-spoof observer proofs. One Send-local error-origin tag is necessary because the current mixed wrapper loses actual native-failure provenance; no generic framework/queue/retry is added. Evidence: spec/progress/evidence/LOOP1-ERROR-HANDLING-001/human-boundary-clarification.txt. Earlier rejection/restoration remains historical. Final independent Review/error audit/CI/main sync all pending.

# Fresh regular Review770 FAIL and F1 Fix (2026-10-13)

Regular Review7700645f54de613c913b306a03824c9c5dc20c09 FAIL F1[P1]: actual native Repository reads bypassed Send origin tag, leaving Sync syncing/queue rejected and history error absent. Original report/hash/checks/repro preserved at spec/progress/evidence/LOOP1-ERROR-HANDLING-001/regular-review-7700645/. Fresh /root/fix_read_origin repairs only literal native read boundary in existing accountSend accountRepository factory and three production constructor consumers; transaction/SQL/storage/Repository/nativeDB/Composer/draft unchanged. Two read fixtures invoked by original Desktop Send verifier;184production final hashes/294retained sites and65protected inputs bound. Full explanation/commands/failures/limits: spec/progress/evidence/LOOP1-ERROR-HANDLING-001/fix-read-origin/handoff.md and verification-history.json.

This Fix is F1 only, not full184semantic acceptance. New final committed task HEAD requires new fresh regular Review then different fresh specialized audit on SAME finalSHA; bothPENDING. Task remainsreview/S2OPEN; nopush/CI/PR/integration/main-sync. LastGood35bd6f5. Sole Fix owns these uncommitted files until committed clean release; main782unknown/2tracked untouched. Recorder R-ERROR-READ-FIX prospective_resume parentR-ERROR-INTEGRATION-COORD-20261013/relatedR-ERROR-REGULAR-7700645; incompleteprestart/directinspection explicitly disclosed. Actual freshDesktopcompile/Auth/literalread/SQLxread/TLSSendSync localPASS; Finalarchitectureall/tests82(oneexisting skip)/planning/frozen/Development recovery PASS in recorded commandhistory; clean committed Acceptance receipt will be external after commit. No newframework/migration or authority exception.
