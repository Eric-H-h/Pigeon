# OTPigeon V0.2 Alpha

这是用于 iPhone 真机和第二用户测试的预发布版本，不是稳定版。

## 已实现

- iPhone 短信正文经可信局域网发送到 Windows；运行时不依赖云服务。
- 每次安装生成稳定的 `otpigeon-xxxxxxxx.local` 地址和随机配对 token。
- 自动适应 RFC1918 私网接口变化，并提供数字 URL 兜底。
- 验证 token 后提取唯一的 4–8 位 OTP，写入敏感剪贴板。
- 不记录短信正文、token 或完整 OTP。
- Windows GUI、PyInstaller 单文件 EXE、自动测试、mDNS 诊断脚本和完整文档。

## 已知限制

- 尚需 iOS 18.4.1 对稳定 `.local` 地址、锁屏自动化和真实短信的最终验收。
- 个人自动化不能随 Shortcut 分享，需要接收者手动创建。
- EXE 尚未代码签名，可能触发 SmartScreen。
- HTTP 没有端到端加密，只能在 Windows 移动热点或可信私有网络使用。
- VPN/代理 Fake-IP、客户端隔离或企业网络策略可能阻止 `.local`。

## 发布检查

本 Release 应保持 Draft，直到完成：

- 无 Python 的干净 Windows 11 启动测试；
- iPhone 移动热点 `.local`、`/check`、真实短信与锁屏测试；
- 第二名非开发者按文档完成安装；
- `.shortcut` 从真机导出并确认不含维护者地址和 token；
- LGPL 发行方式复核。
