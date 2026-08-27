# OTPigeon

把 iPhone 收到的短信验证码，安全地送到同一局域网内的 Windows 剪贴板。

OTPigeon 是一个本地优先的小工具：iPhone「快捷指令」把短信正文发给 Windows，Windows 只提取 4–8 位验证码并写入剪贴板。运行时不需要云服务器，也不会把短信或验证码写入日志。

> 当前状态：**V0.2 Alpha**。31 项自动化测试、Windows EXE 启动、私网 HTTP、token 鉴权和原始 mDNS 记录冒烟测试已通过；公开发布前仍需完成 iPhone 对 V0.2 稳定地址的真机验收。请先阅读[当前限制](#当前限制)。

## 它解决什么问题

旧版做法把 `192.168.137.1` 写死在快捷指令中。一旦热点或网络环境改变，自动化就会失效，而且用户很难判断问题发生在哪一层。

OTPigeon 为每次安装生成一个稳定名称，例如：

```text
http://otpigeon-a1b2c3d4.local:8765
```

IP 改变后，Windows 会在当前私有网络接口上重新发布这个名称；快捷指令通常不需要修改。窗口仍会显示数字 IP，供不支持 `.local` 名称的网络临时兜底。

## 推荐使用方式

1. Windows 开启「移动热点」。
2. iPhone 连接这个热点。
3. Windows 启动 OTPigeon，记下 `PC address` 与 `Pairing token`。
4. 按[图文版快捷指令指南](guide/iphone-shortcuts.html)创建普通快捷指令和个人自动化。
5. 先在 Safari 打开 `<PC address>/health`，看到 `OTPigeon OK` 后，再测试 `/check` 和真实验证码。

Windows 热点是默认推荐路径，因为网络边界更清楚。家庭 Wi-Fi 也可以使用，但必须是受信任的私有网络，并且路由器不能隔离设备。

下载发行包时先阅读 [QUICKSTART.md](QUICKSTART.md)。Alpha EXE 尚未代码签名，SmartScreen 可能提示风险；请先核对 GitHub Release 附带的 SHA-256，不要关闭 SmartScreen。

## 从源码运行

要求：Windows 10/11、Python 3.10–3.12。

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python run_otpigeon.py
```

首次启动时会在 `%LOCALAPPDATA%\OTPigeon\config.json` 创建随机安装 ID 与随机配对令牌。不要把这个文件上传、截图公开或发给他人。

## 工作方式

```text
iPhone 短信个人自动化
        │ 短信正文 + 配对令牌（HTTP POST，仅局域网）
        ▼
otpigeon-xxxx.local:8765
        │ 验证令牌 → 提取唯一的 4–8 位数字
        ▼
Windows 剪贴板（请求排除历史记录与云同步）
```

服务只提供三个端点：

- `GET /health`：网络连通性检查，不需要令牌。
- `POST /check`：验证配对令牌，不接触剪贴板。
- `POST /otp`：验证令牌、提取验证码并复制。

## 安全与隐私

- 不依赖第三方服务器，短信正文只在 iPhone 与 Windows 的当前局域网之间传输。
- 每次安装使用独立的随机令牌；服务端使用常量时间比较。
- 不记录请求正文、令牌或完整验证码；界面只显示脱敏事件。
- 请求体和短信长度有限制，异常输入会被拒绝。
- 即使服务监听多个接口，也只接受本机回环或 RFC1918 私网来源。
- 写入验证码时请求 Windows 排除剪贴板历史与云剪贴板；最终行为仍受 Windows 版本和策略影响。
- 局域网 HTTP **不是端到端加密**。不要在酒店、校园等不受信任网络使用；优先使用 Windows 移动热点。

完整边界见[隐私与安全说明](docs/privacy-and-security.md)和[安全策略](SECURITY.md)。

## 当前限制

- iOS 个人自动化不能随普通快捷指令一起分享，接收者仍需自己创建一次 Message 自动化。
- `.local` 解析受 Windows 防火墙、iOS 本地网络权限、路由器客户端隔离和企业网络策略影响；失败时使用窗口显示的数字地址排查。
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
- [LGPL 源码与重建说明](docs/lgpl-rebuild.md)

## 开发

```powershell
$env:SKIP_CYTHON = "1"
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
