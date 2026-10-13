# Independent candidate Review checklist

This checklist executes canonical §12-14/§21 and SRC-01 through SRC-07; it does not redefine architecture/contracts. A fresh Review Agent who neither implemented nor fixed the candidate reads unique current task, canonical hash/ADRs, task inputs, Minimality Contract and diff. Record independence, exact reviewed SHA/branch/range and clean committed checkout method. Renaming roles is not independence.

- Check behavioral fixtures, transaction/ACK/Session/epoch/Sync invariants, authorization, security negative cases and actual live test enable conditions/skips. Tokens/passwords cannot appear in query, logs, traces or errors.
- Inspect real service responsibility, root assembly whitelist, shared support semantics and runtime import graph against canonical §3/§10/§11. Reject cross-service internal imports, shared reverse imports, full Auth hidden in shared, business disguised as tests or task globs treated as waivers.
- Check exact write scope, migration file/responsibility map, temporary authorization/exit and effective positive/negative structural checks. Directory/file names and observable equivalence alone are insufficient.
- Apply separate backend stages. Java placeholder rules apply now; future Java business uses canonical boundaries and expiry, never Go layout. Stage003 exposes old Go deviations for stage004, not grandfathering.
- Review interfaces/exports/dependencies against present responsibility and Minimality Contract; no speculative layers or future infrastructure.
- Verify task queue/status uniqueness, dependencies, recovery and evidence; preserve historical PDF/done/checkpoints/Recorder. Check current accepted baseline discovery.
- Verify exact final candidate hosted head, changed-path job selection and actual required conclusions. Execution-rule Markdown changes require applicable checks; missing/failed/cancelled/anomalously skipped jobs fail acceptance. Old CI and expired ADR-0001 cannot substitute.
- Distinguish bounded stages from product, batch and S1 Gate. Stage003 checker effectiveness can pass while old Go fails; final migration must pass applicable structure/live regression.

FAIL remains unfinished: fresh Fix Agent repairs within authorized scope, then a new Review Agent reviews the candidate. Local independent PASS still requires applicable hosted CI before closure. An irreducible authority conflict blocks its dependent portion and records the smallest decision question.

## Technology authorization

Read `spec/governance/technology-selection.md` and canonical §2.3 / §6.1 before implementation or Review. Every new architecture-sensitive language/framework/runtime/core dependency requires traceable accepted Frozen Architecture / approved ADR authority. Missing decision: stop affected work BLOCKED_BY_ARCHITECTURE -> smallest question -> Human/Architect decision -> freeze -> fresh independent Review/applicable exact-head hosted CI -> implementation. Task text/allowed_paths/tests cannot approve selection. Reviewer FAIL on absent authority; inspect real imports/native responsibility beyond static guards. Desktop native SQLite is explicitly Tauri + SQLx(SQLite) with atomic transaction adapter; TypeScript holds Repository/models/transaction intent. No separate tauri-plugin-sql execute-call transactions. Mobile is Android Kotlin + Jetpack Compose, validated on Android Studio emulator. Mobile models/Repository/protocol/plugin adapters implement equivalent behavior under the same canonical contracts/fixtures; direct TypeScript SDK reuse is not required. Web/Desktop/shared stay TypeScript. Android SDK/Gradle/Kotlin/Compose engineering identifiers do not authorize Room/ORM/network libraries, JS runtime/bridge/codegen or shared native rewrite.

## 提交 GitHub CI 前的错误处理专项审查

常规独立 Review PASS 后，按 [error-handling.md](error-handling.md) 委派一个全新、未参与当前候选实现/Fix/常规 Review 的 Agent；两项都覆盖最终候选 SHA。检查无依据防御/兼容、空 catch/默认假数据/Promise 忽略、未知异常分类失真、日志后未恢复、重复捕获/包装/根因丢失，核对逐文件 inventory 与每个保留 catch/回退依据。证据须含身份/独立性、SHA/branch/range、clean committed checkout、命令/退出码/时长、结果/发现/保留理由。

专项 FAIL 禁止 push 或创建/更新触发该候选 CI 的 PR；新 Fix → 新常规 Review → 新专项 Agent 循环，不能沿用旧 SHA PASS。此环节只设在提交 GitHub CI 前，不能替代 hosted CI、protected integration、actual-main 或安全主仓库同步。权威冲突按既有架构流程停止受影响部分。
