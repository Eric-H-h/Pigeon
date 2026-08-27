# Third-party notices

OTPigeon 的源码依赖以下第三方项目。发布二进制前应再次核对实际锁定版本及其随包许可证文件。

| Package | Version | Purpose | License |
| --- | --- | --- | --- |
| ifaddr | 0.2.0 | 枚举本机网络接口 | MIT |
| python-zeroconf | 0.150.0 | 在局域网发布 `.local` 名称和服务 | LGPL-2.1-or-later |
| PyInstaller | 6.20.0 | 仅用于构建 Windows 可执行文件 | GPL-2.0-or-later with bootloader exception |
| pytest | 8.x | 仅用于测试 | MIT |

许可证全文保存在 [`licenses/`](licenses/)；发行包必须同时包含该目录与 OTPigeon 的 `LICENSE`，并保留构建流程与依赖版本，使接收者可以从对应源码重建。`python-zeroconf` 的 LGPL 合规性是发布门槛；若发行方式不能满足其许可要求，应在公开发布前改用许可边界更清晰的本机 mDNS 实现。
