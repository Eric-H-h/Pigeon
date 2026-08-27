# 开发历史与旧版迁移

## PoC

最初的个人版本证明了链路可行：Message 自动化把短信正文 POST 到 Python HTTP 服务，Windows 提取验证码并写入剪贴板。

PoC 的主要限制是：

- 在快捷指令中写死 `192.168.137.1`；
- token 写在源码中；
- 快捷指令动作直接塞进个人自动化，不利于分享；
- 没有明确的错误协议、输入上限、隐私边界和发行流程。

下图是旧版动作配置，仅用于解释迁移动机，**不要照抄其中的固定 IP**：

![旧版快捷指令写死数字 IP](images/legacy-fixed-ip-actions.jpg)

## V0.2

V0.2 命名为 **OTPigeon**，把 PoC 拆为可测试模块，并增加：

- 每次安装独立的稳定 `.local` 名称；
- 私有 IPv4 接口变化监视与数字地址兜底；
- 随机持久化 token 和重新生成操作；
- JSON、长度和 Content-Type 限制；
- Windows 剪贴板历史/云同步排除标记；
- GUI 状态与脱敏事件；
- 普通 Shortcut + 个人自动化的可分享结构；
- 自动测试、PyInstaller 构建和 CI。

旧版源码和原始交接记录在重构前已做本地备份；脱敏副本分别保存在 [`legacy/`](../legacy/) 与 [`docs/archive/`](archive/) 供追溯。公开仓库不保留任何真实 token。
