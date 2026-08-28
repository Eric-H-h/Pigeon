# Security Policy

## Supported version

项目处于 Alpha 阶段，仅最新的 `0.2.x` 代码接受安全修复。尚未完成真机验收的构建不应被视为稳定发行版。

## Reporting a vulnerability

公开仓库建立后，请优先使用 GitHub 的 **Report a vulnerability / Private vulnerability reporting**。如果该入口尚未启用，请先创建一个不包含复现密钥、短信正文或个人数据的普通 issue，请维护者提供私下沟通渠道。

请勿在公开 issue 中提交：

- `%LOCALAPPDATA%\Pigeon\config.json`；
- Pairing token；
- 真实短信或验证码；
- 包含个人手机号、通知内容或账号信息的截图。

## Security boundary

Pigeon 的目标是阻止同一局域网中的偶然请求，并避免把验证码持久化；它不是互联网暴露的认证服务。

- 服务监听本机所有 IPv4 接口，依赖随机配对令牌鉴权。
- 传输使用局域网 HTTP，没有 TLS。攻击者若能监听当前网络，理论上可看到请求内容。
- 推荐拓扑是 iPhone 连接 Windows 移动热点；不要在公开 Wi-Fi 上运行。
- 不要在路由器上做端口转发，也不要把 8765 端口暴露到公网。
- Windows 防火墙只应允许「专用网络」，不应允许「公用网络」。

更多说明见 [docs/privacy-and-security.md](docs/privacy-and-security.md)。
