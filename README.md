# Pigeon

> 投递简历时，不再为了一个验证码反复拿起手机。

## 为什么我做了 Pigeon

准备应届生求职时，我常常要在一天内连续填写许多公司的招聘网站、第三方招聘平台和测评系统。这些页面经常要求短信验证：我刚在电脑上填到一半，就要停下来拿起手机、打开短信、记住验证码，再回到电脑继续输入。

真正让我苦恼的不是输入几位数字，而是这个动作会反复打断投递节奏。投递得越多，我在电脑和手机之间切换得就越频繁；原本连贯的填写过程，也被一次次拆得零零碎碎。

所以我做了 Pigeon，希望省掉“拿起手机查看验证码”这一步。iPhone 收到验证码短信后，Pigeon 会在 Windows 上提取其中的 OTP（One-Time Password，一次性密码；这里就是短信中的一次性验证码），并把它放进剪贴板。我可以继续留在电脑前，直接按 `Ctrl + V`。

## 它有什么效果

```text
原来：网站发送验证码 → 拿起手机 → 打开短信 → 记住验证码 → 回到电脑输入
现在：网站发送验证码 → 你直接按 Ctrl + V
```

Pigeon 只负责把验证码送到剪贴板，不会替你点击“发送验证码”、自动填写其他个人信息或提交简历。最终操作仍由你确认。

## 软件介绍

Pigeon 是一个连接 iPhone 与 Windows 的本地工具：

- iPhone 通过 Shortcut 把收到的短信正文发送到同一局域网内的电脑；
- Pigeon 从短信中提取唯一的 4–8 位一次性验证码（OTP）；
- 提取结果写入 Windows 剪贴板，短信正文和完整 OTP 不会写入日志；
- 整个过程不依赖第三方云服务器。

窗口会直接显示 Shortcut 需要填写的完整 URL、配对 `token` 和当前可用的 IP 地址。切换路由器或 IP 变化后，可以从窗口复制新的 URL。

## 下载

当前版本：**V0.2.0 Alpha 9**，支持 Windows 10/11。

