---
task_id: LOOP1-GROUP-001
title: 建群、成员添加与三端群聊接入
status: active
owner: /root/group_contract_fix_r5
stage: S2
gate: S2
client_supplement_phase: group_product
---

# Goal

创建者从自己的好友列表选人，创建GROUP会话并自动加入；任意有效群成员均可从本人的好友列表选择新成员加入当前群，好友资格仅针对本次操作者校验。补齐Web/Desktop/Mobile群会话入口、成员与发言者身份展示；复用现有发送、成员鉴权、seq、幂等、ACK、Outbox、分发和Sync，新文案接入现有i18n。依赖I18N及本规划正式接受，位于I18N后/S2 Gate前。2026-10-18 Human 新请求恢复下一任务；依赖核验通过后先交付独立公共契约切片。

# Inputs

- spec/architecture/README.md -> spec/architecture/baseline.md -> spec/architecture/frozen-architecture.md，先核hash；§2.3/§3/§4.3/§5/§6.1/§6.5/§6.6/§6.7/§10 SRC-01 through SRC-07/§11/§15/§19/§20/附录A/B。
- spec/architecture/decisions/ADR-0013-group-planning.md；已接受ADR-0005/0006/0007/0008/0009/0010/0011/0012及其原始接受；spec/governance/minimality.md、execution-boundaries.md、independent-review.md、technology-selection.md、error-handling.md；research/README.md。
- spec/domain/group.md、spec/invariants/group.md、spec/acceptance/group.md全G01..G09；既有domain/invariants auth-user-friend、messaging、sync-plugin；spec/acceptance/client-gui.md、client-supplement.md。
- contracts/http/auth-user-friend.openapi.json、contracts/http/sync.openapi.json、contracts/errors/http-errors.schema.json、contracts/websocket/envelope.schema.json、contracts/websocket/sync-v1.schema.json、contracts/database/及对应golden fixtures；产品激活前重新枚举真实权威及最新main。
- 已接受I18N/STATE三端源码、真实入口harness与截图证据，仅作为基线，不冒充群聊验收。

# Technology Authorization

沿用canonical§6.1与已接受ADR-0005/0006/0009/0011/0012；无新依赖/语言/框架/runtime。Web保持memory-only；Desktop TypeScript拥有Repository/模型/事务意图，SQLx原子native边界不改；Mobile Kotlin/Compose+Android SDK SQLite等价行为，无TS复用强制。ADR-0013仅明确现群功能和最小契约增量，不扩张native职责。
client_language: TypeScript
client_language: Kotlin
client_framework: React
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

# Dependencies

- LOOP1-CLIENT-I18N-001；独立接受、protected integration/actual-main验证及H:/IM-platform安全同步完成。
- LOOP1-GROUP-PLAN-001；本规划正式独立接受、protected integration/actual-main验证及H:/IM-platform安全同步完成。

# Allowed Paths

普通业务按服务职责窄列，allowed_paths不豁免canonical。下面只授予未来GROUP激活后使用；激活时核对路径，确有新增输入先修Task范围，不在实施后追认。无跨服务迁移。

