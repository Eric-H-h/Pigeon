# OTPigeon V0.2.0 Alpha 6

这是用于 iPhone 真机和第二用户测试的预发布版本，不是稳定版。

## 本版变化

- 主窗口直接显示 Windows 当前的私有 IPv4 地址，例如 `http://192.168.5.101:8765`。
- 每 5 秒重新检测网络地址，IP 变化后窗口自动刷新。
- 移除 `.local`/mDNS 连接方式及 `python-zeroconf` 运行时依赖。
- README、快速开始和图文指南统一要求 Windows 使用“专用网络”。
- 明确说明：如果只有切换到“公用网络”才能连接，应修正防火墙权限，而不是长期使用公用网络。
- 保留随机配对 token、私网来源限制、OTP 提取和敏感剪贴板写入。

## 已知限制

- 数字 IP 改变后，需要更新普通 Shortcut 中的一处 URL；个人自动化不用重建。
- 多网卡电脑可能显示多个私有地址，用户应选择与 iPhone 同一网段的地址。
- 个人自动化不能随 Shortcut 分享，需要接收者手动创建。
- EXE 尚未代码签名，可能触发 SmartScreen。
- HTTP 没有端到端加密，只能在 Windows 移动热点或受信任的专用网络使用。

## 发布检查

本 Release 应保持 Draft，直到完成：

- 无 Python 的干净 Windows 11 启动测试；
- iPhone 使用数字地址通过 `/health`、`/check`、真实短信与锁屏测试；
- Windows 网络类别和 OTPigeon 防火墙权限均为“专用”；
- 第二名非开发者按文档完成安装；
- `.shortcut` 从真机导出并确认不含维护者地址和 token。
