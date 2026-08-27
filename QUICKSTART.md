# OTPigeon 快速开始

> V0.2 Alpha 尚未完成 iPhone 稳定地址的公开真机验收。预发布包只用于测试，不要在公共 Wi-Fi 使用。

## 1. Windows

1. 解压整个发行 ZIP，不要只把 EXE 从压缩包中直接运行。
2. 双击 `OTPigeon.exe`。
3. Windows 防火墙询问时，只允许 **专用网络**，不要允许公用网络。
4. 窗口显示 `Running` 后，保留 `PC address`，并复制自己的 `Pairing token`。

未签名的 Alpha EXE 可能触发 Microsoft Defender SmartScreen。先核对下载来源和 SHA-256；只有确认文件来自本项目且哈希匹配时，才选择“更多信息 → 仍要运行”。不要关闭 SmartScreen，也不要从第三方网盘下载。

## 2. iPhone

1. Windows 开启移动热点，iPhone 连接该热点。
2. 按 `guide/iphone-shortcuts.html` 创建 `Send to OTPigeon` 普通 Shortcut。
3. 把 Windows 窗口中的地址和 token 填入 Shortcut。
4. 用 Safari 打开 `<PC address>/health`，确认显示 `OTPigeon OK`。
5. 手动运行 `/check` 后，再创建 Message Personal Automation，并选择 `Run Immediately`。

个人自动化无法随普通 Shortcut 分享，所以每个用户必须自己创建一次。

## 3. 出错时

先使用窗口 `Available links` 中的数字 URL 测试 `/health`。数字地址成功而 `.local` 失败时，问题位于 mDNS、VPN、代理 Fake-IP 或路由器隔离，参见 `docs/troubleshooting.md`。

## 4. 校验下载

把 ZIP 和 `.sha256` 文件放在同一目录，在 PowerShell 运行：

```powershell
Get-FileHash -Algorithm SHA256 .\OTPigeon-windows-x64.zip
Get-Content .\OTPigeon-windows-x64.zip.sha256
```

两处哈希值应完全相同。
