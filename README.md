# OTPigeon

把 iPhone 收到的短信验证码，安全地送到同一局域网内的 Windows 剪贴板。

OTPigeon 是一个本地优先的小工具：iPhone「快捷指令」把短信正文发给 Windows，Windows 只提取 4–8 位验证码并写入剪贴板。运行时不需要云服务器，也不会把短信或验证码写入日志。

> 当前状态：**V0.2.0 Alpha 7 验证版**。窗口直接给出 Shortcut 要填写的完整 `/otp` URL，并新增可持久化的中文/English 界面。此分支尚未推送或合并，等待真机验证。

## 它解决什么问题

旧版把固定 IP 写在快捷指令中，网络改变后很难判断应该填哪个地址。OTPigeon 现在会自动检测当前私有网络接口，并在窗口中直接显示真实地址，例如：

```text
http://192.168.5.101:8765
```

软件不再依赖 `.local` 名称解析，因此不会受到代理 Fake-IP 或路由器 mDNS 支持情况影响。数字 IP 仍可能在切换路由器、重开热点或重新分配地址后改变；窗口会自动刷新，用户只需修改普通 Shortcut 中的 URL，不必重建个人自动化。

## 网络类别必须选择“专用网络”

OTPigeon 只应在你信任的局域网中使用。Windows 当前 Wi-Fi 或热点连接必须设置为 **专用网络（Private）**，Windows 防火墙中的 OTPigeon 也只勾选 **专用**，不要勾选 **公用（Public）**。

如果改成“公用网络”后才能连接，说明现有防火墙权限勾反了。正确做法不是长期使用公用网络，而是：

1. 把 Windows 网络类别改回“专用网络”；
2. 打开“Windows 安全中心 → 防火墙和网络保护 → 允许应用通过防火墙”；
3. 找到 OTPigeon，勾选“专用”，取消“公用”；
4. 重启 OTPigeon，再从 iPhone 测试 `/health`。

## 推荐使用方式

1. 让 Windows 和 iPhone 连接同一台受信任路由器；也可以让 iPhone 连接 Windows 移动热点。
2. 确认 Windows 网络类别是“专用网络”。
3. 启动 OTPigeon；防火墙询问时只允许“专用网络”。
4. 从窗口复制“快捷指令 URL”与“配对 token”，填入 iPhone Shortcut；URL 已包含 `/otp`，不需要手动拼接。
5. 把 URL 末尾的 `/otp` 临时替换成 `/health` 并在 Safari 打开；看到 `OTPigeon OK` 后再测试真实验证码。

如果在校园环境使用自己的路由器，只要 Windows 和 iPhone 都连接这台路由器的普通 LAN、没有进入访客网络或启用设备隔离，两台设备之间的请求会留在自己的局域网内。不要让两台设备直接连接不受信任的校园公共 Wi-Fi。

下载发行包时先阅读 [QUICKSTART.md](QUICKSTART.md)。Alpha EXE 尚未代码签名，SmartScreen 可能提示风险；请先核对 GitHub Release 附带的 SHA-256，不要关闭 SmartScreen。

## 从源码运行

要求：Windows 10/11、Python 3.10–3.12。

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python run_otpigeon.py
```

首次启动时会在 `%LOCALAPPDATA%\OTPigeon\config.json` 创建随机安装 ID、随机配对 token 和界面语言设置。不要把这个文件上传、截图公开或发给他人。

## 工作方式

```text
iPhone 短信个人自动化
        │ 短信正文 + 配对令牌（HTTP POST，仅局域网）
        ▼
Windows 当前私有 IPv4 地址:8765
        │ 验证令牌 → 提取唯一的 4–8 位数字
        ▼
Windows 剪贴板（请求排除历史记录与云同步）
```

服务只提供三个端点：

- `GET /health`：网络连通性检查，不需要令牌。
- `POST /check`：验证配对令牌，不接触剪贴板。
- `POST /otp`：验证令牌、提取验证码并复制。

## IP 地址改变后怎么办

OTPigeon 每 5 秒重新检测一次私有 IPv4 地址，窗口会自动显示新地址。地址变化后：

1. 从窗口复制新的“快捷指令 URL”；
2. 打开 iPhone 上的普通 `Send to OTPigeon` Shortcut；
3. 用新值完整替换 URL 动作中的旧值；
4. 把末尾 `/otp` 临时改成 `/health`，先用 Safari 测试连通性。

个人自动化不用删除或重建。经常在同一路由器使用时，也可以在路由器管理页面为 Windows 设置 DHCP 地址保留；具体入口由路由器型号决定。

## 界面语言

窗口右上角的 `Language` 可选择“中文”或 `English`，选择结果会保存到本机配置。中文界面仍保留 `token`、`IP`、`URL`、`OTP`、`Shortcut` 等专有词的英文写法，便于和 iPhone 及排障文档逐项对应。

## 安全与隐私

- 不依赖第三方服务器，短信正文只在 iPhone 与 Windows 的当前局域网之间传输。
- 每次安装使用独立随机令牌；服务端使用常量时间比较。
- 不记录请求正文、令牌或完整验证码；界面只显示脱敏事件。
- 请求体和短信长度有限制，异常输入会被拒绝。
- 服务只接受本机回环或 RFC1918 私网来源。
- 写入验证码时请求 Windows 排除剪贴板历史与云剪贴板；最终行为仍受 Windows 版本和策略影响。
- 局域网 HTTP **不是端到端加密**。只在受信任的专用网络中使用，不要做公网端口转发。

完整边界见[隐私与安全说明](docs/privacy-and-security.md)和[安全策略](SECURITY.md)。

## 当前限制

- 数字 IP 改变后，需要更新普通 Shortcut 中的一处 URL。
- 如果窗口列出多个地址，应选择与 iPhone 同一网段的地址；例如 iPhone 是 `192.168.5.x`，就选择同样以 `192.168.5.` 开头的 Windows 地址。
- iOS 个人自动化不能随普通 Shortcut 一起分享，接收者仍需自己创建一次 Message 自动化。
- 验证码识别面向包含关键词的 4–8 位数字及常见 `123-456` 格式；多个无关键词数字会拒绝猜测。
- V0.2 基线为 iOS 18.4.1 英文界面；其他 iOS 18 小版本的按钮文字可能略有不同。
- 当前不自动点击网页、不自动提交表单，也不会读取 Windows 上的短信。

## 文档

- [快速开始](QUICKSTART.md)
- [Alpha 发布说明](RELEASE_NOTES.md)
- [iPhone 快捷指令图文指南](guide/iphone-shortcuts.html)
- [故障排查](docs/troubleshooting.md)
- [架构与设计取舍](docs/architecture.md)
- [开发历史与旧版迁移](docs/development-history.md)
- [从源码开发与测试](docs/development.md)

## 开发

```powershell
.venv\Scripts\python -m pip install -r requirements-build.lock
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m pytest
.venv\Scripts\pyinstaller otpigeon.spec
```

详见[开发说明](docs/development.md)。

## 卸载

1. 在 OTPigeon 窗口选择 `Exit`。
2. 删除解压出的 OTPigeon 文件夹或 `OTPigeon.exe`。
3. 删除 `%LOCALAPPDATA%\OTPigeon`，清除安装 ID 与配对 token。
4. 在 iPhone 删除 `Send to OTPigeon` Shortcut 和对应的 Message Personal Automation。
5. 如 Windows 防火墙中仍有 OTPigeon 允许项，可在“允许应用通过防火墙”中移除。

## License

OTPigeon 自身代码使用 [MIT License](LICENSE)。二进制发行包还应同时附带 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 中列出的第三方许可信息。
