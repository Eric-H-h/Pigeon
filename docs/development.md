# 开发与构建

## 环境

- Windows 10/11
- Python 3.10–3.12
- PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-build.lock
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m pytest
```

运行时依赖只有 `ifaddr`，用于枚举本机网络接口。V0.2.0 Alpha 8 不使用 `python-zeroconf` 或 mDNS 发布逻辑。

## 本地运行

```powershell
.venv\Scripts\python run_otpigeon.py
```

配置写入 `%LOCALAPPDATA%\OTPigeon\config.json`。测试或截图前不要把真实 token 放进仓库。

启动后可用窗口显示的数字地址检查服务：

```powershell
curl.exe --noproxy "*" http://当前数字IP:8765/health
```

## 构建 EXE

```powershell
.venv\Scripts\pyinstaller --noconfirm --clean otpigeon.spec
```

输出位于 `dist\OTPigeon.exe`。发布包还必须包含：

- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `README.md`
- `QUICKSTART.md`
- `RELEASE_NOTES.md`
- `SECURITY.md`
- `guide\iphone-shortcuts.html`

## 发布前门槛

1. `pytest` 全部通过，文档链接检查通过。
2. 在干净 Windows 环境启动 EXE，确认没有 Python 依赖。
3. Windows 网络类别为“专用”，OTPigeon 防火墙只勾选“专用”。
4. 窗口上方显示以 `/otp` 结尾的完整 Shortcut URL，下方显示当前真实私有 IPv4 地址，不出现 `.local` 地址。
5. `Language` 可在中文和 English 间切换，重启后保持选择；中文界面保留 `token`、`IP`、`URL`、`OTP` 等术语。
6. iPhone 使用该数字地址通过 `/health` 和 `/check`。
7. 地址改变后窗口自动刷新；更新普通 Shortcut 的 URL 后恢复连接。
8. 真实短信能复制 OTP，失败事件不泄露正文、token 或完整验证码。
9. 检查发行包第三方许可和 SHA-256。

没有完成第 4–7 项时，只能发布为 pre-release。
