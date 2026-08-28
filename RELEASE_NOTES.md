# Pigeon V0.2.0 Alpha 9

这是 Pigeon V0.2.0 Alpha 9 的预发布构建。本版完成产品名称统一，并进一步简化面向使用者的项目介绍。

## 本版变化

- 用户可见的应用名、健康检查结果、Shortcut 名称、EXE 和 ZIP 产物统一为 `Pigeon`。
- README 的项目动机改为第一人称叙述，更直接地说明应届生连续投递时反复查看手机验证码的困扰。
- 使用效果简化为“网站发送验证码 → 你直接按 `Ctrl + V`”。
- 首次出现 OTP 时补充完整解释：One-Time Password，即一次性密码；在本项目中就是短信中的一次性验证码。
- 配置目录改为 `%LOCALAPPDATA%\Pigeon\config.json`，并自动迁移旧版配置，保留原有 token 和语言设置。
- 项目主页链接更新为 `github.com/Eric-H-h/Pigeon`。

## 延续现有行为

- 直接使用 Windows 当前私有 IPv4 地址，不使用 `.local` 或 mDNS。
- 每 5 秒检测地址变化并刷新窗口。
- Windows 当前连接和 Pigeon 防火墙权限都应使用“专用网络”。
- 保留随机配对 token、私网来源限制、OTP 提取和敏感剪贴板写入。

## 发布前验证重点

1. 窗口标题和应用内名称均显示 `Pigeon`。
2. 把 URL 末尾 `/otp` 改成 `/health` 后，iPhone Safari 显示 `Pigeon OK`。
3. 旧版配置首次启动后自动迁移到新目录，token 和 Language 保持不变。
4. 真实短信自动化仍能把 OTP 写入 Windows 剪贴板。
