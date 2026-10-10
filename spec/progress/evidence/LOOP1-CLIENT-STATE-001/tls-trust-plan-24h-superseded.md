# STATE临时测试信任精确执行对象

未安装信任，产品TLS默认校验无改动。旧CA和leaf均2026-10-04 19:20:46 UTC到期，真实结果已记录。新CA原件指纹见tls-prepared.json，SHA256 2c8bae566f9e9332f1b61c2f9f0906497eeb9ff282ec1d01db0ffed580078ad7，Windows SHA1 8f6b520d74be55471906592c724eaae113033070；有效至2026-10-11 08:36:32 UTC（北京时间16:36:32）。CA pathLen0并critical name constraints只localhost/127.0.0.1，leaf对应SAN，仅24小时测试。CA私钥未持久化；leaf key仅worktree私有runtime ACL保留。

拟执行范围：Windows当前用户Root仅导入此CA，不触LocalMachine或policy；实际桌面同账号新进程核验默认TLS/hostname通过，不以工具隔离视图代替应用真实环境。记录原Root证书集私有hash/baseline，发现碰撞/身份不符即停；结束仅删除此新thumbprint，原集合逐项相等并以同live endpoint默认TLS拒绝+请求scoped原CA成功作rollback负正例。任何import失败不通过registry/unprotected-store或绕过TLS解决。

Android仅既有受控AVD IMClientSend34/API34 x86_64，拟独占serial emulator-5590；先确认无其他owner、api/AVD/Enforcing/原uid及134CA实际集合。暂时adb root仅操作该AVD；在init/zygote命名空间受控copy原CA集合加此CA，然后只读bind overlay /apex/com.android.conscrypt/cacerts，不持久改system分区、不改SELinux或product TrustManager。每namespace记录mount identity与original exact CA hashes，新app继承和默认SDK TLS验证。adb reverse仅所需测试18443/8443映射，记录原list不覆盖未知mapping。完成严格反序umount新mount/删除已登记own临时路径，reboot no wipe/no snapshot，核对init/zygote/app原集合、Enforcing、uid2000及ownmapping不存在，default SDK拒绝同live fixture。旧helper硬编码旧证书及到期，不直接运行；tests/state窄工具只登记此对象，失败保留并安全回滚。

清理只已记录本次创建的进程、Docker project labels/volumes、fixture账号数据库和新临时证书；不删除真实用户数据库/凭好或凭据，不改变main未知work。证书更换是测试输入，不改变生产security boundary/contracts，但新系统Root import具有真实信任影响，当前仅准备审查对象，执行待明确授权。

