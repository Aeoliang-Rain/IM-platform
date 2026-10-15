# LOOP1-ERROR-HANDLING-001 最终行政封存恢复

本说明仅执行当前 Task、AGENTS 与现有独立接受要求，从属 Frozen Architecture / ADR / contracts / domain / invariants / acceptance；不建立新产品权威、公共 schema 或自动接受机制。完成强制启动读取后、执行任何行政 Next Action 前，先检查固定发现文件 `C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/final-error-handling-acceptance-seal.json`。本修复生成时该文件不存在；下述完整有效分支只是恢复条件，不是未来 PASS 声明。

## 核验顺序

1. **身份和当前字节。** 读取封存全文及实际引用原件，核对 Task 恰为 `LOOP1-ERROR-HANDLING-001`、产品 `63f685d1b959b318f97d804f40af49d61aa3f273` → 历史产品 main `1cab3dc4c9180bfe6a6654fde028a0354faf8a4c`，与本目录既有 product receipts / copy-manifest / 原始证据一致。另独立识别最终行政 candidate、其 base/diff range、记录的 task branch `task/LOOP1-ERROR-HANDLING-001`、新 protected PR / actual-main SHA；不能拿产品或旧行政候选 PASS 覆盖新行政候选。最新 Fix candidate/clean checkout/source lease 由外部 `fix-admin-resolver/final-receipt.json` 绑定；旧 `admin-error-close/final-receipt.json` 与 FAIL `16584b7` 是谱系。逐一重算封存引用的收据、报告、命令输出及所列 artifacts 的 bytes/SHA-256，沿引用核对原件与实际 Git commit/blob、branch/head/diff，而非只读汇总 PASS。缺原件或不一致必须显式失败。
2. **两个阶段各自的审查与 CI。** 产品历史仍须绑定其两个不同 fresh regular/specialist、精确 product SHA 和既有限定证据。行政两个 PASS 必须来自两个不同全新上下文，先 regular 后 specialist，二者都未实现/Fix 最终候选，specialist 也未做 regular；检查身份/独立性、同一个最终 candidate SHA、branch/range、clean committed 方法与实际 findings/result。任意修复的新 SHA 必须重做两项；无两项 PASS 不得 push 或创建/更新触发 CI 的 PR。检查实际 hosted run 的 event/head/branch/classifier、每个必需 job 及实际 steps：产品 push `38732968440`、PR `38733066327`、历史 main `38734397144` 各14 jobs 成功，只有已记录的正常 OS 条件 step skips；新行政 push、PR、actual-main 各自匹配各自精确 SHA，按最终 diff 的实际分类核对。当前纯行政预期5 selected（classify/architecture/source_go/source_java/gate）成功、8 classifier-false 正常 inactive；若最终 diff 改变则按实际必需集合，不能硬套此计数。缺失、failed、cancelled 或异常 skipped job/step 都不成立；旧 run 或 summary success 不能替代。
3. **实际集成和第二次同步。** 对照实际 PR 合并响应、protected guard、Git parents 与完整树：行政 PR head 必须是两审及 candidate CI 的最终 SHA，actual-main 必须是其实际 protected merge，行政 candidate 与该 main 完整 tree 相等。原产品 main1cab 是历史接受点，不要求它等于后来 remote HEAD。核对第二次实际 `H:/IM-platform` 同步收据及前后原始 snapshot，目标为这个新行政 actual-main；head、preserved branch、status、cached diff、782 unknown 原始文件 bytes/hashes 与无关 index flags/entries 六项实际检查均满足，不能以 preflight/PENDING 代替实际应用。允许从干净 assigned candidate 或相等的 actual-main 整合树恢复；核对记录的 candidate branch，而不要求当前主仓库 checkout 改成 task branch。主仓库保留 `recovery/s1-handoff-20261001`、两处未知 tracked edits/782 unknown 正常，不要求全仓 clean，不覆盖它们。当前任务自己拥有的 source bytes 必须等于封存所绑定 candidate/actual-main committed blobs；若这些字节已改变，旧 seal 不适用于新候选。Recorder finish/结构校验、真实 trace gaps 和缺失命令结果单独核对、如实保留；它们不是产品接受或门禁替代。

## 三种恢复结果

- **缺失：** 保持 `administrative_closure_pending`；读取现有候选收据和后续真实证据，定位下述链上首个未满足步骤，不因无 final seal 重做已被精确证据接受的步骤。
- **存在但损坏、身份/SHA 不匹配或证据不全：** 明确报告具体失败/缺少的路径、hash、身份或步骤，保持 pending；只承认仍可独立核验的精确候选证据，从首个未满足步骤继续。若不能绑定候选/当前 owned source，先解决该身份或字节冲突，不能复用旧接受；若仅最终封存遗漏而全部前置已证实，由 Coordinator 修复外部封存。绝不静默忽略错误或将存在/PASS 单词当接受。
- **全部完整有效：** 恢复为本 Task 产品与行政均已闭环；仅将这个精确 candidate 生成时 current 的 Batch/Execution/Blockers/Next Exact Action、Task 当前 Handoff/Next Action、checkpoint 与 acceptance 的行政 pending/重复双审/CI/sync 指令认作已完成历史快照。无须递归改写已接受 source 或再次提交一轮行政闭环；旧 FAIL、pre-sync PENDING、历史 Task/evidence 与所有限制仍保留，不据此改写历史或给任意新候选接受。

未完成链为：候选身份/owned bytes与clean committed本地记录 → NEW regular → DIFFERENT NEW specialist（同最终 SHA）→ exact candidate push CI → PR CI → protected merge → actual-main CI → 第二次实际安全同步 → 最终外部封存及引用核验。对首个缺口执行既有流程；审查/CI失败进入 fresh Fix 与两项新审查，禁止跳过后续步骤。此顺序是现有流程的本任务发现说明，不放宽任何上位要求。

三种结果始终保留 S1 已接受、S2 **OPEN** 和 Human 当前停止边界：不得选择下一任务、启动后续产品或评估/宣布 S2 Stage Gate。无效行政封存本身不撤销另有完整证据的产品历史接受。恢复结论应记录实际已核验 seal hash、精确 candidate/main、证据路径与首个未完成动作；本地或 Recorder PASS 不得写成独立接受。
