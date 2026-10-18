# CI 只读诊断

结论：`DIAGNOSIS_ONLY_NOT_ACCEPTANCE`。候选 204e803724c2a64514c6e14f8d1ed86cabca8acb，base 86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0；actor /root/group_ci_diagnose_r3。没有 source 写入、push/PR/CI 重跑/merge/sync。

## 已证实的故障链

原始 PR run38859630177 attempt1/job116838949761 log 510–537 显示 normal `go test -count=1 ./...` 全部 PASS，tests 包19.408s；随后 race core/gateway/shared PASS，race tests 在46.347s panic。实际 checkout204e803，PGSSLMODE:disable；TLS refusal 已消失。原始 log 的 SHA256为e62928626ef9a98cf312654e6b606a70d77525405adbf8ced3b60de92db706b9，复制原件和hash见input-manifest。

gateway.go186–194将watch放入独立goroutine；224–241中watch每秒创建 Background()+1s ctx，在authenticate/QueryRow返回之前不会再次检查c.done。session.go27–39直接返回真实pgx错误，没有Core包装；这一错误产生于Gateway数据库直读，不经过Core RPC或消息提交。serve192对helper不接受的错误panic。

pgxpool/pool.go267–282让constructor继续在后台连接；puddle/pool.go422使用newValueCancelCtx(ctx,p.baseAcquireCtx)。puddle/context.go14–17的Deadline/Done/Err全来自baseAcquireCtx，watch ctx只提供Value。puddle/pool.go179–189的Close是cancelBaseAcquireCtx的唯一调用点。pgxpool.Close449–452调用此Close。因而在途constructor的“context canceled”属于pool关闭取消，不是watch的1秒截止。pgconn/errors.go138–150将因取消打断的net timeout规范为裸context.Canceled；pgconn.go314–317/384–392包裹为perDial/fmt后，在ConnectConfig160形成ConnectError+errors.Join。

真实错误树（双地址受控复现与hosted文本一致）：

```
*pgconn.ConnectError (非net.Error)
  *errors.joinError
    *pgconn.perDialConnectError
      *fmt.wrapError (failed to receive message)
        context.Canceled (非net.Error)
    *pgconn.perDialConnectError
      *fmt.wrapError (dial error)
        *net.OpError (net.Error, Timeout=false)
          net.canceledError
```

watchTransportFailure248–277逐join分支检查；第一个分支全无net.Error，返回false。第二分支确为网络包装，也不能覆盖第一分支。现negative test watch_failure_test.go220–239明确要求裸Canceled未知、mixed/internal不被伪装。该helper在这个生命周期误用上保持失败符合治理；不应把Canceled一概改known来压制panic。

## 可重复的最小反馈loop与对照

仅在本E目录创建诊断测试，通过Go -overlay加入gateway包，直接调用真实未导出的watch、validator、watchTransportFailure以及真实pgx5.7.6/puddle2.2.2。受控PGwire listener读取真实StartupMessage后阻塞，显式channel安排顺序，未修改tracked source，也没有sleep/重复碰运气。

1. pool.Close在startup读阻塞时发生：单IPv4和双地址均产生ConnectError/Canceled、helper=false；watch约1.002s返回（首tick为1s，未等自身下一秒截止）。
2. 不关pool而等待watch自身截止：约2s返回context.DeadlineExceeded，net.Error=true/Timeout=true/helper=true。否定“日志只是watch正常超时”的解释。
3. 直接authenticate的30s调用ctx：pool.Close后ctx.Err仍nil、错误却wrapsCanceled，进一步确认取消属于pool constructor。
4. 已在途watch时，先peer.Close，再等待外层handler返回（真实connection.close/c.done已执行），最后pool.Close，仍复现同树。HTTP handler返回/c.done均不足以表示watch完成。

初版normal三探针PASS；增量第4探针normal PASS；最终四探针连同IPv4/双地址子例在 `go test -race ... -run ^TestDiagnose -count=1 -v ./gateway` 一次运行PASS，包6.982s。PASS表示复现/可区分对照成立，不是bug已修复或候选接受。精确argv、退出码、时长和redacted输出blob见command-index及research原件。最终probe字节单独绑定manifest。

## 测试fixture所有权

tests/message_test.go97注册db.Close，128注册server.Close，131注册各client.Close，146–161注册数据清理；LIFO使其先清数据、关client、关server，再关pool，但没有watch join。auth_test.go77/154/173；contract_fixture_test.go409/416及440bound.Close；revocation_fallback_test.go30/41、161gatewayDB.Close/193server.Close同样只关闭socket/server/pool。没有t.Parallel或测试Setenv修改pool设置的证据；各package有各自pool、共用disposable数据库，但当前根因不需要数据交叉写来解释。

connection.close(gateway.go59–61)的c.done只表示关闭开始；serve没有watch完成channel/WaitGroup，NewHandler(http.go17)只返回http.Handler。httptest会从HTTP连接跟踪中移除hijacked连接；server.Close不等于独立watch结束。故仅重新排现有close顺序、等待c.done/外层handler返回或切IPv4，均没有可靠完成性证明。新join实现后，test-only handler completion包装可以提供可靠等待，不必预先决定新增公开NewHandler API；方案见minimal-scope-proposal。

## 范围与限制

当前Task R2仅准许PGSSLMODE:disable和7checkout pins，backend明确Forbidden；没有已证据支持的剩余CI-only修复。应暂停受影响闭环，先申请最窄Go生命周期scope，不改classifier、normal/race、未知异常传播、契约或Frozen。内部lifecycle纠正本身沿canonical§3Gateway/§10SRC、Minimality/error治理可成立；若选择改变错误或安全语义则另需architecture流程。GROUP保持backlog，S2 OPEN。

本地无可用Docker daemon、未找到psql。Go1.26.6 Windows与hosted Go1.23 Linux不同；完整PG/NATS/race suite未复现，原non-verbose hosted日志也不能唯一指出是哪一个fixture。受控listener不是数据库，退休探针的外层handler复制serve的watch/close生命周期组合，未声称真实DB成功auth.bind再失败。已证机制和代码取消owner足以否定上述CI环境捷径；精确完整修复仍需授权后回归、fresh regular→different fresh error→exact CI等。

## Recorder与工作区

启动必读、技能读取、prompt复制、工具帮助在Recorder run之前，capture_mode=prospective_resume/pre_recorder_trace_complete=false。首次start-run因schema不接受diagnosis角色exit1，随后使用fix枚举承载“只读诊断”，并不表示执行Fix。一个backend cwd相对recorder路径启动失败未进入run；一次Go命令因Recorder总在repo root执行而找不到go.mod（记录exit1），后续显式child Set-Location后成功。一次auth.go读路径不存在但其组合PowerShell命令最终exit0，这不是该文件成功读取；实际session.go随后单独读取。直接外部probe/evidence写入及通信不由run-command捕获，均在此公开。无旧Recorder流编辑。外部stdout导出来自redacted blobs，不能把其digest冒充raw stdout_sha256；command-index保留两者语义。git-state复核assigned root/HEAD/branch、clean tracked/index及五product tree与base一致；main未写入。
