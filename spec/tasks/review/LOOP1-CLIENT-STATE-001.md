---
task_id: LOOP1-CLIENT-STATE-001
title: 消息状态、幂等重发与好友同步
status: review
owner: /root/state_finalize
stage: S2
gate: S2
client_supplement_phase: state_product
---

# Current Resume State (fresh finalization 2026-10-10)

Fresh implementation finalizer /root/state_finalize preserves prior state_impl work and original FAILs. Product547514/native18f8/Android1b6 mandatory tests are local evidence; full verification-matrix and byte-identical originals are archived. Source/build packaging distinctions remain explicit. Mandatory Sync69, GUI46/12PNG, Web browser52, real Go suite/Sync205→208 passed. Exact TLS/root74/Android baseline and owned resource teardown completed. Screenshot527 hash audit and exact metadata/source/run derivations are in screenshot-index.json; empty screenshot-metadata-gaps is local completeness, not Architect approval. Web-row substring selector defect corrected with original matrix preserved. Clean committed candidate Recovery Acceptance follows this review transition; fresh Architect/Review/hosted/protected integration/main sync remain Coordinator PENDING. Old Recorder running remains untouched; new R-STATE-FINALIZE-20261010 is prospective_resume with public gaps. S2 OPEN; no UIREF/I18N.

# Goal

以最新三端实现和已有验收为基线，逐项记录现有能力、证据和待补齐内容，将以下要求写入任务目标与强制验收。

1. 消息可靠性的两个核心场景：
   A. 首次发送未在服务端提交，发送方超时显示 FAILED，用户点击重发后完成首次持久化并收敛为 SENT。
   B. 首次发送已在服务端提交，接收方已获得消息，发送方因成功确认丢失或延迟显示 FAILED；用户重发后获得原始提交结果，原消息收敛为 SENT。

2. 同一逻辑消息的每次重发复用原始 request_id、conversation_id、发送者身份和消息内容。服务端已有提交时返回原始 messageId、seq、createdAt；最终对应一条持久化消息、一条逻辑 Outbox 和各客户端的一条消息展示。

3. 覆盖 SENDING、FAILED、重发按钮和 SENT 的真实界面状态。FAILED 表达当前尝试未获得成功确认；迟到 ACK、实时消息和适用 Sync 均通过既有收敛入口更新原消息，SENT 保持终态。核对 Gateway/Core 超时与提交结果未知路径，使其处理符合实际提交结果和现行契约。

4. 同一会话的已确认消息以服务端 seq 为最终排序依据，覆盖：
   - R1 首次未提交，R2 先成功提交，R1 后重发成功：最终顺序为 R2、R1。
   - R1 首次已提交但确认超时，R2 随后提交，R1 再获得确认：最终顺序为 R1、R2。
   验证 UI 在 ACK、实时事件、Sync 交叉到达后保持正确身份、状态和顺序。

5. Desktop/Mobile 覆盖保留本地消息时的重启重发，以及受控测试中从全新账号本地数据库和初始同步游标恢复的流程。验证已提交历史按 seq 恢复，后续新消息使用新的 request_id 和服务端分配的序号，序号连续性与渲染顺序正确。Web 按当前页面内存生命周期和已接受的在线消息同步规则验收。

6. 补齐三端好友变更同步。明确既有好友查询和 User Sync 的触发、消费及界面刷新链路；任一端添加好友后，其余在线端最终更新好友列表、对应私聊和名称展示，并验证断线恢复与账号切换后的正确结果。

7. 使用真实服务端、数据库和客户端的受控故障注入验证上述链路。场景 B 同时取得服务端持久提交、接收方获得消息、发送方 FAILED、重发后原消息 SENT 的证据；分别核对存储记录、请求身份、序号、Outbox 和实际渲染。


# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> `spec/architecture/frozen-architecture.md` §2.3/§3/§6.1～6.6/§10 SRC-01 through SRC-07/§11/§15/§19/§20/附录A。
- `spec/architecture/decisions/ADR-0012-client-supplement-planning.md`；ADR-0005/0006/0007/0008/0009/0010/0011及对应已接受证据；`spec/architecture/decisions/client-ui/architecture.md`、`spec/architecture/decisions/client-ui/design-direction.md`。
- `spec/governance/minimality.md`、`spec/governance/execution-boundaries.md`、`spec/governance/independent-review.md`、`spec/governance/technology-selection.md`。
- `spec/domain/messaging.md`、`spec/invariants/messaging.md`、`spec/domain/sync-plugin.md`、`spec/invariants/sync-plugin.md`；`contracts/websocket/envelope.schema.json`、`contracts/websocket/sync-v1.schema.json`、`contracts/http/auth-user-friend.openapi.json`、`contracts/http/sync.openapi.json`、`contracts/database/`与对应golden fixtures。
- `spec/acceptance/client-gui.md`、`spec/acceptance/client-supplement.md`基线表与本任务全部强制验收；激活时重新读取前项实际接受树/截图/证据。

# Technology Authorization

canonical§6.1/§6.5与accepted ADR5/6/9/11；ADR12正式接受后§6.6窄补充。Web/Desktop/shared TypeScript、React，Desktop Tauri+SQLx必要Rustnative；Mobile Android Kotlin/Compose等价contracts/fixtures、SDKSQLite，真实Android Studio emulator。无新runtime/i18n/network/state/ORM库。
client_language: TypeScript
client_language: Kotlin
client_framework: React
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

只修本任务已证明缺口，Core持有message事务，Gateway只transport/unknown-outcome；不修改契约、schema或新增source职责。

# Dependencies

- LOOP1-WEB-001；须独立接受、protected integration/actual-main验证及H:/IM-platform同步全部完成，status done才可激活本项，不只是本地commit。
- LOOP1-CLIENT-SUPPLEMENT-PLAN-001；本规划必须正式生效、独立接受/合入/main同步完成才可ready/active。

# Allowed Paths