- [直接下载 Windows ZIP](https://github.com/Eric-H-h/Pigeon/releases/download/v0.2.0-alpha.9/Pigeon-windows-x64.zip)
- [查看 SHA-256 校验值](https://github.com/Eric-H-h/Pigeon/releases/download/v0.2.0-alpha.9/Pigeon-windows-x64.zip.sha256)
- [查看全部 Releases](https://github.com/Eric-H-h/Pigeon/releases)

下载后请解压整个 ZIP，再运行其中的 `Pigeon.exe`。当前 Alpha 版本尚未进行代码签名，Windows SmartScreen 可能显示风险提示；请确认文件来自本仓库，并核对 Release 中的 SHA-256。

## 快速使用

1. 让 iPhone 和 Windows 连接同一台你信任的路由器。
2. 在 Windows 中把当前网络设置为**专用网络**；首次运行时，防火墙也只允许 Pigeon 访问**专用网络**。
3. 解压下载的 ZIP，运行 `Pigeon.exe`。
4. 从窗口复制“快捷指令 URL”和“配对 token”，填入 iPhone Shortcut。
5. 收到验证码短信后，等待窗口显示“OTP 已复制”，然后在电脑上按 `Ctrl + V`。

连接测试：将窗口 URL 末尾的 `/otp` 临时改成 `/health`，再用 iPhone Safari 打开。看到 `Pigeon OK`，说明手机到电脑的局域网链路正常。

如果你在校园网环境中使用自己的路由器，两台设备都应连接这台路由器的普通 LAN，不要使用访客网络，也不要开启设备隔离。

## Shortcuts 配置教程

[在线查看 Windows + iPhone Shortcuts 图文教程](https://eric-h-h.github.io/Pigeon/guide/iphone-shortcuts.html)

教程包含 Windows SmartScreen、防火墙专用网络设置，以及 iPhone Message 自动化、`POST` 请求和 JSON 字段的完整配置。无需下载仓库，打开页面后即可跟随图文步骤进行设置。

## 进一步了解

以下内容用于排障、了解安全边界或参与开发。只想使用 Pigeon 的用户，完成上面的下载和快速使用即可。

### IP 地址改变后怎么办

Pigeon 每 5 秒检测一次当前私有 IPv4 地址，并自动更新窗口中的完整 `/otp` URL。地址变化后，只需在普通 Shortcut 中替换这一处 URL，个人自动化不需要重建。

如果经常使用同一台路由器，也可以在路由器管理页面为 Windows 设置 DHCP 地址保留；具体入口取决于路由器型号。

### 为什么必须使用专用网络

Pigeon 通过局域网 HTTP 接收短信正文，因此只应在你信任的网络中运行：

1. Windows 当前 Wi-Fi 或以太网应设置为**专用网络（Private）**；
2. Windows 防火墙中的 Pigeon 只允许**专用网络**，不要允许**公用网络（Public）**；
3. 不要在路由器上把 TCP 8765 转发到公网。

如果只有切换成“公用网络”后才能连接，通常说明防火墙权限勾反了。请把网络改回专用，并修正应用的防火墙授权。

### 工作方式

```text
iPhone 短信个人自动化
        │ 短信正文 + 配对 token（HTTP POST，仅局域网）
        ▼
Pigeon：验证 token → 提取唯一的 4–8 位 OTP
        │
        ▼
Windows 剪贴板（请求排除历史记录与云同步）
```

服务提供三个端点：

- `GET /health`：检查手机到电脑的网络连接；
- `POST /check`：验证配对 `token`，不操作剪贴板；
- `POST /otp`：验证 `token`、提取 OTP 并复制。

### 安全与隐私

- 短信正文只在 iPhone 与 Windows 的当前局域网之间传输；
- 每次安装生成独立的随机配对 `token`；
- 程序不记录短信正文、`token` 或完整 OTP，界面只显示脱敏事件；
- 服务只接受本机回环或 RFC1918 私网来源；
- 局域网 HTTP **不是端到端加密**，因此不能在公共 Wi-Fi 或公网端口转发环境中使用。

完整边界见[隐私与安全说明](docs/privacy-and-security.md)和[安全策略](SECURITY.md)。

### 当前限制

- IP 改变后，需要更新普通 Shortcut 中的一处 URL；
- iOS 个人自动化不能随普通 Shortcut 一起分享，接收者仍需自己创建 Message 自动化；
- 当前识别包含关键词的 4–8 位数字及常见 `123-456` 格式；遇到多个无法判断的数字时会拒绝猜测；
- 当前不会自动点击网页、填写其他字段或提交表单。

### 从源码运行

要求：Windows 10/11、Python 3.10–3.12。

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python run_pigeon.py
```

首次启动会在 `%LOCALAPPDATA%\Pigeon\config.json` 创建随机安装 ID、配对 `token` 和界面语言设置。首次启动新版时，程序会自动迁移旧名称目录中的配置。不要公开或提交这些配置文件。

### 开发与文档

- [快速开始](QUICKSTART.md)
- [Alpha 9 发布说明](RELEASE_NOTES.md)
- [故障排查](docs/troubleshooting.md)
- [架构与设计取舍](docs/architecture.md)
- [开发历史与旧版迁移](docs/development-history.md)
- [从源码开发与测试](docs/development.md)

运行测试与构建：

```powershell
.venv\Scripts\python -m pip install -r requirements-build.lock
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m pytest
.venv\Scripts\pyinstaller pigeon.spec
```

### 卸载

1. 在 Pigeon 窗口选择“退出”。
2. 删除解压后的文件夹或 `Pigeon.exe`。
3. 删除 `%LOCALAPPDATA%\Pigeon`；如曾使用旧版，也删除旧名称的配置目录，清除安装 ID 与配对 `token`。
4. 在 iPhone 删除相关 Shortcut 和 Message Personal Automation。
5. 如 Windows 防火墙仍有 Pigeon 允许项，可在“允许应用通过防火墙”中移除。

## License

Pigeon 使用 [MIT License](LICENSE)。二进制发行包同时包含 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 中列出的第三方许可信息。
