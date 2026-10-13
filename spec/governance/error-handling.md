# 错误处理与提交 GitHub CI 前的独立专项审查

本治理执行 Human 2026-10-13 请求，从属于 Frozen Architecture、approved ADR、contracts、domain/invariants 与 acceptance。它补充 canonical §12–14，不替代任何权威，不改变公开错误、ACK、兼容或安全语义。发生权威冲突，停止受影响工作并按既有架构流程记录最小问题；不得先实施再追认。

## 实现规则

未知异常、内部编程错误、不变量破坏 MUST 沿正常调用链传播，使操作、测试或进程明确失败。需要崩溃时允许崩溃，随后定位真实缺陷。MUST NOT 用空 catch、忽略 Promise rejection、假空数据、默认成功/正常状态、失真错误类别或仅打印日志继续掩盖错误。不得重复捕获、无依据包装、吞掉原始异常或堆叠未来兼容/兜底层。可在已批准边界安全投影已知故障，避免泄露凭据；隐私要求不授权把未知编程错误变成网络/协议/存储失败。

保留当前架构/契约要求的事务回滚、资源清理、网络失败后的 FAILED、协议拒绝、账号隔离、提交结果不确定保护和冻结偏好默认。每项捕获/回退说明 **具体故障 → 当前依据 → 实际恢复/失败行为**；例如回滚保留未发布 Outbox，下次现有 tick 重试，或写失败关闭连接使客户端通过 timeout/retry/Sync 收敛。“避免崩溃”“提高健壮性”“以后可能需要”均不能单独成立。捕获边界尽量只包含会产生该已知故障的外部操作，内部回调/验证/状态发布不得借用它的异常类别。

串行队列可在已知失败后继续调度，但原操作必须真实失败；未知错误不能被清除后让 idle/后续操作伪装 PASS。取消和账号退休只允许丢弃已知过期结果，不能吞掉内部 bug。资源清理必须执行；清理失败若不可恢复应传播，不替换未知根因。不得新增通用错误框架、日志平台、重试框架、未来功能或无当前依据抽象。

## 最小示例

错误：吞掉内部异常，状态可能只更新了一半，调用者却继续运行。

```typescript
try {
  applyUpdate(event);
} catch {}
```

正确：让测试/操作显式失败，再修复真实缺陷。

```typescript
applyUpdate(event);
```

错误：把加载失败伪装成正常空结果，使使用者无法区分没有数据与故障。

```typescript
try {
  return await loadData();
} catch {
  return [];
}
```

正确：保留真实失败结果，由正常调用链承担它。

```typescript
return await loadData();
```

示例只表达既有 TypeScript 语义，不授权新技术、业务机制或 contracts 变更。

## 独立提交门禁

实现与必要本地验证/提交 → **常规独立 Review** → **新的独立错误处理专项审查** → 提交 GitHub CI → 适用 exact-head CI → protected integration → actual-main 验证 → H:/IM-platform 安全同步。只有最后同步验证完成才可 done；Task PASS 不等于 Stage Gate PASS。

专项审查 Agent MUST 是全新上下文，且未参与当前候选实现、Fix 或常规 Review。常规 Reviewer 与专项审查者不能是同一 Agent；改角色名不构成独立性。常规 PASS 后才运行专项审查，专项审查仅在提交 GitHub CI 前设置一次，不在每次编辑/命令之前重复。

任一审查 FAIL 时候选未完成；专项 FAIL 明确禁止 push、创建或更新会触发该候选 CI 的 PR。新 Fix Agent 修复 → 新常规 Review Agent → 又一个新专项审查 Agent，循环至两项都 PASS。任何修复形成新 SHA，两项必须重审 **最终 SHA**；旧 SHA 的 PASS 不可沿用。通过后仍要核对真实 hosted head、changed-path 必需作业与结果；missing/failed/cancelled/anomalous skip 不是 PASS。

## 专项清单与证据

- 逐文件覆盖任务的生产范围，包括没有 grep 命中的文件及必要原生适配器；记录路径、输入 SHA-256、职责、实际检查结果与候选 hash。
- 查无当前依据的防御检查、兼容分支、空 catch/空默认、Promise 忽略、错误分类失真、日志后错误运行、重复捕获/包装/根因丢失。
- 逐项记录位置、触发条件、如何掩盖、最小修复及真实验证；逐个保留 catch/回退列具体故障、当前依据、恢复行为，不能仅按文件概括。
- 检查实现逻辑/导入/责任和 Minimality，不因局部测试绿而删必要事务/FAILED/账号/不确定提交保护；不改 contracts 或削弱旧断言。
- 记录角色/身份/新上下文与未参与声明、精确 SHA/branch/diff range、干净 committed checkout 方法、命令/退出码/时长、PASS/FAIL、发现及保留理由、证据 hash/路径。

Task Spec 与 current.md 必须能恢复两项审查状态及下一动作。Research Recorder 记录可观察工作，与产品接受分开；Recorder PASS、自评或本地测试不能替代独立审查、CI 或集成。
