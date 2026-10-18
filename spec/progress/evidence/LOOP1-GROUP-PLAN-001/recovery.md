# LOOP1-GROUP-PLAN-001 最终封存恢复

本任务发现说明从属canonical/ADR/contracts与AGENTS，只解析当前规划/行政候选的接受证据；不建立自动接受权威。强制启动后先读固定外部发现文件：C:/Users/21441/.codex/visualizations/2026/10/15/01a1400d-ed56-7fb0-bb81-bc855be6da84/final-group-planning-acceptance-seal.json。当前实现生成时不存在。旧ERROR seal只是本轮恢复前置，不能接受任何群规划新候选。

## 两阶段身份和原件

第一阶段是规划内容候选：task/LOOP1-GROUP-PLAN-001，base86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0；Task review、Completion PENDING、S2 OPEN/GROUP backlog。外部implementation/final-receipt.json绑定实际clean SHA、diff、source-owned blob hashes、本地命令/Recorder/lease，不能代替独立接受。必须由NEW常规Reviewer再DIFFERENT NEW错误专项在同finalSHA PASS；两者未参与实现/Fix，专项未参与常规。任一修复后两审全部重做。随后exact candidate push CI、PR CI、protected integration、actual-main CI/完整tree等价及第一次H:/IM-platform实际安全同步。逐个核对实际head/event/branch/classifier/所有required jobs及steps；缺失/failed/cancelled/异常skip不成立。此diff含ci checker与测试，不能套用后续纯metadata jobs计数。第一阶段全满足后，另一个closing writer才能把本控制Task移done并填写真实第一阶段candidate/main/证据；产品GROUP始终backlog。

第二阶段是上述行政metadata最终候选：独立识别closing writer实际branch/base/finalSHA/diff与外部receipt。其Task done/Completion字段只声称第一阶段接受，current中的administrative_pending仅指新metadata候选。该最终SHA必须重新NEW常规→DIFFERENT NEW错误专项，同SHA且均未实现/Fix候选，专项未做常规；再exact-head push/PR hosted、protected merge、actual-main hosted/tree核验及第二次实际安全主目录同步。不能复用第一阶段两审/CI/同步覆盖metadata新SHA，不能因Task done就跳过。两审PASS前不得push/触发候选PR CI。

封存同时绑定task_id恰LOOP1-GROUP-PLAN-001、两阶段实际candidate/main/PR/branch/diff及完整接受链。沿引用读取实际review报告/receipt、原始hosted jobs/steps/合并guard/Git parents/完整树/两次sync原件；逐项重算bytes/SHA256及Git blobs，不能只接受PASS文字、计数或封存文件存在。第二次actual-main必须是第二阶段protected merge，candidate/main完整tree等价；当前本轮owned source必须与该commit blobs及封存hash逐一相符，未知main工作不应被当作owned或要求全仓clean。两次sync逐项核对head、保存原branch、status、cached diff、782 unknown原bytes/hashes与无关index flags/entries；preflight/PENDING不等于实际应用。Recorder实际finish/validate和trace gaps另核对，结构PASS不是接受。

## 恢复分支

- 缺失：本轮未有完整最终闭环，保留pending，结合已有实际证据从上述链首个未满足动作继续；不因缺seal重做已有精确接受步骤。
- 损坏/身份或字节不匹配/引用缺失：报告具体path/hash/SHA/角色/required job/sync缺口，保持pending，不能吞错或借旧候选PASS。先解决候选身份/owned bytes；若仅外部seal遗漏但所有前置真实证据都独立核实，由Coordinator补外部seal，不改source凑hash。
- 两阶段全部完整有效：仅把此精确候选生成时Task/Handoff/Next Action、current/Blockers/Next Exact Action、checkpoint及handoff的planning或administrative pending解释为当时历史快照；本控制任务规划与行政均闭环。无需递归改写已接受源文件、再提交无限封存。所有旧FAIL、PENDING原快照/Recorder/限制作历史保留；不得据此接受任何字节改变的新候选。

无论分支，LOOP1-GROUP-001保留唯一backlog、client_supplement_phase planned且无产品接受，S2 OPEN/STOP。不得执行群产品/下一任务或评估Stage Gate。恢复证据记录实际seal hash、两阶段精确candidate/main与原件核验结果、首个缺口；本地/Recorder不得充当独立接受。

