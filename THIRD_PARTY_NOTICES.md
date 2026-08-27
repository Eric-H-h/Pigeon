# Third-party notices

OTPigeon 的源码依赖以下第三方项目。发布二进制前应再次核对实际锁定版本及其随包许可证文件。

| Package | Version | Purpose | License |
| --- | --- | --- | --- |
| ifaddr | 0.2.0 | 枚举本机网络接口 | MIT |
| python-zeroconf | 0.150.0 | 在局域网发布 `.local` 名称和服务 | LGPL-2.1-or-later |
| PyInstaller | 6.20.0 | 仅用于构建 Windows 可执行文件 | GPL-2.0-or-later with bootloader exception |
| pytest | 8.x | 仅用于测试 | MIT |

许可证全文保存在 [`licenses/`](licenses/)；发行包必须同时包含该目录与 OTPigeon 的 `LICENSE`。官方发行流程还附带精确版本的 zeroconf 源码、OTPigeon 对应提交源码和重建说明，见 [`docs/lgpl-rebuild.md`](docs/lgpl-rebuild.md)。本项目未修改上游 zeroconf。该工程措施不替代发行者自己的许可证审查；若具体发行方式仍不能满足要求，应停止发布该二进制或改用许可边界更清晰的本机 mDNS 实现。
