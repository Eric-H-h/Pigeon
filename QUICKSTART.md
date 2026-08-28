# OTPigeon 快速开始

> V0.2.0 Alpha 8 是本地验证版。它直接使用 Windows 当前的私有 IPv4 地址，不使用 `.local` 名称。不要在公共 Wi-Fi 上使用。

## 1. Windows

1. 让 Windows 连接受信任的路由器，或开启 Windows 移动热点。
2. 在“设置 → 网络和 Internet → Wi-Fi（或以太网）→ 当前连接”中，把“网络配置文件类型”设为 **专用网络**。
3. 解压整个发行 ZIP，双击 `OTPigeon.exe`。
4. Windows 防火墙询问时，只勾选 **专用网络**，不要勾选公用网络。
5. 窗口显示“运行中”后，复制“快捷指令 URL”与自己的“配对 token”。完整 URL 已包含 `/otp`。

如果只有把网络改成“公用”才能连接，说明 OTPigeon 的防火墙权限勾反了。请把网络改回“专用”，然后在“Windows 安全中心 → 防火墙和网络保护 → 允许应用通过防火墙”中为 OTPigeon 勾选“专用”、取消“公用”。

未签名的 Alpha EXE 可能触发 Microsoft Defender SmartScreen。先核对下载来源和 SHA-256；只有确认文件来自本项目且哈希匹配时，才选择“更多信息 → 仍要运行”。不要关闭 SmartScreen，也不要从第三方网盘下载。

## 2. iPhone

1. 让 iPhone 连接 Windows 所在的同一台受信任路由器或 Windows 移动热点，不要使用访客网络。
2. 按 `guide/iphone-shortcuts.html` 创建 `Send to OTPigeon` 普通 Shortcut。
3. 把 Windows 窗口中的完整“快捷指令 URL”和 token 填入 Shortcut，不要再次添加 `/otp`。
4. 把 URL 末尾 `/otp` 临时替换成 `/health`，用 Safari 打开并确认显示 `OTPigeon OK`。
5. 手动运行 `/check` 后，再创建 Message Personal Automation，并选择 `Run Immediately`。

个人自动化无法随普通 Shortcut 分享，所以每个用户必须自己创建一次。

## 3. IP 改变后

窗口会自动生成包含新 IP 的完整 URL。打开普通 `Send to OTPigeon` Shortcut，用新 URL 替换旧 URL；个人自动化不用重建。修改后先把末尾 `/otp` 换成 `/health` 做 Safari 测试。

如果窗口列出多个数字地址，选择与 iPhone 同一网段的地址。例如 iPhone 为 `192.168.5.134`，Windows 应选择 `192.168.5.x` 地址。

## 4. Language

窗口右上角可选择“中文”或 `English`，选择结果会自动保存。中文界面中的 `token`、`IP`、`URL`、`OTP`、`Shortcut` 保持英文，便于与 iPhone 动作名称对应。

## 5. 校验下载

把 ZIP 和 `.sha256` 文件放在同一目录，在 PowerShell 运行：

```powershell
Get-FileHash -Algorithm SHA256 .\OTPigeon-windows-x64.zip
Get-Content .\OTPigeon-windows-x64.zip.sha256
```

两处哈希值应完全相同。
