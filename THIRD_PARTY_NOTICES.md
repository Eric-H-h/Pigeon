# Third-party notices

OTPigeon 的源码依赖以下第三方项目。发布二进制前应再次核对实际锁定版本及其随包许可证文件。

| Package | Version | Purpose | License |
| --- | --- | --- | --- |
| ifaddr | 0.2.0 | 枚举本机网络接口 | MIT |
| PyInstaller | 6.20.0 | 仅用于构建 Windows 可执行文件 | GPL-2.0-or-later with bootloader exception |

上述项目的许可证全文保存在 [`licenses/`](licenses/)；发行包必须同时包含该目录与 OTPigeon 的 `LICENSE`。V0.2.0 Alpha 7 不包含 `python-zeroconf` 或其他 mDNS 运行时依赖。pytest 等测试工具只用于开发环境，不会打包进 EXE。
