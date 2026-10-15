---
task_id: LOOP1-GROUP-PLAN-001
title: S2 群聊架构与任务插入规划
status: review
owner: /root/group_fix_r1
stage: S2
gate: S2
---

# Goal

以本轮 Human 请求为明确架构修订授权，冻结最小建群、任意有效成员从本人好友加人及三端群聊接入决定；新增 LOOP1-GROUP-001 backlog，置于 I18N 后、S2 Gate 前。本轮仅规划及独立接受、精确 CI、受保护集成、actual-main 核验和 H:/IM-platform 安全同步；不实现群聊，S2 OPEN。

# Inputs

- spec/architecture/README.md -> spec/architecture/baseline.md -> spec/architecture/frozen-architecture.md，核验 SHA；§2.3/§3/§4.3/§5/§6/§10 SRC-01 through SRC-07/§11/§15/§19/§20/附录A/B。
- 已接受 ADR-0005/0006/0007/0008/0009/0010/0011/0012；spec/governance/minimality.md、execution-boundaries.md、independent-review.md、technology-selection.md、error-handling.md；research/README.md；spec/tasks/TASK_TEMPLATE.md。
- spec/domain/auth-user-friend.md、spec/domain/messaging.md、spec/domain/sync-plugin.md；spec/invariants/auth-user-friend.md、spec/invariants/messaging.md、spec/invariants/sync-plugin.md；spec/acceptance/client-gui.md、spec/acceptance/client-supplement.md；contracts/只读。
- spec/progress/evidence/LOOP1-GROUP-PLAN-001/human-request.txt 和 recovery-verification.md；最新 accepted main 86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0；前任务 accepted-product/recovery.md 的最终封存恢复已由 Coordinator 完整核验。

# Technology Authorization

控制面仅现有 Python 标准库/PowerShell；产品继承 canonical §6.1、已接受 ADR-0005/0006/0009/0011/0012。无新语言、框架、runtime 或依赖，本轮不写产品。

# Dependencies

- LOOP1-ERROR-HANDLING-001；最终行政封存完整核验，protected PR41 actual main 86b41e4d、actual-main CI 与安全主目录同步完成。
- LOOP1-CLIENT-I18N-001；既有接受保持，不重开产品。

# Allowed Paths

allowed_paths 是硬边界，不豁免架构；Human 本轮明确授权以下规划修订，不授权本轮产品实现。

