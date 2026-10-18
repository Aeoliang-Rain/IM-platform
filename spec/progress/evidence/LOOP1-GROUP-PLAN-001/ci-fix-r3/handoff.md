# R3 Gateway watch 生命周期 Fix（未独立接受）

当前唯一 Task LOOP1-GROUP-PLAN-001 仍 review/Completion PENDING；GROUP backlog/planned、S2 OPEN。R3 sole writer /root/group_ci_fix_r3，assigned exact root H:/.codex/worktrees/grp/IM-platform，branch task/LOOP1-GROUP-PLAN-001，clean start204e803724c2a64514c6e14f8d1ed86cabca8acb，full-range/LKG86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0。最终 clean SHA/Acceptance/Recorder/sourcelease RELEASED 只从外部 ci-fix-r3/final-receipt.json 恢复；本 Fix 不 push/PR/CI/merge/sync。

## 授权、故障与最小修复

Human 原文 gateway-watch-scope-approval-20261016.txt 已byte-exact归档；Task inputs/allowed_paths/Forbidden/verification/error范围在 backend 写前修订并读回。95诊断 artifacts 全部hash复核；必要原件/history-manifest保留，旧204e双审和push14PASS仅历史，PR38859630177 attempt1 normalPASS/raceGo+gateFAIL不构成新接受。

唯一生产文件 gateway.go：serve 保存其唯一已启动 watch 完成 channel，goroutine defer close；serve 返回前先 connection.close 再 join。watch 原1s deadline、错误值、watchTransportFailure逐分支分类和panic均原样；watch自己close不join，避免self-wait。未知/internal/mixed正常失败，不把context.Canceled变网络，不recover或忽略故障。其余六文件为一个真实回归及五直接fixture调用处的test-only注册/完成等待。mutex同时保护admission停止和active计数，Cond等待全部已开始handler，避免WaitGroup Add/Wait竞态。原client defer/t.Cleanup在server等待前，等待在pool.Close前；失败退出同样经过既有defer/cleanup。httptest.Close本身不追踪hijacked，故该最小包装当前有必要；无新publicAPI/http.go/依赖/框架/通用lifecycle。

回归在实际serve上成功auth.bind，真实pgx第二constructor收到StartupMessage后阻塞，关闭peer，等handlerDone，再pool.Close。旧生产实际RED exit1，子进程原context canceled panic；新生产同命令GREEN。受控wire仅一行session供bind和后续在途startup，不能冒充数据库。原closedpool/internal/mixed、取消分类和known expiry负例保留；真实PG异常watch子进程测试原字节未改。

## 本地验证与限制

local-verification.json记录真实argv/退出码/时长/raw hash和输出发现；local-output来自Recorder redacted blobs，不把blob digest冒充raw stdout hash。normal/race ./...本地exit0但所有DB_TEST_ENABLE条件skip明确未执行；docker info exit1，psql不可用。真实PG/NATS原normal/race必须之后hosted执行，不能用wire或本地PASS替代。88architecture(1既有OSskip)、35CI(4既有OSskip)最终通过；首次nested Go GOCACHE失败完整保留。首次Go默认缓存权限失败也保留。

原--base-commit86b可选零产品断言在授权改变后不适用，实际exit1保留；不带flag的全部Frozen/hash/ADR/authority结构检查PASS。scope-proof.json独立比较真实base86b与start204e，以及最终工作bytes：261产品路径中仅获授权7路径变化，254其余backend/clients/plugins/deploy/contracts逐路径及bytes保持；Frozen/ADR/checker/workflow/GROUP Task保持start。没有修改checker或现有负例以放行。最终同SHA两审须核验此适用性及原授权。

current/Task/checkpoint真实本地结果与最后已知良好86b保持；clean committed Acceptance提交后只存外部收据，避免自引用。Development实际exit0；提交后Acceptance结果以最终外部receipt为准。首次startup/skill/helper外部写入/通信未被run-command覆盖，prospective_resume明确trace incomplete；无老stream编辑。Recorder仅研究，不提供Task或Gate接受。

## 接续

NEW fresh regular Review → DIFFERENT NEW fresh错误专项，同一最终SHA两项PENDING；任何Fix均重做。两项PASS之后才exact-head candidate/PR实际required jobs → protected integration → actual-main CI/树 → 保存main782未知原件的实际安全同步。metadata收尾候选仍另需完整独立闭环。H:/IM-platform全程只读，未知work不采纳。GROUP backlog/S2 OPEN。

## 原始证据空白检查适用性

可选全文件 `git diff --cached --check` 对按字节保留的 history/Recorder 原始 CRLF/空白报 exit1；原件不改。仅代码及控制文件独立 --check，不能称全文件 PASS；正常 commit hooks/Acceptance 不绕过，原失败在外部 Recorder 收据。
