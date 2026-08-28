# iPhone Shortcut

OTPigeon 需要两部分：

1. 可导出分享的普通 Shortcut：`Send to OTPigeon`；
2. 每个用户必须在自己 iPhone 上创建的 Message Personal Automation。

iOS 不允许把个人自动化触发器随普通 Shortcut 一起分享，因此仓库不能提供“一键完成全部设置”的文件。

当前请按 [guide/iphone-shortcuts.html](../guide/iphone-shortcuts.html) 创建普通 Shortcut。完成 Windows + iPhone 真机验收后，由项目所有者从 iPhone 导出最终 `.shortcut` 文件，再放到本目录；在此之前不应伪造或上传未经签名/未经验证的 Shortcut 文件。

导出前确认：

- URL 使用用户自己电脑窗口显示的当前数字 IP，例如 `http://192.168.5.101:8765/otp`；
- 分享文件不得包含维护者自己的数字 IP；导入后必须引导用户填写自己的地址；
- 示例 token 是占位符，不包含维护者的真实 token；
- 导入后引导用户填写自己的地址和 token，并说明 IP 改变时只更新这一个 URL；
- `Request Body` 为 JSON，字段严格为 `token` 和 `text`；
- `text` 的值来自 `Shortcut Input`。