## R1 修复候选发现（2026-10-15）

原implementation/final-receipt.json绑定的10b39c8已经fresh常规Review FAIL R1/P2，原件review-10b39c8/及manifest保留。后续内容候选实际最终SHA、branch/range/clean/owned Git blobs/本地验证/Recorder/sourcelease请从同一固定外部目录的fix-r1/final-receipt.json解析；它取代原implementation收据作为本次修复候选身份发现，不能替代新finalSHA fresh常规及different fresh专项/hosted/集成/actual-main/安全同步。两审均PENDING；原FAIL不能复用为接受。既有两阶段闭环与所有原历史保持；GROUP backlog/S2 OPEN。

## R2 CI candidate discovery（2026-10-16；最新候选身份入口）

R1收据绑定的bab8已通过两项fresh审查与push全14，但PR两次Go+aggregate gate FAIL；旧两审/CI只历史、原件见ci-fix-r2/history-manifest.json，不接受新字节。当前最新内容候选身份必须从固定外部目录 ci-fix-r2/final-receipt.json 解析；它取代implementation/fix-r1收据作为最新candidate发现，旧文件和既有两阶段流程全部保留。该R2收据绑定实际branch/clean finalSHA/base/range/owned Git blobs/local结果/Recorder/lease RELEASED；不是独立接受。R2仅现Go临时无TLS PG env及7checkout精确绑定，13/13候选refs，生产树不改。

新finalSHA的NEW常规及DIFFERENT NEW错误专项均PENDING，CI/integration/actual-main/安全同步PENDING；任何修复必须两项重审再提交CI，不复用bab8 PASS。Go env方向未经新hosted验证，不能称已解决。source commit后不可再写；后续独立接受及行政闭环遵从上文完整两阶段机制。GROUP唯一backlog/planned，S2 OPEN/STOP。


## R3 Gateway watch 生命周期 Fix 候选（2026-10-18；旧R2仅历史）

当前唯一Task仍LOOP1-GROUP-PLAN-001 review/Completion PENDING；GROUPbacklog/S2OPEN。soleFix /root/group_ci_fix_r3 clean start204e，fullbase及LKG86b。Human窄授权 ci-fix-r3/gateway-watch-scope-approval-20261016.txt 已按字节归档并先更新/读回Task；诊断95artifact核验及旧204e审查/hostedFAIL原件见ci-fix-r3/history-manifest.json。actualserve/auth.bind/watch/真实pgx在途退休旧源码RED原取消panic，唯一watchjoin+必要fixture等待后GREEN，classifier/未知internalmixed失败/ACK/安全不改。

最新候选只能由外部 `C:/Users/21441/.codex/visualizations/2026/10/15/01a1400d-ed56-7fb0-bb81-bc855be6da84/ci-fix-r3/final-receipt.json` 恢复实际finalSHA/branch/range/clean/ownedGitblobs/命令/Acceptance/Recorder与sourcelease RELEASED。不要读取已退休顶层发布别名，不用旧204e或bab8PASS接受新字节。当前新常规Review PENDING、DIFFERENT NEW专项PENDING，二者最终SHA相同；任何Fix两项重新做。两项PASS前禁止push/更新触发CI的PR。

完整Frozen无flag/planning/architectureall及strictscope七backend、254其余产品bytes验证PASS；原--base86b可选zero-product断言与后续Human授权冲突，真实FAIL保持，不改checker。normal/race ./...本地PASS但DB_TEST_ENABLE未设/livePGNATS未执行；dockerdaemon/psql不可用，wire不是数据库。88architecture(1既有skip)/35CI(4既有skip)最终通过，首次缓存相关失败原件保留。Development/clean committedAcceptance最终结果以外部receipt为准；local/Recorder不是独立接受。

接续：NEW常规→DIFFERENT NEW错误专项→exactcandidate/PR实际requiredjobs及真实PGNATSnormal/race→protected integration→actualmainCI/树→保存782未知main原件的实际安全同步；后续metadata候选另需独立闭环。main H:/IM-platform从未写入/采纳/清理，未知work不归Fix。证据ci-fix-r3/handoff.md与local-verification.json；checkpoint2026-10-18-group-plan-ci-r3-review-pending.md。R1/R2/原实施及Recorder/FAIL谱系保持原字节；S2OPEN/STOP。