- `clients/web/src/application/http.ts`
- `clients/web/src/application/client.ts`
- `clients/web/src/application/repository.ts`
- `clients/web/src/ui/main.tsx`
- `clients/desktop/src/application/send.ts`
- `clients/desktop/src/application/sync/application.ts`
- `clients/desktop/src/application/ui/workspace.ts`
- `clients/desktop/src/application/ui/auth.ts`
- `clients/shared/protocol-sdk/src/storage/repository.ts`
- `clients/desktop/src/ui/main.tsx`
- `clients/mobile/app/src/main/kotlin/im/platform/client/send/SendViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/sync/SyncViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Workspace.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/storage/Repository.kt`
- `backend/go/core/message.go`
- `backend/go/gateway/gateway.go`
- `backend/go/core/message_test.go`
- `backend/go/gateway/message_test.go`
- `backend/go/tests/message_test.go`
- `tests/clients/send/**`
- `tests/clients/sync/**`
- `tests/clients/gui/hold_send.py`
- `tests/clients/gui/go_runtime.py`
- `tests/clients/gui/regressions.py`
- `tests/clients/web/behavior.mjs`
- `tests/clients/web/regressions.mjs`
- `tests/clients/web/browser.mjs`
- `tests/clients/state/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/send/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/sync/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/GuiAuthenticatedInstrumentation.kt`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-STATE-001/**`
- `spec/progress/checkpoints/*loop1-client-state-001*.md`
- `spec/tasks/backlog/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/active/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/review/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/done/LOOP1-CLIENT-STATE-001.md`

当前实际源码职责如client-supplement基线表；本项列出的新增组件/测试/资源目录仅承载本Task已明确职责，不授权整个clients/backend通配或跨职责搬迁。激活时以最新前项树核对，路径不足先登记scope修订并遵守authority；allowed_paths不是架构豁免。本项不得实施语言资源/语言持久化adapter或改语言/外观存储guard；UIREF仅分离稳定标识与显示接口，不提前国际化。

# Acceptance

Goal全部条目与spec/acceptance/client-supplement.md本任务段是强制验收，既有client-gui截图/Architect/独立Review/CI/main链共同生效。独立Reviewer核对真实请求/存储/状态/渲染或完整性/语言证据和实际import/minimality；不得以基线PASS代替新增场景。done前须Completion Metadata真实绑定独立接受/受保护集成/main同步，且相关证据文件可核对。前项接受树是本项baseline，不复用旧候选接受认定新SHA。

# Forbidden

不改变contracts/schema/ACK/security/兼容、技术边界或未来AI/plugin/runtime/Java功能；Web不新增聊天DB/离线历史/全量初始回填。不覆盖未知main work、不删除真实用户数据库/偏好/凭据，不自动跑StageGate。本规划endpoint不授权激活本Task。

# Minimality

使用既有Repository收敛/Send/Sync/UI与三端授权栈，直接满足本项要求；新抽象必须有现要求付租证明。无generic framework/事件总线/新库/未来migration机制。仅本项行为或组件完整性/视觉基线要求。

# Verification

- Minimum baseline: `python -Xutf8 -B ci/check_architecture.py --scope all --json`；`python -Xutf8 -B tools/verify_frozen_architecture.py`；`python -Xutf8 -B ci/check_s2_planning.py`；`tools/verify-loop1-ctrl-002.ps1 -Mode Development`，clean committed候选 `-Mode Acceptance`。
- `python -Xutf8 -B tools/verify_client_sqlite.py --scope shared`；`python -Xutf8 -B tools/verify_client_send.py --scope shared`及`--scope desktop`；`python -Xutf8 -B tools/verify_client_sync.py --scope shared`及`--scope desktop`；已接受checker命令是可执行基线，不把planned harness当PASS。
- Android `python -Xutf8 -B tools/verify_client_send.py --scope mobile --serial <实际独占emulator serial>`、`python -Xutf8 -B tools/verify_client_sync.py --scope mobile --serial <实际serial>`；`python -Xutf8 -B tests/clients/gui/android.py --serial <实际serial> --capture`。Android SDK/JDK17/Gradle及真实Android Studio emulator、有效TLS/受控证书、独占adb reverse/fixture启用；placeholder必须替换为真实值记录。Host/mock不能代替emulator。
- Web `python -Xutf8 -B tests/clients/web/verify.py`（locked install/build/behavior/appearance/source）；`node tests/clients/web/browser.mjs`实际原截图。Desktop现有locked build/`python -Xutf8 -B tests/clients/gui/native.py package` Windows安装包及真实截图/通知tray（仅后续产品任务激活后；需现有Windows x86_64 MSVC/Visual Studio vcvars64、Rust/Cargo/Tauri及locked npm依赖，遵循native.py的既有工具链路径；先完成package构建，再安装同候选制品并以其自身身份运行；缺工具链/安装/独占环境不计PASS）；`python -Xutf8 -B tests/clients/gui/regressions.py`只在输入与独占环境满足时运行。
- Backend现有`go test ./...`（cwd backend/go）和 `python -Xutf8 -B tools/verify_sync_runtime.py`适用真实Go/PostgreSQL/NATS/TLS入口；DB_TEST_ENABLE=1、实际受控DATABASE_URL/NATS_URL，缺环境skip不计PASS。受控数据/证书/进程创建与回滚须记录，不读取私人数据或凭据。
- 激活前为本任务新增场景明确实现并登记实际harness命令、fault hook/环境、fixture身份、独占资源及清理。现入口baseline不替代新增A/B/组件/语言证据；未执行命令不计PASS。
- Screenshot manifest绑定候选SHA/build/runtime/fixture/状态/尺寸/theme/font/density/语言与PNG hash，真实原图/Architect决策；独立Review/exact-head必需hosted jobs/protected integration/actual-main/safe sync全部完成才done。

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-STATE-001/`保存可复现场景/原始结果/failed记录/真实截图Architect/independent Review/hosted/main/sync；Research Recorder独立run。当前未执行产品验收；local/Recorder PASS不是Task/Stage PASS。

# Completion Metadata

acceptance_result: PENDING
accepted_candidate_sha: unavailable
integrated_main_sha: unavailable
main_sync_result: PENDING
independent_review_evidence: unavailable
hosted_acceptance_evidence: unavailable
main_sync_evidence: unavailable

# Handoff

仅backlog规格交付，无产品实现/接受/同步。起点latest accepted main b4d271ceeed40343e627450f6b43cd9c9ad5ff0e，基线审计见规划evidence/baseline-audit.md；本规划pending，S1 PASS/S2 OPEN。无本Task uncommitted product ownership，未知main工作保留。激活时fresh context读最新前项完整接受/视觉/source并补充精确harness。

# Next Action

保持backlog。后续明确授权且所有依赖独立接受/集成/main同步满足才ready→active，声明client_supplement_phase: state_product并登记实际新增验收命令；本次不执行产品。

## 2026-10-10 正式激活与恢复

Human当前直接授权“阅读AGENTS.md，完成下一个task”取代上一轮规划STOP，仅本STATE；UIREF/I18N与S2 Gate不启动。WEB已done/PR29产品a1b154d独立接受同步；PLAN已done/PR31产品9f99独立接受同步；本Agent调用GitHub connector取得PR32实际merged3eaf API原件 pr32-api-original.json，确认行政闭合。assigned root H:/.codex/worktrees/st/IM-platform精确核验，baseline3eaf，初始clean，main未知工作不复制。

Recorder R-STATE-20261010-IMPL，private H:/IM-platform/.git/worktrees/IM-platform43/state-research；prospective_resume/启动前authority读取缺口公开，API非shell用事件绑定，不假称完整命令。基线architecture all/frozen/planning/Recovery Development真实exit0，raw输出留Recorder，不是接受。

实际已定位harness：现有hold_send.py / go_runtime.py / native.py package、Android GUI instrumentation、Web browser与regressions；新增STATE故障联合harness在tests/clients/state/，准备后登记精确argv，不声称未执行PASS。场景A hold-forward导致0消息/0Outbox；B held confirmation必须既有receiver得到与sender FAILED再原retry；顺序/恢复/好友/账号隔离逐端执行，具体计数和PNG绑定candidate。TLS准备入口python -Xutf8 -B tests/clients/state/tls_fixture.py --prepare，只生成受控24h localhost/127.0.0.1证书与计划，不安装Root。Android当前adb无device，既有AVD IMClientSend34 API34可定位；Docker/JDK17/Gradle/MSVC/Cargo可用。旧CA与leaf NotAfter均Oct4，不能通过新验证；新的Root trust/受控overlay执行待精确证书与回滚审查。

当前实现/接受/hosted/integration/sync均PENDING；下一步准备新受控证书与精确联合harness，同时审计unknown commit及friend sync缺口。产品写入只allowed_paths；唯一writer /root/state_impl；同期/root只读协调。无本Task自我接受，S2 OPEN。

## Human scope amendment 2026-10-10

Human answered “按API契约更正” to scope-http-cache-decision.md. Add only clients/web/src/application/http.ts to allowed_paths for removing generic noncontractual response no-store condition. Preserve TLS/request cache/credentials/redirect/strict parser/budget and contractual SyncHttp no-store check. No contract/server authority amendment.

### Current recovery update 2026-10-10 (STATE implementation)
Current authority: Human approved 7-day localhost/127.0.0.1 temporary trust and clarified API contract means current frontend/backend interaction contract. The authorized additional path clients/web/src/application/http.ts has one semantic line changed: generic response cache-control rejection removed; SyncHttp's explicit no-store gate remains.
Current temporary chain: week2 CA SHA256 a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5, CurrentUser Root thumbprint 727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C, NotAfter 2026-10-17T08:58:07.083261Z. Old 24-hour object superseded, old week1 install fully rolled back to original 74-root set. Week2 Root and specified IMClientSend34 readonly CA overlay remain installed only for live controlled acceptance. Finally restore exact root set, exact overlay/mount baseline, adb reverse8443 and root UID, then fresh default-native TLS rejection with live CA-file positive control; no completion before cleanup.
Actual preliminary evidence: Web A/B PASS; Android default SDK TLS positive/hostname mismatch negative PASS; Android A/B state-73fd0288-c4a6-4d25-b99b-90d7131b0819 PASS after real Retry UI viewport correction. Original failed runner/viewport rounds retained. Latest Desktop NSIS installed SHA3529537fc45ae3864c1f7923a4f809da73e2d26e8580469aada61d8c6842416f; actual Windows API login/default TLS/history recovery now observed. sky launch_app and get_window_state each hung ~10 minutes despite requested short timeout; no sandbox-cause inference. Windows API verifies exact owned process40156/window8260804/path and captures full raw1942x1273 after own DPI awareness. All current evidence dirty-source preliminary, not accepted Task PASS.
Remaining: Desktop actual A/B, both R1/R2 order scenarios each client, native FAILED restart/original retry, fresh controlled account DB initial cursor0 history recovery, three real friend-add source directions and disconnect/account-switch/race recovery, source/build candidate binding and final original screenshot manifests/Architect, mandatory behavior/source/hosted checks, independent Review and protected integration/main sync. No UIREF/I18N/Stage Gate activation. Implementation writer owns task branch changes; baseline3eaf256790e9e6b7190326714be3f011edb24401 remains last committed good. Next exact action Desktop actual conversation/send A/B via UIA and live Go fault relay; then remaining actual matrix. Current live own Go project im-gui-product-20261004-35588, proxy8443, emulator-5590/PID4656 require finally cleanup. No clean candidate commit yet; status active, never done.
### Source freeze recovery update 2026-10-10
Preliminary actual Web/Desktop/Mobile A/B and both R1/R2 sequence order scenarios passed, with original earlier failures retained. Desktop preserved FAILED across actual PID restart and original UI Retry; Android host force-stop while runner remained live, new PID and saved FAILED/original request Retry passed. Full Go DB suite passed using a newly created isolated UUID database, then exact database cleanup. Core commit classification conservatively treats transaction/statement resolution unknown, transport/context and other unproven errors as unknown with no rejected ACK; existing deferred-trigger P0001 before persistence and ErrTxCommitRollback are definite rollback, backed by actual DB tests.
Desktop fresh controlled account SQLite absent before login, UserSync cursor0 and conversation afterSeq0, historical seq1/2 and new request seq3 passed. Mobile fresh absence/history seq1/2/3 and new SENT seq4 occurred; capture gate failed because Sent was incorrectly given Retry-height margin. Original failure and visible raw Sent screenshot retained; harness now distinguishes actual Sent row versus Retry row.
Friend preliminary rounds exposed harness username/UI page mistakes, not accepted matrix PASS. Actual Web/Desktop/Mobile new adds occurred, with individual cross-client projections; complete new-group driver is pending. All three disconnect and real account-switch branches are now encoded but unexecuted; new full fixture group only registered. Formal matrix will use committed source/build binding after rebuilding actual Go image for latest Core classification. Native installed source bytes remain current product, but test runner/code freeze binding will be recorded.
Next exact action freeze clean active source/harness candidate, rebuild own live Core/Gateway, restore only own required build outputs, then execute final complete matrix and screenshot manifests. Independent Architect/Review and exact-head selected hosted jobs/main sync remain Coordinator-owned PENDING. week2 CurrentUser Root/AVD readonly overlay remain live and MUST finally be precisely rolled back with fresh default-native TLS rejection and live CA-file positive control. No done or Task PASS declared.


## Resume update 2026-10-10 native cancellation checkpoint

Current native product source is 547514f6c8c8c0c40e27073b67d17bb3f224b6c5. Latest complete friends1e3c matrix remains FAIL after three origins and Web reconnect: Mobile offline retained syncing. Native cancellation repair and Desktop native SQLx before-FAIL/after-PASS are recorded in native-offline-cancellation.md. New installed native formal matrices are pending; old source35d images remain historical. Week2 exact CA/readonly overlay remain installed and must be rolled back with native negative TLS. Remaining verification/review/CI/integration/main synchronization remain required; no acceptance claim. Earlier appended resume attempt failed on GBK decoding and made no task/progress edit; this UTF-8 entry is the recovery record. All task changes belong to state_impl.

## Fresh finalization handoff 2026-10-10

Prior next actions above are historical. Current local mandatory verification is verification-matrix.md / command-index.json, with full original FAILED chain and dual hashes. Product source547514 byte identity and APK packaging qualification remain final-product-binding.json; exact runtime/trust baseline remains final-resource-baseline.json. New source/index-only finalizer corrects matrix argv matching and binds screenshots through original manifest/UIA/source defaults and immutable phase execution, without editing originals. All inherited uncommitted changes are known state_impl ownership and preserved; finalizer owns this finalization. Main781 unknown changes remain untouched. No task acceptance/CI/sync asserted. Final clean candidate/Recovery Acceptance result and own finished Recorder are sealed externally by actual SHA after commit. Next exact action Coordinator fresh Architect and independent Review, then required hosted/protected actualmain/safe sync. Completion Metadata remains PENDING until that real chain.
