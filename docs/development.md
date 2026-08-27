# 开发与构建

## 环境

- Windows 10/11
- Python 3.10–3.12
- PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
```

## 本地运行

```powershell
.venv\Scripts\python run_otpigeon.py
```

配置写入 `%LOCALAPPDATA%\OTPigeon\config.json`。测试或截图前不要把真实 token 放进仓库。

程序运行时可在另一个终端直接检查 mDNS 记录（不会输出 token）：

```powershell
.venv\Scripts\python scripts\mdns_smoke.py
```

## 构建 EXE

```powershell
.venv\Scripts\pyinstaller --noconfirm --clean otpigeon.spec
```

输出位于 `dist\OTPigeon.exe`。发布包还必须包含：

- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `README.md`
- `guide\iphone-shortcuts.html`

## 发布前门槛

1. `pytest` 全部通过。
2. 在干净 Windows 环境启动 EXE，确认没有 Python 依赖。
3. 防火墙只勾选专用网络。
4. iPhone 使用数字地址通过 `/health`。
5. iPhone 使用 `.local` 地址通过 `/health` 和 `/check`。
6. 热点重开或地址改变后，Shortcut 不修改仍可通过。
7. 真实短信能复制 OTP，失败事件不泄露正文、token 或完整验证码。
8. 检查发行包第三方许可。

没有完成第 4–7 项时，只能发布为 pre-release。

注意：Windows 上的 `Resolve-DnsName` 可能被代理 Fake-IP 模式接管。开发验收应同时核对 `_otpigeon._tcp.local.` 服务记录中的地址确实属于当前 RFC1918 接口，并以 iPhone 真机访问结果作为最终门槛。