- `contracts/http/group.openapi.json`（建群/加人/本人会话快照；唯一新增HTTP权威）
- `contracts/http/verify-group.py`（标准库/现有validator适配，不新依赖）
- `contracts/http/verify-auth-user-friend.ps1`（现全局 ordered registry 仍精确为原15码原序+GROUP_REQUEST_CONFLICT；本Fix R5仅修 EH-R3-P2-001 的 Get-OpenApiStructureErrors 直接边界：只有 pinned checker 明确 schema-invalid exit1 可计结构拒绝；缺Node/launch失败、内部exit2/37及其他非零/未知异常、ConvertTo-Json内部异常正常传播，使整个verifier非零且不报PASS。保留旧15码业务覆盖、全局16码、6正例/21负例/15 mutations及全部原模型/结构断言；不得修改Auth OpenAPI、JS checkers或旧fixtures）
- `contracts/errors/http-errors.schema.json`（仅已批准群操作必要错误）
- `contracts/database/migrations/0002_group_operations.up.sql`
- `contracts/database/migrations/0002_group_operations.down.sql`
- `contracts/database/README.md`（仅新增migration语义/兼容与回滚）
- `contracts/database/migrate.py`（仅现有独立runner支持0001→0002的有序应用、ledger/status与已冻结回退；保留0001字节、历史checksum、锁及真实失败行为）
- `tests/database/test_migrations.py`（仅上述迁移入口的空库/0001升级/重入/回退/旧fixture兼容正反回归）
- `tests/infrastructure/smoke.ps1`（现Go/Java profile的直接验证边界：EH-R3-P2-003要求ledger SELECT保留ORDER BY version，以保留/转义元素边界的结果精确验证两条且仅两条canonical记录0001_initial、0002_group_operations，大小写/顺序精确；拒绝单条含逗号或换行的unknown version、缺失/额外/重复/乱序/大小写错/native非零，不用另一个有歧义join、过滤unknown或动态接受未来migration。EH-R3-P2-002要求仅检查现owned project cleanup的实际结果，cleanup-only失败使操作非零，body与cleanup同时失败保留两因，环境清理仍执行，全部必需清理完成后才输出PASS。保留role/TLS/WSS/Compose、现资源归属和全部其他检查；不加通用错误/清理/重试框架）
- `tests/e2e/go_tls_messaging.py`（同一首契约切片的现Go S1 strict TLS E2E迁移ledger输入适配：仅SELECT显式ORDER BY version及精确0001_initial与0002_group_operations两项比较；TLS/hostname反例、Auth/成员/ACK/seq/Outbox/Sync/cleanup及原失败传播保持）
- `.github/workflows/ci.yml`（仅在现有shared必需contract步骤接入群verifier与正负suite；保留旧检查、真实非零传播及既有作业选择，不增workflow/job/framework）
- `contracts/fixtures/group/**`（canonical正负/并发/幂等/兼容输入与expected）
- `backend/go/core/group.go`（群权限、事务、快照）
- `backend/go/core/group_test.go`
- `backend/go/core/http.go`（仅现HTTP路由注册）
- `backend/go/core/social.go`（仅现user状态事件/Outbox复用所需最小内部提取，不重写好友）
- `backend/go/core/sync.go`（仅已授权群metadata恢复衔接，分页/cursor语义不变）
- `backend/go/core/outbox.go`（仅现低频群状态通知衔接）
- `backend/go/gateway/http.go`（仅现HTTPS代理路由）
- `backend/go/gateway/group_test.go`
- `backend/go/tests/group*.go`（跨服务黑盒，不放运行期业务）
- `clients/shared/protocol-sdk/src/group/**`（契约传输adapter）
- `clients/shared/protocol-sdk/src/storage/models.ts`（现群metadata类型）
- `clients/shared/protocol-sdk/src/storage/repository.ts`（仅现metadata读写/群身份投影；不改消息写入与草稿）
- `clients/web/src/application/group.ts`
- `clients/web/src/application/http.ts`（已授权群HTTP transport）
- `clients/web/src/application/client.ts`（群操作与现同步编排）
- `clients/web/src/application/repository.ts`（memory群快照/身份，无存储）
- `clients/web/src/ui/components/Shell.tsx`
- `clients/web/src/ui/components/FriendsPanel.tsx`
- `clients/web/src/ui/components/ConversationList.tsx`
- `clients/web/src/ui/components/Messages.tsx`
- `clients/web/src/ui/components/Header.tsx`
- `clients/web/src/ui/components/GroupPanel.tsx`
- `clients/web/src/ui/i18n/en.ts`（群聊键/参数）
- `clients/web/src/ui/i18n/zh-CN.ts`（群聊键/参数）
- `clients/web/src/ui/i18n/ja-JP.ts`（群聊键/参数）
- `clients/web/src/ui/i18n/resources.ts`（群聊键/参数）
- `clients/web/src/ui/style.css`（仅新入口必要现有tokens布局）
- `clients/desktop/src/application/ui/group.ts`
- `clients/desktop/src/application/ui/auth.ts`（现HTTP transport，不改认证）
- `clients/desktop/src/application/ui/workspace.ts`（现群/同步编排）
- `clients/desktop/src/ui/components/Shell.tsx`
- `clients/desktop/src/ui/components/FriendsPanel.tsx`
- `clients/desktop/src/ui/components/ConversationList.tsx`
- `clients/desktop/src/ui/components/Messages.tsx`
- `clients/desktop/src/ui/components/Header.tsx`
- `clients/desktop/src/ui/components/GroupPanel.tsx`
- `clients/desktop/src/ui/i18n/en.ts`
- `clients/desktop/src/ui/i18n/zh-CN.ts`
- `clients/desktop/src/ui/i18n/ja-JP.ts`
- `clients/desktop/src/ui/i18n/resources.ts`
- `clients/desktop/src/ui/style.css`（仅新入口）
- `clients/mobile/app/src/main/kotlin/im/platform/client/group/**`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt`（仅现HTTP transport，无认证语义修改）
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Shell.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Chat.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Friends.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/ConversationList.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Messages.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/Group.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n/**`（仅现纯数据群资源与键）
- `clients/mobile/app/src/main/kotlin/im/platform/client/storage/Repository.kt`（仅现metadata读写/群身份投影；不改消息写入/草稿/SQLite事务adapter）
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/group/**`
- `tests/clients/group/**`
- `tests/contract/group/**`（本Fix R5只新增 `tests/contract/group/test_verification_failures.py`，对上述三项既有验证入口做有意义的实际进程/直接边界故障回归；原test_group.py全部22测试方法、35valid/30invalid对象与helpers保持）
- `tests/integration/group/**`
- `tests/clients/i18n/verify.mjs`（群资源键/参数负例）
- `tests/clients/i18n/compiled.mjs`（群资源键/参数负例）
- `ci/check_s2_planning.py`（仅GROUP phase/完成事实，不能自删Gate要求）
- `tests/architecture/test_s2_planning.py`（对应完成/阻断负例）
- `spec/tasks/backlog/LOOP1-GROUP-001.md`
- `spec/tasks/ready/LOOP1-GROUP-001.md`
- `spec/tasks/active/LOOP1-GROUP-001.md`
- `spec/tasks/review/LOOP1-GROUP-001.md`
- `spec/tasks/done/LOOP1-GROUP-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GROUP-001/**`
- `spec/progress/checkpoints/*group*.md`

以上现有路径及新群文件已明确列举；checker/Reviewer核实，无权增加无关页面、根装配、shared业务、native能力。当前没有schema本地变化依据，不授权native SQLite/schema/Composer改动；如契约冻结后证明必要，先按架构/Task流程处理。

# Public Contract Slice

先建立并独立冻结contracts/http/group.openapi.json：POST /v1/groups（requestId、memberUserIds）、POST /v1/groups/{conversationId}/members（requestId、memberUserIds）、GET /v1/conversations（只返回本人有效会话和群成员最小展示身份）。字段/成功结果/错误码/分页资源界限/关联ID/幂等冲突/权限/兼容负例以contracts/唯一机器定义；本Task仅规定必须交付的入口和语义，不成为第二wire权威。复用既有PublicUser/ID/错误形状；读取不泄露非成员会话，返回GROUP种类、成员userId/真实displayName及可区分身份，含非好友成员；状态事件只提供subjectId/revision invalidation不能代替快照。

建群：(actor,create request)；加人：(actor,conversation,add request)，操作类型分隔；目标集合规范化、去重、至少一人且不含操作者。当前授权校验后，同key同集合返回原始已提交结果，同key不同集合冲突。创建利用现(created_by,group_create_request_id)唯一键；必要最小持久幂等结果支持加人重放，additive0002先定义唯一约束/原结果绑定/回滚fixture，绝不重写0001。旧DIRECT/HTTP/WSS/ACK/Sync/旧客户端保持兼容。若资源或具体shape需扩张批准范围，BLOCKED_BY_ARCHITECTURE提出最小问题。

首个契约切片同时交付0002、现有独立migration runner及tests/database/test_migrations.py必要适配，并把群verifier与tests/contract/group正负suite接入现有shared必需contract步骤。真实hosted证据须证明这两个新入口确实执行并传播非零失败，不能只证明路径分类选中了job。现有Go部署/CI仍通过contracts/database/migrate.py up应用canonical schema，既有compatibility步骤仍执行tests/database；不得由Core启动或群verifier偷偷执行DDL，不改写0001绕过runner。保留0001 up/down原字节及历史checksum、既有checksum不符拒绝、事务advisory lock、ledger原子性和失败传播；0001→0002及空库到0002、重复up、受控回退和旧fixture兼容须实际验证，详见Verification。

契约/runner/回归/现有CI接入作为同一个首契约切片，须clean commit、fresh常规Review→different fresh错误专项→exact-head适用hosted CI→protected integration/actual-main→主目录安全同步独立冻结接受并登记实际contract SHA，才实现Go/客户端；本planning接受不是新公共契约已冻结。中间契约切片不使整个GROUP done。

# Server Transaction and Sync

Core在一个PG事务中按当前Session校验actor；create校验每目标本人好友并加入创建者；add校验GROUP/当前有效成员和每目标本人好友。目标已有有效成员为无新增效果但仍验证其好友资格；任一目标非法全批失败。锁/唯一约束使同key并发与不同request重叠归并，写群/新增成员/持久原结果/所有受影响用户conversation.changed、membership.changed及对应Outbox同事务，COMMIT后才成功。仅实际变化产生逻辑变更；原key重放不产生第二群/成员/事件。注入每写点失败证明全部回滚。

低频事件面向全部当前有效成员含新成员及其所有端；现User Sync触发/轮询/reconnect消费invalidations，以授权会话快照刷新群/成员/非好友身份并按revision幂等。丢NATS由持久cursor恢复，不以消息到达作为唯一发现入口。成员加入后沿当前成员鉴权查询已提交群消息，不引入join-seq限制。消息仍现message.send、seq、原身份幂等、ACK、单Message/单Outbox、Gateway local fan-out和conversation Sync；不新增群WSS envelope。Gateway仅代理，不决定好友/成员事务。

# Three Client Slice

Web/Desktop沿既有TypeScript分层和各端独立React视觉；Android Kotlin/Compose等价adapter。不复制发送/Sync领域机制。各端好友入口选本人好友建群，群内任意成员入口选本人好友加人；可见加载/空列表/验证拒绝/成功/失败/提交未确认、可用原ID重试，失败不能伪装空群或成功；选择/草稿/现发送状态在切语言时保持。群会话列表/成员展示/消息senderId关联群身份，不能只查好友造成C匿名或错认；重名仍可区分。新文案/错误呈现/accessibility放现en/zh-CN/ja-JP纯数据资源，参数和英文回退测试，语言偏好与activation_task固定I18N不改。Web只当前在线页面memory，Desktop/Mobile现按账号SQLite/游标事务收敛。

# Error Handling Review

按治理逐文件inventory当前产品范围/源hash/职责；每finding记录位置/触发/掩盖/最小修复/测试，每保留catch说明具体故障→现依据→真实恢复。事务rollback/资源清理保留根因，未知异常/编程错误/不变量破坏正常传播。超时/response loss/commit unknown诚实未确认，保留原request/targets，不能推定未提交、自动换ID或显示假成功。最终SHA fresh regular后different fresh专项，任一修复两项重做；专项FAIL禁止push/CI-triggering PR。真实错误和根因不得用通用兜底/重试平台掩盖。

# Acceptance

完整spec/acceptance/group.md G01..G09：A-B好友、A建群+B；B-C好友、A-C非好友，B加C；三者各端发现群互发辨认sender。非成员/失效Session/非好友/混合批次/伪造actor/DIRECT拒绝；重复/同key异内容/并发/重叠/已有成员；事务失败回滚、提交前与提交后响应丢失原ID重试；多端同步/离线补偿/账号隔离；现ACK/seq/单逻辑Outbox/成员授权/无gap保持。

三端真实入口测试/原始截图manifest及独立Architect Review→修复重拍→Approval；语言三套键参数/可读性完整。真实Go/PG/NATS/TLS和浏览器/同候选安装Tauri/Android Studio emulator，截图不能代替权限/事务/幂等。各切片与最终产品fresh两审、exact-head actual required hosted jobs、protected integration、actual-main CI/完整树/安全主目录同步有精确SHA证据才done；S2保留OPEN直到全部独立Stage条件另行判定。

# Forbidden

不实现退群/移除/群主管理/邀请审批/链接/二维码/陌生人拉群/群名编辑/已读/新消息类型/每成员持久投递；不加服务/runtime/库/bridge/ORM/通用工作流或错误框架，不提前S3/S4。不改ACK/security/现兼容语义，不绕过契约独立冻结，不扩大搜索/非成员身份访问。未知main工作不复制覆盖；当前只实现下述首契约切片；Go/客户端实现等待该切片独立接受并同步。

# Minimality

直接现Core事务与既有Send/Sync/Outbox，现Group/member/create唯一约束优先；加人原结果在response-loss后需最小持久操作receipt，为当前幂等要求而设，禁止泛化任务系统。一次批次全成全败省去部分成功协议。仅群相关入口、数据与i18n键，无新平台或重构。

# Verification

- Minimum activation baseline：`python -Xutf8 -B tools/verify_frozen_architecture.py`、`python -Xutf8 -B ci/check_s2_planning.py`、`python -Xutf8 -B ci/check_architecture.py --scope all --json`，`python -Xutf8 -B -m unittest discover -s tests/architecture`、`python -Xutf8 -B -m unittest discover -s tests/ci`；已有accepted stage-three checker，不豁免。
- Fix R5三项错误回归：`python -Xutf8 -B -m unittest discover -s tests/contract/group -p "test_verification_failures.py" -v`；实际调用当前PS入口/边界，隔离transport shim只控制外部依赖/原生exit，不作为真实Docker/TLS接受。known structural exit1仍为正常拒绝；初始真实Node正例0后，mutation阶段exit2/37/异常终止/launch与内部异常均令完整verifier非零且无PASS。Go/Java smoke成功、仅primary失败、仅cleanup失败、双失败覆盖真实native退出/两因/环境清理/成功输出时序；精确两canonical记录通过，单逗号/嵌入换行version及缺/extra/duplicate/order/case/nonzero拒绝。新增suite必须在现shared Ubuntu runner已有pwsh/Node下实际执行，不用Windows-only skip、未启用环境或新workflow/job冒充覆盖。
- 现契约回归：`pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1`、`python -Xutf8 -B tools/verify_sync_transport.py`、`python -Xutf8 -B -m unittest discover -s tests/contract -p test_sync_transport.py`、`python -Xutf8 -B contracts/websocket/verify.py`、`python -Xutf8 -B contracts/plugin-api/verify.py`，不删除或压低旧检查。
- 首契约切片（未来交付后执行）：`python -Xutf8 -B contracts/http/verify-group.py`和`python -Xutf8 -B -m unittest discover -s tests/contract/group -p "test_*.py" -v`真实覆盖群schema/正负fixtures，二者须在现有shared必需contract步骤执行并传播非零退出；核对精确hosted SHA/job/step原始日志，不能只核对classifier选择。
- 同一首契约切片的迁移验证：在明确受控、可丢弃PostgreSQL中，配置真实psql/libpq PGHOST/PGPORT/PGUSER/PGDATABASE和安全凭据（不放argv或日志），设置`DB_TEST_ENABLE=1`，实际执行`python -Xutf8 -B contracts/database/migrate.py status`、`python -Xutf8 -B contracts/database/migrate.py up`、再次status及up，并运行`python -Xutf8 -B -m unittest discover -s tests/database -p test_migrations.py -v`。回归分别覆盖空库→0002、保留旧数据/ledger的0001→0002、重复应用无新增、checksum不符拒绝、锁/并发与失败整批回滚；按该切片冻结的回退规则仅在受控库调用现有`python -Xutf8 -B contracts/database/migrate.py down --allow-data-loss`，核对0002的实际schema/ledger回退及重入、旧fixtures/兼容窗口。不得把只测0001当0002覆盖，不新增业务DDL入口。记录0001 up/down原字节SHA-256与历史ledger checksum保持、实际迁移level、命令/启用环境/退出/耗时；现有Go up和compatibility数据库suite的真实hosted执行同样必需。缺PG/psql、未启用或skip均未执行，不计PASS；当前规划轮不运行这些未来迁移/产品检查。
- 未来新增（当前不存在/不可计PASS）：`python -Xutf8 -B contracts/http/verify-group.py`，`python -Xutf8 -B tests/clients/group/verify.py`、`python -Xutf8 -B tests/clients/group/runtime.py --serial <实际独占serial> --capture`。激活后先实现/登记参数、fault hooks/fixture/服务/清理及每G项映射；若命令有变化先Task更新，不能把planned harness当已执行。
- cwd backend/go：`go test ./...`；真实受控PG/NATS使用DB_TEST_ENABLE=1及受控DATABASE_URL/NATS_URL执行group integration/concurrency/fault测试，缺环境skip不是PASS；`python -Xutf8 -B tools/verify_sync_runtime.py`沿现TLS入口。
- `python -Xutf8 -B tests/clients/web/verify.py`、`node tests/clients/web/browser.mjs`；shared/Desktop现`tools/verify_client_send.py --scope shared`和`--scope desktop`、`tools/verify_client_sync.py --scope shared`和`--scope desktop`适用回归。
- Desktop `python -Xutf8 -B tests/clients/gui/native.py package`，Windows现MSVC/Rust/Tauri/locked npm、安装同候选制品并以真实身份运行和截图；host renderer不替代。
- Android `python -Xutf8 -B tests/clients/gui/native.py gradle assembleDebug assembleDebugAndroidTest`，实际独占Android Studio emulator执行group instrumentation及现Send/Sync回归；记录真实serial/API/受控TLS，无私人物理设备/全局trust修改。`tools/verify_client_send.py --scope mobile --serial <实际serial>`、`tools/verify_client_sync.py --scope mobile --serial <实际serial>`仅真实执行才PASS。
- `python -Xutf8 -B tests/clients/i18n/verify.py`及新增群资源负例；screenshot/Architect候选绑定；`pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`，clean committed `-Mode Acceptance`。
- 全部实际命令经Recorder，绑定exit/elapsed/raw outputs；两审/hosted/job selection/actualmain/sync独立证据，不把local/Recorder/截图当最终Gate。

# Evidence

spec/progress/evidence/LOOP1-GROUP-001/；未来contract freeze、G01..G09原始DB/请求/故障/三端入口/截图/Architect/双审/hosted/protectedmain/sync按候选SHA保存。当前仅规划入队，全部产品验收未执行。

# Completion Metadata

acceptance_result: PENDING
accepted_candidate_sha: unavailable
integrated_main_sha: unavailable
main_sync_result: PENDING
independent_review_evidence: unavailable
hosted_acceptance_evidence: unavailable
main_sync_evidence: unavailable

# Handoff

2026-10-20 fresh Fix R5只在assigned root/branch/clean4624完成PHASE1 Task登记，Coordinator独立读回Task a352ce78/rawdiff942d6e及19021其他tracked bytes不变后，明确PHASE2唯一SOURCE WRITE LEASE。现仅两个PS+单新formal文件修复R3三个falsePASS；原schema/checkers/fixtures/22methods/SQL/runner/GoE2E/Go/clients/Frozen/ADR/CI/Gate/旧sealed字节保持。修前6methods14subtestFAIL/exit1保留；修后完整28methods0failure0error0skip/57.550s exit0。旧Auth全局16/旧15码覆盖/6positive21negative15mutations与群35valid30invalid、Sync4/WSS/Plugin保持。真实Go14.735s/Java12.515s/旧strictTLS31.219s全exit0，own容器卷空、原容器身份状态保持。详见新contract/fix-r5/local-verification.json与raw prefix/late ZIP；local不是独立接受。

PG初次identity连接拒绝exit2，未建schema；Coordinator恢复同一实例后，own亲自核PG16.15/data-v2/63830/db/user，再在两次新随机schema验证。最终A3 canonical runner up/status0和actual smoke snippet0；真实count1的comma/newline version都令smoke非零，comma runner known-prefix1/newline未知ValueError1保留；缺表native查询也失败。两次finally均drop own schema、before/after列表相同，credentials只交libpq路径。A2外部helper过强known-prefix诊断假设assert失败原件保留，A3仅外部断言校正，不改runner/重分类unknown。首次Task Permission13/Docker只读API权限拒绝无partial/资源，后精确escalation成功；所有原failure保留。Recorder R-GROUP-FIX-R5-20261020 prospective_resume/partial，startup/helperauthoring/通信/prompt摘录/UTF8重读缺口诚实披露，后续串行drain；最终finish FAIL/structural validate/commit/cleanAcceptance另由外部finalreceipt实际绑定，最终实际结果由sealed receipt绑定；本writer不自评独立接受。

regular_review: NEW PENDING future FixR5 finalSHA (old regularR5 PASS bound4624 only)
error_handling_review: R3 FAIL at462431a45d60d1de0449a35b2fcf698a894d664b EH-R3-P2-001/002/003; DIFFERENT NEW PENDING future finalSHA
hosted_acceptance: PROHIBITED_PENDING_BOTH_NEW_REVIEWS (historical0a9 CI FAIL preserved)
main_sync: PENDING

R3原receipt b083da01148b5cef0b496913358d92efe973e353aee646fdf9b8ec198d046ed7/report f507ea6507ea343e2d904f9f4bb15269ed91a06803712a4aebb2c5644841bcdb/646manifest d5826a824a29b2c7973c4ee536f1fdaf436b56525fad6c957cce8ab1aaab2297及Coordinator核验/phase1批准原件在新original-review-and-scope.zip逐字节绑定。新最终SHA/ownedblobs/lease只从外部 `C:/Users/21441/.codex/visualizations/2026/10/18/01a14d96-146d-7f42-9fd8-0fd0c7e399e0/contract-fix-r5/final-receipt.json`恢复，当前未封存；LKG6f不变。GROUPactive/group_product、S2OPEN、首契约freeze/Go/三端/G01..G09 PENDING。

# Next Action

Coordinator从外部contract-fix-r5/final-receipt.json核实际单fixcommit最终SHA/clean/ownedblobs、Development/clean committedAcceptance、诚实Recorder direct closure及SOURCE WRITE LEASE RELEASED；本writer不publication。NEW fresh常规R6→DIFFERENT NEW fresh专项R4同最终SHA，任何新fix两项重审，两项都PASS前禁止push/CI-triggering PR。之后新exact-head hosted实际requiredjobs/steps→protected integration→actual-main hosted/tree→保存782unknown及2unknowntracked安全主目录同步。首契约独立接受seal/同步完整后才fresh产品Agent登记contract SHA继续Go/三端/G01..G09；GROUP仍active/group_product、S2 OPEN，旧R5常规PASS/旧CI不豁免新接受。

# 2026-10-18 Activation / Contract Candidate

Human 本轮直接指令“阅读AGENTS.md，完成下一个task”恢复 GROUP，不沿用旧规划轮 STOP。
Coordinator 与 fresh recovery Agent 已实际核验 GROUP-PLAN/I18N 的独立接受、精确 hosted、protected main 与保存未知工作安全同步；规划封存3735文件hash/265历史blob/1749语义检查、I18N440证据项均匹配。起点与最后已知良好 main `6f163927334c39c9c8833eb8222335c661bde673`。
唯一 writer `/root/group_contract_impl`，assigned exactroot `H:/.codex/worktrees/group/IM-platform`，branch `task/LOOP1-GROUP-001`。顺序 backlog→ready→active，唯一队列与 status 同步；phase group_product 不改变语言激活 I18N。

本切片限 contracts/http/group.openapi.json、verify-group.py、必要 errors 新码、0002 up/down、database README/migrate.py、tests/database/test_migrations.py、fixtures/group、tests/contract/group、现 workflow shared contract step 两个新入口及本 Task/current/必要新证据/checkpoint。保留0001 up/down字节、历史ledger checksum、原检查/必需job及失败传播；不写 Go、客户端、Frozen、ADR 或旧证据。

POST 输入只 requestId/memberUserIds，身份仅当前数据库权威Session；规范UUID小写/排序/去重后至少一目标、不含actor，每次raw batch最多100。create key(actor,CREATE,request)；add key(actor,conversation,ADD,request)。当前身份与授权校验优先于重放；同规范目标原结果重放，异内容409 GROUP_REQUEST_CONFLICT；非好友/非法群/非成员403，非法结构/自身400。create201含自动actor；add200只返回实际新成员（可为空）。两者原结果字段 requestId/conversationId/addedMemberUserIds/createdAt 持久绑定；createdAt是提交操作的原始记录时间，并非可在COMMIT前确认的wall-clock commit时间。未知内部失败非2xx、结果未知保留原ID，不伪造成功或rollback。

GET /v1/conversations 使用 requestId、limit1..100、成对可选 afterConversationId/afterMemberUserId。按(conversationId,memberUserId)升序分页本人有效会话的有效成员joined rows，逐项含会话kind/createdBy/createdAt及现PublicUser/role/joinedAt；无外群筛选或身份扩权。单页最多100行、hasMore必须有额外已提交行与前进，持续至terminal，不限制群总人数/总页数。每页一致、跨页不宣称冻结全局快照；并发插入落在已读key前须由UserSync invalidation和周期从头刷新补齐。消费端按会话/用户ID合并，非好友成员身份同样可见。

0002只定义窄group operation receipts，保存actor/type/request/conversation/规范targets/原added IDs/原createdAt；CREATE/ADD独立唯一约束，现create唯一键继续有效。成员表不能反推出创建原targets。迁移up按0001→0002在同一advisory-lock事务应用全部pending及ledger；down每次只回退最高已应用版本且需现allow-data-loss，保留旧业务schema/数据至显式回退0001。生产先停止相关writers并备份/评估receipt重试窗口，禁止运行新endpoint时删receipt。旧DIRECT/HTTP/WSS/Sync/ACK兼容不变。

contract_freeze_result: PENDING
contract_candidate_sha: unavailable
regular_review: NEW PENDING
error_handling_review: DIFFERENT NEW PENDING
hosted_acceptance: PENDING
main_sync: PENDING
整体G01..G09/真实三端/Architect/产品接受PENDING，GROUP保持active、S2 OPEN。
本地个人activation baseline：Frozen/planning/architecture-all exit0；88architecture(skip1)/35CI(skip4) exit0。PG/psql尚未可用，真实迁移未执行，不计PASS；现hosted compatibility DB suite及Go迁移up必须实际执行。外部Recorder R-GROUP-CONTRACT-20261018为prospective_resume，startup/directread/helperauthoring/通信不伪造完整trace。
下一动作：完成首契约候选/正负与迁移回归→clean commit→fresh常规→different fresh专项同SHA→hosted→protected integration/actual-main→保存未知work安全主目录同步；之后另fresh实现产品。此writer不push/PR/CI/merge/sync，不将整个Task移review/done。

# Actual verification input adaptation

2026-10-18 首次实际旧Auth verifier退出1：shared error code registry differs from the canonical ordered set。已授权新GROUP_REQUEST_CONFLICT使其硬编码15码全局目录比较失配；复用FRIENDSHIP_STATE_CONFLICT会失真群错误分类，不采用。按本Task原“激活时核对路径，确有新增输入先修Task范围，不在实施后追认”及ADR-0013必要新错误/既有验证接入授权，Coordinator判定这是现验证输入最小适配。先将上述唯一路径/精确责任写入并读回，之后才修改旧verifier。
仅global registry期待旧15码原序+GROUP_REQUEST_CONFLICT；原AUF expectedCodes15及其全部负例覆盖仍完整，群新码由群contract/fixture suite独立覆盖。不改旧Auth OpenAPI/fixtures，不接受任意未来错误码，不以subset替代exact ordered比较。最初FAIL原始输出在Recorder，保留不改；新增输入/实际逻辑由最终SHA两项NEW审查核验。

# Missing original-result compatibility boundary

真实0001可已有GROUP/create identity却无receipt，且过去没有群create公共HTTP调用。新POST遇已有identity而缺可验证原结果，无法证明合法旧来源或异targets，必须保留缺少持久原结果根因，以non-2xx服务器失败结束；不得伪造ErrorResponse/409、猜targets、回填成功或覆盖群。旧群读取/发送保持，新授权ADD仍可行。新操作意外缺receipt同样失败，不正常化为legacy；只有已有可验证receipt同key异targets才409。无marker/回填新机制。最初通信中拟legacy409的过强解释已撤回，未部署该proposal；保留外部原通信/helper，不作accepted事实。该最小诚实失败边界由最终fresh两审核验。

# Current first-slice local outcome

群verifier35valid26invalid与13tests PASS；实际专用PG16.15 final11tests10.397s、8真实integration、0skip，status/up/repeatup/down0002/status/re-up/status均exit0。原0001 bytes/ledger checksum保持，scope proof保护Frozen/ADR/domain/invariants/acceptance/全部Go和客户端旧契约。旧Auth初次registry FAIL保留，先Task登记读回窄scope后仅一comparison适配，再真实PASS；旧15码/21负例/15mutations不削弱。现控制/架构/CI/所有旧契约回归通过，local不是独立接受。
研究run因两处已知post-start只读capture缺口计划finish FAIL，结构validate/0unmatched与完整trace分开，实际最终值由外部receipt绑定；不编辑trace/补造事实。全部Task写入/测试经过Recorder，原direct读取exit1留明。契约双审、hosted、protected integration/actual-main、安全主目录同步以及全部产品G项/截图/Architect仍PENDING。
后续产品实情：writeSocialEvent旧revision固定1不能用于多次群变更；现user_state仅kind/subject/revision且Sequence number|bigint。契约接受后fresh实现先核验实际持久化需要/Task范围，不能把成员JSON藏无关列或投机新增native/schema/新revision平台；稳定前缀、锁序、账号数据游标事务保持。

首次全staged --check因精确复制recovery原receipt的CRLF native exit2（外层PowerShell工具exit1），日志保留。两份本轮原件现以recovery-preflight/originals.zip+bindings.json逐字节保存并核原hash，外部原件不改；仅移除本writer新松散copies，不归一化原件。首次打包helper错误假定native exit1而assert失败，原ZIP已保存，现按真实非零选择器修正；不影响产品/原件。全部候选空白复检另行真实执行。

# Fresh Fix R1 Local Outcome

唯一source writer现为 `/root/group_contract_fix_r1`，exactroot/branch与初始clean5aa已核。R1-P2-001修前原2反例probe exit1（错误接受），修后同原件probe exit0（均明确拒绝）；verifier35valid/30invalid、17tests全PASS。原35正例/26负例对象与13旧test/helper AST完全保持，仅追加4负例/4测试。详见 `spec/progress/evidence/LOOP1-GROUP-001/contract/fix-r1/`；旧独立report/receipt及222artifact manifest哈希已核，旧文件/历史证据不改。

本轮只改verify-group.py、exchanges.json、test_group.py、本Task/current和新fix-r1证据；不改OpenAPI/public shape/0001/0002/runner/Go/客户端/Frozen/ADR/旧wire/旧证据。Recorder初始化unsupported event exit2已披露修正；prospective_resume仍partial，最终finish/validate实际值由新receipt绑定。单个fix commit后两项最终审查均NEW PENDING、CI/sync PENDING；当前finalSHA=PENDING发现路径 `C:/Users/21441/.codex/visualizations/2026/10/18/01a14d96-146d-7f42-9fd8-0fd0c7e399e0/contract-fix-r1/final-receipt.json`，不沿用历史5aa receipt。Last known good accepted/synchronized main仍 `6f163927334c39c9c8833eb8222335c661bde673`。本writer提交后释放lease，禁止push/PR/CI/merge/sync；新独立两审与完整接受仍由Coordinator推进。

本轮current格式初版遗漏既有Command/Result/Evidence标签导致Development exit1，已最小补齐并保留真实FAIL；最终Development/clean Acceptance结果由新final-receipt绑定。研究一次live session与只读git检查重叠也已warning公开，最终structural validation独立报告。

# Fresh Fix R2 Local Outcome

2026-10-18 `/root/group_contract_fix_r2`在assigned exactroot/branch/clean0190核验后获唯一writer lease。专项EH-R1-P2-001原件223hash均匹配；原17tests遇5次内部exit2仍PASS已真实复现。最小修复仅结构检查器明确exit1→Invalid；缺Node、exit2/其他异常码→带exit/stdout/stderr的RuntimeError；launch和未知exceptions原样传播。新增3个回归方法，原17tests/19methods+helpers AST与35valid30invalidfixtures保持；正常20tests和verifier全exit0。相同原fault后original17suite1error/current20suite2errors，每个5formal输入均RuntimeError，不能negativePASS。

JS/OpenAPI/publicwire/errors/SQL/runner/CI/0001bytes、0190完整prefix/lookahead/合法短page、Go/三端/Frozen/ADR/旧证据不改。Frozen/planning/allarchitecture、88architecture(skip1)/35CI(skip4)、旧Auth/Sync/WSS/Plugin通过。PG未改不重复，旧真实11/0skip保留，hosted仍须实际执行。Development/clean committedAcceptance最终命令/exit/elapsed由新receipt绑定。

Recorder为prospective_resume/partial，startup/helperauthoring/通信/封存不完整capture，早期输出截断后定向重读，两次ADR猜名失败后纠正；一次baseline live session与只读检查重叠已warning，后续严格串行。preservation helper初次Windows argv206失败已保留并改用完整delta集合检查后通过。finish诚实FAIL、direct validate另报；研究与产品接受分开。新finalSHA两项freshreviews/hosted/protected/actualmain/sync均PENDING；整体active/group_product/S2OPEN。单个fixcommit之后释放lease，finalSHA/clean/ownedblob/实际Recorder只由新fixed receipt绑定；最后已知良好main仍6f163927334c39c9c8833eb8222335c661bde673。

本Fix r2首次Development真实exit1：current两行Command/Evidence格式不符及子进程选中系统Python2.7；已最小修正记录格式并在本轮runner环境前置既有Python3路径，不改控制检查器。原始FAIL保存，复验/clean Acceptance由最终receipt绑定。

Staged whitespace检查首次失败：本轮新松散JSON以Windows CRLF写出且证据目录保留原字节，git识别CR为尾空白；尚未commit。外部原始probe/Recorder和sealed specialist均不改，新repo证据draft原字节另存pre-stage-originals.zip；松散JSON仅生成逻辑等价LF语义投影，representation-bindings.json绑定原/投影hash，更新索引后重验。此为表示修正，不更改原故障事实。

# Fresh Fix R3 Local Outcome

2026-10-18 `/root/group_contract_fix_r3`先只读startup，在R3封存后收到Coordinator明确唯一SOURCE WRITE LEASE GRANTED；assigned exactroot/branch/clean bca已核，最终R3receipt/report/416原件和actual52 no-renames parent paths逐项匹配。R3-P2-001原4个non-object body合法400交换before真实4AttributeError/exit1，after同封存输入4接受/exit0。

仅verify-group.py读取raw body/query后dict才提取requestId，否则走现uncorrelatable/serverUUID路径；schema/UUID/错误优先级及有合法ID的坏对象关联检查保持。无新增catch，不把unknown context/validator defects变为known400。新增2个参数化方法涵盖create/add/list、实际JSON null/array/bool/number/string及空对象对照、非法状态/码/UUID/伪成功与合法ID坏对象关联。新回归在bca原verifier真实15subtest errors/exit1，修后完整22tests0fail0error；原20tests/22methods+helpers AST、另12个verifier函数和35valid30invalidfixtures字节不变，0190分页prefix/lookahead/合法短页/237成员与bca结构checker故障分类完整保留。

Frozen/planning/allarchitecture、88architecture(skip1)/35CI(skip4)与旧Auth/Sync4/WSS/Plugin均exit0；Development/clean committedAcceptance及最终耗时/实际SHA由新receipt绑定。无PG/schema/runner变化，本Fix不重跑也不声称PG通过；R3独立真实11tests/0skip原件保留，未来hosted仍必需真实执行。wire/OpenAPI/JSchecker/errors/SQL/runner/CI/0001bytes、Go/三端/Frozen/ADR/旧sealed保持。

外部red helper首次非隔离调用遇本OUT inspect.py遮蔽标准库inspect而失败，原始exit1保留；用Python -I排除helper目录后才得到真实15errors，不改产品或旧输出。早期工具展示截断而raw完整保存，局部读取复核。Recorder prospective_resume/partial：startup、helperauthoring/通信/最后packaging与封存非完整capture；finish诚实FAIL、direct validate结构结果由receipt单独报告，trace不编辑。全部post-driver命令串行无same-run overlap。单个fixcommit之后释放lease；新finalSHA常规r4/DIFFERENT专项r2、hosted/protected/actual-main/main-sync全部PENDING，GROUPactive/S2OPEN。

# Deployment verification input adaptation (Fix R4)

2026-10-18 Coordinator先授予PHASE1唯一Task登记lease，落实Allowed Paths原“激活时核对路径，确有新增输入先修Task范围，不在实施后追认”和Public Contract Slice既有独立runner真实部署0001→0002要求。仅登记上述两条验证输入路径；不改Frozen/ADR/公共wire/SQL/Go/clients/CI/Gate或群功能范围，未登记前不实施。

候选0a9f24a38774760e8003e15cc77ff65e3c0d25ac曾经fresh常规r4及different fresh专项r2 PASS，但真实push39115869727/job117641538618和PR39115960616/job117641824783均在Go transport smoke失败：smoke.ps1:60只接受0001_initial，实际合法ledger为0001_initial、0002_group_operations。原raw SHA256分别34fd1cb1e8879f7a9066d25923f2d120acef517a1664090ea81566ef44add247、54a64153e82dd857d02a236d6ec3159150145ac447c601aa736ae91342e09e86；原bindings146d3960cde7d98b0e34ca587d13ecf47b10ca45ab5edc614af709a759fc117c，位于外部OUT的contract-failed-deploy-original-bindings.json，原件保持。

同deploy后续Go S1 strict TLS messaging E2E因前步失败尚未hosted执行；静态核对go_tls_messaging.py:254发现同一旧单项ledger预期，不能称第二hosted失败。外部原snippet与同sql/docker包装注入复现，两处各10例：合法两项在原实现均拒绝；仅在内存proposed比较中接受精确两项，缺失/额外/重复/乱序/大小写错/非零退出仍明确拒绝或RuntimeError。before/proposed报告位于OUT/contract-fix-r4，SHA256分别048cc6f7bad4e3e1a16d1171129c8d2ea4784e3943badb69935ac01fd4eaacd6、6ccea954a2146149d56628a2f4c7d4cf8ccebe0f324bcf45dd589dc01d2049ce。此为隔离注入，不是实际Docker/TLS PASS。

PHASE1读回时脚本仍未修改；Coordinator确认后明确授予PHASE2才实施。仅确定排序和明确两项精确比较，不动态接受未来migration；保留所有原检查/失败传播。后续任何新fix SHA都须NEW fresh常规与DIFFERENT NEW fresh专项后才可publication，再exact-head hosted、protected integration、actual-main及保存未知main安全同步。首契约未冻结、产品G01..G09仍PENDING，GROUP active/group_product、S2 OPEN。

# Fresh Fix R4 Local Outcome

2026-10-18 sole writer `/root/group_contract_fix_r4`先只读恢复，PHASE1 Task先登记/Coordinator独立读回确认后，才获PHASE2明确授权。最终改动仅smoke.ps1两行与Go strictTLS E2E一行，确定ORDER BY version与精确0001_initial+0002_group_operations比较，保留PS LASTEXITCODE/Python RuntimeError及全部原断言。actualsource各10正反注入、真实Go smoke21.281s/Java13.5s/GoE2E29.391s均exit0；各ownproject容器/卷空、既有容器身份状态保持。群35/30与22tests和旧契约完整回归；wire/SQL/runner/Go/三端/旧sealed不改，scope-proof与原件见contract/fix-r4/。

初次镜像站403、首E2E产品stdoutPASS而外部observer失败均原件保留；首E2E childexit/elapsed不可用，不推断整体PASS。仅外部observer修正后新attempt真实child+outer exit0。官方仅缓存同declaredimages并先核canonical缺失，不改版本/daemon/全局trust。Recorder prospective_resume/partial、最初baseline一次overlap及读取/事件/权限失败公开；finish诚实FAIL，最终结构/cleancommitAcceptance/实际SHA/ownedblobs/lease RELEASED只由新finalreceipt绑定。旧0a9两审PASS及两CI总体FAIL不是新候选接受。新常规r5、DIFFERENT专项r3、hosted/protected/actual-main/sync PENDING；GROUPactive/S2OPEN，产品尚未实施。

# Verification Failure Repair Scope (Fix R5, registered before implementation)

本登记依据本Task原“激活时核对路径，确有新增输入先修Task范围，不在实施后追认”、既有独立runner真实部署/精确ledger/失败传播义务、canonical§12及spec/governance/error-handling.md和Minimality Contract。已封存R3三个当前可复现错误：EH-R3-P2-001 unknown checker错误被当schema-negative PASS；EH-R3-P2-002 cleanup native37仍整体0/PASS；EH-R3-P2-003真实PG一条逗号version被join压平为两条canonical而误PASS。原actual source Auth SHA256 faf8a4aab1c724dc51fd19fd39d1e077a83f67057b879029902f3004f9562e07，smoke SHA256 cc1103cd765339c9f26f6ae06c5f807cd32bcecc75aa7dcc08ab870100366700；原failed事实、旧审查/CI/Recorder/evidence均保留。

最小机制只在两个现边界：Auth仅明确exit1产生known schema错误，其他实际失败正常传播；smoke保留元素边界与精确两记录判定（拟使用现PG JSON聚合与现PowerShell解析原语，避免版本text中的逗号/换行别名），owned cleanup检查实际native结果并保留primary/cleanup双因，env cleanup在其finally执行且PASS延至必需清理结束。只在新单一test文件调用实际source/入口作三缺陷回归，不引入通用跨平台/错误/retry框架、依赖或生产test hook。Ubuntu与Windows都执行既有pwsh/Node，环境缺失明确失败，不能skip充PASS。实际实现细节仍由PHASE2和新独立Review核验，不由本Task授权架构/公共contract改变。

PHASE2精确拟写路径：`contracts/http/verify-auth-user-friend.ps1`、`tests/infrastructure/smoke.ps1`、`tests/contract/group/test_verification_failures.py`、本active Task、`spec/progress/current.md`、仅新 `spec/progress/evidence/LOOP1-GROUP-001/contract/fix-r5/**`。保留public Auth/group OpenAPI/JS checkers/errors/fixtures、原22tests/35valid30invalid、0001/0002/runner/GoE2E、全部Go/clients/Frozen/ADR/CI/Gate/旧sealed字节；不实现产品。

退出条件：三个falsePASS的原故障实际失败而known负例/正常成功保持；原检查与全局16/旧15业务码/6正例/21负例/15mutations完整；新formal suite现shared discovery确实执行；真实受控runtime及必要PG记录边界证据清理owned资源、所有原失败保留；source scope/逐字节保护/cleancommit与Development、clean committedAcceptance/Recorder实际结果明确。之后新最终SHA两项fresh独立审查、真实hosted/受保护集成/actual-main/安全主目录同步均PENDING，接受同步前不complete/done，不推进S2。

# Fresh Fix R5 Local Outcome

仅两处现验证边界修复三项R3发现；新增一个formal文件6methods，原22methods/35valid30invalid与公共schema/fixtures/checkers/SQL/runner/GoE2E/Go/三端/Frozen/ADR/CI/Gate/旧sealed逐字节保持。28methods实际0fail0error0skip、旧Auth15mutations与其他旧契约/控制/架构回归、真实Go/Java smoke/旧strictTLS E2E、必要真实PG ledger边界均已执行，完整argv/exit/elapsed及原失败见新fix-r5原件。隔离fault shim不代替真实运行，os._exit86仅快速原生终止，不冒称信号崩溃。未重复无变化全11 migration suite，也不声称本Fix独立DB11 PASS；历史11/0skip保持、未来真实hosted仍必需。

Development/clean committedAcceptance、实际单fixcommit/clean/ownedblobs和Recorder direct finish FAIL/validate结构状态由外部final-receipt.json封存，不提前自称通过。完整trace缺口真实披露，原事件/blob不改。新最终SHA fresh regularR6及DIFFERENT specialistR4均NEW PENDING，两审PASS前禁止push/CI-triggering PR；hosted/protected integration/actual-main/安全同步PENDING。首契约未冻结，GROUP active/group_product、S2OPEN，所有G01..G09与产品仍PENDING。
