# STATE临时测试信任精确执行对象

未安装信任，产品TLS默认校验无改动。旧CA和leaf均2026-10-04 19:20:46 UTC到期，真实结果已记录。新CA原件指纹见tls-prepared.json，SHA256 44d029ca6c5d243b8948b477aec9bb1c0c66d8f8ec656e26d2f5df5d83d615a2，Windows SHA1 ca463bfb65537808cb8d61591e5a7626f64e6202；有效至2026-10-17 08:41:50 UTC（北京时间16:41:50）。CA pathLen0并critical name constraints只localhost/127.0.0.1，leaf对应SAN，仅7天测试。CA私钥未持久化；leaf key仅worktree私有runtime ACL保留。

拟执行范围：Windows当前用户Root仅导入此CA，不触LocalMachine或policy；实际桌面同账号新进程核验默认TLS/hostname通过，不以工具隔离视图代替应用真实环境。记录原Root证书集私有hash/baseline，发现碰撞/身份不符即停；结束仅删除此新thumbprint，原集合逐项相等并以同live endpoint默认TLS拒绝+请求scoped原CA成功作rollback负正例。任何import失败不通过registry/unprotected-store或绕过TLS解决。

Android仅既有受控AVD IMClientSend34/API34 x86_64，拟独占serial emulator-5590；先确认无其他owner、api/AVD/Enforcing/原uid及134CA实际集合。暂时adb root仅操作该AVD；在init/zygote命名空间受控copy原CA集合加此CA，然后只读bind overlay /apex/com.android.conscrypt/cacerts，不持久改system分区、不改SELinux或product TrustManager。每namespace记录mount identity与original exact CA hashes，新app继承和默认SDK TLS验证。adb reverse仅所需测试18443/8443映射，记录原list不覆盖未知mapping。完成严格反序umount新mount/删除已登记own临时路径，reboot no wipe/no snapshot，核对init/zygote/app原集合、Enforcing、uid2000及ownmapping不存在，default SDK拒绝同live fixture。旧helper硬编码旧证书及到期，不直接运行；tests/state窄工具只登记此对象，失败保留并安全回滚。

清理只已记录本次创建的进程、Docker project labels/volumes、fixture账号数据库和新临时证书；不删除真实用户数据库/凭好或凭据，不改变main未知work。证书更换是测试输入，不改变生产security boundary/contracts，但新系统Root import具有真实信任影响，当前仅准备审查对象，Human已明确批准临时测试信任并回滚，最新明确授权有效期一周；仅此新对象。旧24h未装保留为superseded。



## Strict chain repair replacement (latest)

Previous week object 44d029/CA463B was revoked; windows-week1-rollback.json proves full 74-thumbprint baseline restored. Python3.13 strict validation refused missing AKI. New same scoped seven-day object includes AKI/SKI and leaf key usage. No verify_flags or product TLS change. Latest exact input:

```json
{
  "task_id": "LOOP1-CLIENT-STATE-001",
  "directory": "H:\\IM-platform\\.git\\worktrees\\IM-platform43\\state-runtime\\tls-state-week2",
  "hosts": [
    "localhost",
    "127.0.0.1"
  ],
  "endpoint": "https://localhost:18443",
  "notAfterUTC": "2026-10-17T08:58:07.083261+00:00",
  "caSHA256": "a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5",
  "caWindowsThumbprintSHA1": "727e5d6bb4d072f9a76bfbc8fa81a6159a047d5c",
  "caPEMSHA256": "1dfcade204cf7f2b276fb67a745d71d424aed4a5f557f2947c706eee2b970ab5",
  "serverSHA256": "37e443d4412dd48cae3c5d3e542b660a8ac0f53ba6cade7ff498e736fba60c7d",
  "trust_installed": false,
  "ca_private_key_saved": false
}
```

Latest Human seven-day localhost/current-user/readonly-AVD approval covers this necessary certificate repair, as confirmed by Coordinator. New CurrentUser baseline file windows-root-week2-baseline.json; retain original baseline. Cleanup remains exact thumb removal, full baseline equality, default SDK negative test with same live fixture.
