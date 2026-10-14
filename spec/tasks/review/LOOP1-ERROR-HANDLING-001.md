---
task_id: LOOP1-ERROR-HANDLING-001
title: 无意义防御与静默兜底治理、全量生产代码纠正
status: review
owner: fresh Fix Agent /root/fix_android_suppressed_roots
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
