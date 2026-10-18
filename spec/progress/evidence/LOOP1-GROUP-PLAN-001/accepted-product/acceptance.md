# 第一阶段规划及授权修复接受发现

第一阶段已独立接受并实际安全同步：candidate `c7d3d8bfeb5a4742ae06e0ac2d792215bcb3a0e2`，base `86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0`；正常受保护 [PR42](https://github.com/nilesthump/IM-platform/pull/42) 合并到 actual main `45b0a8512da4e505c467a6120cf2fc2cdd0bac7f`。本发现仅记录真实已完成的第一阶段，不接受本次行政 metadata 新字节。

- fresh 常规 `/root/group_regular_r3` 与 different fresh 专项 `/root/group_error_r3` 同 c7，未实现/Fix；原 receipt/report/manifest 与 findings 的小副本及完整外部原件绑定见 [independent-reviews.json](independent-reviews.json)、[copy-provenance.json](copy-provenance.json)。实际96/260个manifest原件全部逐项重算bytes/SHA-256，未复制其全部输出。
- exact push39097442700 attempt1 的实际 before 是204e，6个selected成功、7个正常inactive、13个job objects；PR39097445982及actual-main39098036604 attempt1各14/14成功。所有必需step成功，3个Desktop平台step为既有OS适用性skip；34个successful job实际checkout原log均为对应精确SHA。真实PG16/NATS、DB_TEST_ENABLE=1、临时PGSSLMODE=disable和normal/race ./...包结果已核实；[hosted-acceptance.json](hosted-acceptance.json)绑定原始jobs/steps/checkout logs，未重复拷贝巨量日志。
- main parents恰86b、c7；candidate/main完整tree均`9e41a42cc790619bd258213636bb61b543a68a56`。strict gate/enforce-admins、exact head及正常无admin bypass合并原件被hash绑定。
- [planning-main-sync.json](planning-main-sync.json)为第一次实际APPLY后的PASS收据，main86b→45b、190paths，head/branch/status/cachedDiff/unknownBytes/unrelatedIndexFlags/unrelatedIndexEntries/acceptedTree八项均true；原782未知文件和recovery/s1-handoff-20261001分支保存。原[planning-acceptance.json](planning-acceptance.json)生成于同步前，其safeMainSync PENDING/taskDone false为真实历史快照，由后续实际sync收据补齐。closing writer仅读main HEAD/branch，未读采纳或修改未知原件；第二次同步由Coordinator另行执行。

原五处Recorder轨迹缺口：IMPL14/13原FAIL、REGULAR-R2-RESUME28/27原FAIL、REGULAR-204E80336/35原PASS、CI-FIX-R3 42/41原PASS、ERROR-R3 42/41原FAIL。第五处unmatched `C-500885b6-7109-4df4-b95a-aff3c3570468`，rg WinError5外层exit2、stderr37bytes SHA-256 `d88aacd35d32adcc8179ba77067b72dcc59e1af9b437ce908cc7119d2a8ce442`。structural validate0不代表完整trace；专项产品PASS与RecorderFAIL分开。旧事件、FAIL和raw CRLF whitespace失败保持。原Frozen可选--base86b零产品断言因后续Human七路径修复授权而exit1，checker不改；完整无flagFrozen/strict七backend路径及其余254产品bytes证明已两审/hosted核验。

本轮没有GROUP产品契约、迁移或实现；三端真实群入口/原始截图/Architect是未来GROUP任务G01..G09要求，未执行。GROUP唯一backlog/planned；语言activation仍I18N；S2 OPEN/STOP。

当前行政候选base45b、sole writer `/root/group_plan_close_r1`，仅Task队列/Completion/Handoff/NextAction、current、此NEW证据目录、recovery追加和NEWcheckpoint。两项NEW审查、exact-head push/NEW PR CI、protected merge、actual-main/tree及第二次安全同步全部PENDING。最终source SHA/本地命令/clean Acceptance/Recorder/lease从固定外部`closure/final-receipt.json`恢复；不得复用c7接受新bytes。最终两阶段seal缺失时不能宣称完整封存，按[recovery.md](../recovery.md)恢复，不递归改已接受source凑SHA。
