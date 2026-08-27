# 修改 python-zeroconf 并重建 OTPigeon

OTPigeon V0.2 使用 `python-zeroconf 0.150.0`，其许可证为 LGPL-2.1-or-later。官方发行构建设置 `SKIP_CYTHON=1`，从已校验 SHA-256 的上游源码包构建纯 Python 版本，再将其与 OTPigeon 一起打包。

发行 ZIP 的 `third-party-source/` 应包含：

- `zeroconf-0.150.0.tar.gz`：实际使用版本的完整上游源码；
- `third_party_sources.lock.json`：下载地址、版本和 SHA-256；
- `otpigeon-source.zip`：对应发行提交的 OTPigeon 源码和构建配置。

## 重建原始版本

在 Windows 和 Python 3.10 中解压 `otpigeon-source.zip`，然后运行：

```powershell
py -3.10 -m venv .venv
$env:SKIP_CYTHON = "1"
.venv\Scripts\python -m pip install -r requirements-build.lock
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m pytest
.venv\Scripts\pyinstaller --noconfirm --clean otpigeon.spec
```

`requirements-build.lock` 中的 zeroconf 条目直接指向上述源码包的同一官方 URL，并固定 SHA-256。构建环境必须设置 `SKIP_CYTHON=1`；GitHub Actions 已这样配置。

## 使用修改后的 zeroconf

1. 解压 `zeroconf-0.150.0.tar.gz` 并修改其源码。
2. 创建上面的构建环境。
3. 卸载锁定版本，并以纯 Python 方式安装修改副本：

```powershell
.venv\Scripts\python -m pip uninstall -y zeroconf
$env:SKIP_CYTHON = "1"
.venv\Scripts\python -m pip install --no-cache-dir --no-deps .\zeroconf-0.150.0
.venv\Scripts\pyinstaller --noconfirm --clean otpigeon.spec
```

生成的 `dist\OTPigeon.exe` 会包含修改后的库。OTPigeon 没有修改上游 zeroconf 源码。

本页说明项目提供的重建材料和工程流程，不构成法律意见。正式分发者仍应自行确认其具体发行方式满足许可证义务。
