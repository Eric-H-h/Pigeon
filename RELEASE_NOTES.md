# OTPigeon V0.2.0 Alpha 8

这是只供项目所有者真机验证的本地构建，当前分支尚未推送 GitHub，也未合并到 `main`。

## 本版变化

- 中文与 English 界面的应用名统一为 `Pigeon`，标题栏与窗口标题同步显示。
- 窗口底部增加项目链接 `github.com/Eric-H-h/OTPigeon` 和作者署名 `@eric`；项目链接可点击并使用默认浏览器打开。
- README 改为面向使用者的顺序，先说明应届生投递简历时反复查看验证码的痛点，再提供效果、下载和快速使用；专业内容统一后移。
- 上方输入框改为“快捷指令 URL”，直接显示 `http://当前IP:8765/otp`；复制后可以原样粘贴进 Shortcut。
- 下方“可用 IP 地址”继续列出每个私有网卡的基础地址，方便排查多网卡和 IP 变化。
- 窗口右上角新增 `Language`，支持“中文”和 `English`。
- 默认使用中文，并把 Language 选择保存到 `%LOCALAPPDATA%\OTPigeon\config.json`。
- 中文界面保留 `token`、`IP`、`URL`、`OTP`、`Shortcut` 等专有词的英文写法。
- 旧版配置没有 Language 字段时会自动按中文加载，不要求用户删除 token 或重建配置。

## 延续 Alpha 6 的行为

- 直接使用 Windows 当前私有 IPv4 地址，不使用 `.local` 或 mDNS。
- 每 5 秒检测地址变化并刷新窗口。
- Windows 当前连接和 OTPigeon 防火墙权限都应使用“专用网络”。
- 保留随机配对 token、私网来源限制、OTP 提取和敏感剪贴板写入。

## 真机验证重点

1. 中文界面首次启动正常，切换到 `English` 后所有标签和按钮立即更新。
2. 重新启动后保持上次 Language 选择。
3. “快捷指令 URL”包含 `/otp`，Copy 按钮复制的内容可以直接粘贴到 Shortcut。
4. 把 URL 末尾 `/otp` 改成 `/health` 后，iPhone Safari 显示 `OTPigeon OK`。
5. 真实短信自动化仍能把 OTP 写入 Windows 剪贴板。