- `spec/architecture/README.md`
- `spec/architecture/baseline.md`
- `spec/architecture/frozen-architecture.md`
- `spec/architecture/decisions/ADR-0013-group-planning.md`
- `spec/domain/group.md`
- `spec/invariants/group.md`
- `spec/acceptance/group.md`
- `spec/acceptance/client-gui.md`（仅群聊验收承接及 S2 依赖）
- `spec/acceptance/client-supplement.md`（仅当前 I18N→GROUP→S2 依赖）
- `spec/tasks/backlog/LOOP1-GROUP-001.md`
- `spec/tasks/active/LOOP1-GROUP-PLAN-001.md`
- `spec/tasks/review/LOOP1-GROUP-PLAN-001.md`
- `spec/tasks/done/LOOP1-GROUP-PLAN-001.md`
- `spec/tasks/done/LOOP1-CLIENT-I18N-001.md`（只追加后继说明，旧证据不改）
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GROUP-PLAN-001/**`
- `spec/progress/checkpoints/*group-plan*.md`
- `ci/check_s2_planning.py`
- `tests/architecture/test_s2_planning.py`
- `tests/architecture/test_frozen_architecture.py`（authority fixture 携带新 approval）

# Error Handling Review

本轮生产范围为空；现有检查器为唯一可执行变更。逐文件检查真实解析、依赖和失败传播。保留 catch 仅将具体 I/O/非法 authority/结构失败显式报告 FAIL，不伪造成功或空集合。fresh 常规 Review PASS 后，另一个未参与实现/Fix/常规 Review 的 fresh 专项审查同一最终 SHA；任何修复 SHA 两项重做。两项 PASS 前不得 push/创建或更新触发 CI 的 PR。

# Acceptance

每项 Human 需求在 ADR、canonical、domain/invariants、acceptance、未来 Task 的公共契约交付、事务、同步、三端入口/i18n、路径及验证中可追溯。负例证明 GROUP 未独立接受并安全同步则 S2 阻止；language activation_task 精确绑定 I18N，禁止用末项推导。保留旧 S2 条件及历史。fresh 两审、精确候选实际 required hosted jobs、protected integration、actual-main CI/树核验及保存未知 work 的安全主目录同步均完成后本控制任务才允许 done。群聊产品 backlog、S2 OPEN，停止。

# Forbidden

不改 contracts/backend/clients/plugins/deploy 产品及依赖，不实现/激活 GROUP，不评估或宣告 S2 Gate；不覆盖或采用 main 未知改动，不重写旧任务/FAIL/Recorder/PDF。不把 local/Recorder PASS 写成独立接受，不填写未来接受 SHA/PASS。

# Minimality

一个规划控制任务、一个产品 backlog、一个 ADR，直接扩展现有标准库 checker。幂等收据只为已确认响应丢失/并发需求，未来产品优先现有 schema 必要增量。无新服务/通用编排/角色管理/邀请系统/错误框架。

# Verification

- Existing executable recovery entry points: `tools/verify_frozen_architecture.py` and `tools/verify-loop1-ctrl-002.ps1`.
- Minimum baseline: `python -Xutf8 -B tools/verify_frozen_architecture.py` 及 `python -Xutf8 -B ci/check_s2_planning.py`：起点 86b41e4d 实际 exit0。
- `python -Xutf8 -B tools/verify_frozen_architecture.py --base-commit 86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0`
- `python -Xutf8 -B ci/check_architecture.py --scope all --json`
- `python -Xutf8 -B ci/check_s2_planning.py`
- `python -Xutf8 -B -m unittest discover -s tests/architecture`
- `python -Xutf8 -B -m unittest discover -s tests/ci`
- `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`；clean committed 同入口 `-Mode Acceptance`。Windows bundled Python3 目录仅加到子进程 PATH。
- 实际 classifier 决定 exact-head hosted required jobs；核对实际 event/head/branch/job/step，不把 aggregate CI gate 等同 S2 Stage Gate。

# Evidence

spec/progress/evidence/LOOP1-GROUP-PLAN-001/；外部 implementation/research run R-GROUP-PLAN-IMPL-20261015 resultFAIL/structural validate exit0但一个unmatched command；related resume R-GROUP-PLAN-IMPL-RESUME-20261015，parent R-GROUP-PLAN-COORD-20261015。local/Recorder 不是独立接受。

# Completion Metadata

acceptance_result: PENDING
accepted_candidate_sha: unavailable
integrated_main_sha: unavailable
main_sync_result: PENDING
independent_review_evidence: unavailable
hosted_acceptance_evidence: unavailable
main_sync_evidence: unavailable

# Handoff

当前唯一Fix writer /root/group_fix_r1；assigned exact root/branch已核验，起点clean10b39c8688588c94f95a9a3d671b8496e076fcdf。原常规Review该SHA为FAIL，仅R1/P2（未来runner/迁移回归/现CI接入路径缺口）；原report/findings/receipt与必要原始输出按字节保存review-10b39c8，manifest绑定external全部168 artifacts。最小修复仅GROUP backlog范围/首契约切片及真实验证、group验收同义承接和原始截图SHA-256措辞，未写产品/契约/runner/CI/Frozen。新最终SHA常规Review PENDING；different fresh错误专项PENDING；hosted/integration/main/sync PENDING。本轮Fix frozen(base86)/planning/architectureall exit0，88architecture(1既有Windows skip)/35CI(4既有OS skip)通过；Development初次exit1仅current Verification字段格式，修复后重跑exit0，原失败保持。完整命令/时长/gap见fix-r1/handoff.md和local-verification.json；实际提交SHA/clean Acceptance/owned blobs/Recorder完成及source lease RELEASED以外部fix-r1/final-receipt.json绑定。旧10b39c8 FAIL保持，不复用为接受。

以下为原实现历史handoff：唯一 writer /root/group_plan_impl。已验证 assigned exact root H:/.codex/worktrees/grp/IM-platform，branch task/LOOP1-GROUP-PLAN-001，latest main 86b41e4d clean。前任务 seal 81a829add56ab8cefc497096ba0823df082cf4cad051fb35d3786afe28a578af 由 Coordinator 完整核验，摘要固定引用，不复制旧巨量证据。本地frozen(base86)/planning/architectureall、88architecture tests(1既有Windows skip)、35CI tests(4既有OS skip)、Development实际PASS；详见implementation-handoff.md与local-verification.json。新候选两审/hosted/main/sync PENDING。最终 clean SHA/本地验证/Recorder/source lease 由外部 implementation/final-receipt.json 绑定。

# Next Action

Fix提交clean新候选、执行Acceptance并释放唯一source lease后停止写入；Coordinator从外部fix-r1/final-receipt.json恢复实际最终SHA。新最终SHA须NEW常规Review → DIFFERENT NEW错误专项，两项均PENDING；旧FAIL不能接受新候选。两审通过后 exact-head CI → protected integration → actual-main → safe main sync。任何 Fix 两项重审。后续独立 closing writer 只记录真实接受/集成 SHA，metadata 候选再独立闭环；不得递归改写已接受 source。GROUP backlog/S2 OPEN，STOP。
