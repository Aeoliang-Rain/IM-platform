# 最小待授权范围提案（未实施）

决策问题：是否授权一个独立、窄 Go 生命周期修复切片，只纠正“已启动的 Gateway safety watch 尚未结束，fixture即释放其pool”这项已复现的所有权缺陷？现 LOOP1-GROUP-PLAN-001 Forbidden backend，必须先授权scope；不是Frozen/公共契约新机制决定。

最小设计候选：gateway.go 的serve记录其唯一watch goroutine完成channel，goroutine defer关闭完成信号；serve返回前先按现逻辑connection.close，再等待该watch结束。watch继续使用原1s deadline、原错误返回和helper/panic；不把c.done取消产生的Canceled变为成功，不新增recover。这样父handler完成才真的包含其watch完成。暂不新增公开NewHandler接口；有待新的实现者论证并验证。

直接相关fixture用test-only handler completion包装记录开始/完成并在关闭client后等待所有已启动WSS handler完成，再关闭pool。不能只调用httptest.Server.Close（hijacked不在其通常请求追踪内），不能靠time.Sleep/polling计数/降低并发/增加timeout。wrapper注册与等待须避免WaitGroup Add/Wait竞态并覆盖失败清理；每条handler实际完成必须可证。gateway.go加入join是这一test-only等待可信的前提，现状的“outer handler返回”已被probe证明不足。

最小允许生产路径仅 `backend/go/gateway/gateway.go`；若实现论证证明公开API确需变更，再单独提出，不预先授权gateway/http.go或其他backend生产目录。

最小测试候选路径：`backend/go/gateway/watch_failure_test.go`（真实watch/lifecycle/regression和原unknown/internal/mixed负例）；`backend/go/tests/runtime_test.go`（只含直接handler completion fixture helper）；按实际调用图窄改 `backend/go/tests/auth_test.go`、`backend/go/tests/contract_fixture_test.go`、`backend/go/tests/message_test.go`、`backend/go/tests/revocation_fallback_test.go` 的fixture创建/cleanup等待。实现前进一步精确列调用点；这不是backend/**或测试行为普遍重写授权。

保留所有既有behavior/assertions、数据库故障及internal故障注入、unknown/internal/mixed panic/nonzero、normal+race、精确CI/head/security gates；不改contracts/Frozen/ACK/生产TLS/dependencies/checker/classifier，不加入通用lifecycle框架、新服务或GROUP产品。新增join所需责任来自canonical§3Gateway连接生命周期、§10SRC-01/03/04和error治理资源清理不得掩盖根因；不是architecture扩展。

授权后的最小验证：先在正确seam锁定“在途watch→socket关闭→handler完成→pool释放”的同步回归，证明没有pool先于watch释放；保留真实closedpool、PGinternal/mixed子进程失败测试，检查所有仍应panic的分支。真实disposable PG/NATS上执行原normal和race（不改命令/skip）；任何新最终SHA重新fresh regular→different fresh error→exact push/PR CI→protected merge→actual-main→safe sync。该提案没有声称已修复或已接受。
