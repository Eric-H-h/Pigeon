# 故障排查

按从底层到上层的顺序检查，不要一开始就重建快捷指令或个人自动化。

## 1. Windows 是否在运行

Pigeon 中文界面应显示“运行中”，并在“快捷指令 URL”中显示类似 `http://192.168.5.101:8765/otp` 的完整地址。若提示端口被占用，关闭另一个 Pigeon 实例或占用 8765 的程序后重启。

## 2. Windows 是否使用专用网络

打开“设置 → 网络和 Internet → Wi-Fi（或以太网）→ 当前连接”，确认“网络配置文件类型”为 **专用网络**。

再打开“Windows 安全中心 → 防火墙和网络保护 → 允许应用通过防火墙”，找到 Pigeon：

- 勾选“专用”；
- 取消“公用”；
- 如有多个旧版项目，确认当前 Pigeon.exe 对应的项目也按上述方式设置。

如果把网络改成“公用”后反而可以连接，说明防火墙规则只允许公用网络。请修正应用权限并把网络改回专用，不要把公用网络当成长期解决方案。

## 3. iPhone 与 Windows 是否在同一局域网

推荐让两台设备连接同一台受信任路由器，或者让 iPhone 连接 Windows 移动热点。家庭或自有路由器需要关闭 AP isolation / Client isolation；访客网络通常默认隔离设备。

比较两台设备的地址。例如：

```text
Windows: 192.168.5.101
iPhone:  192.168.5.134
Router:  192.168.5.1
```

前三段相同通常说明它们位于同一 `/24` 局域网。若 iPhone 是另一个网段，先检查是否连错 Wi-Fi、进入访客网络或被路由器划分到另一个 VLAN。

## 4. 先测数字地址

复制窗口中的“快捷指令 URL”，把末尾 `/otp` 替换成 `/health`，再在 iPhone Safari 打开：

```text
http://192.168.5.101:8765/health
```

成功时页面显示 `Pigeon OK`。如果失败：

- 确认没有把旧 IP 留在 Safari 或 Shortcut 中；
- 确认 Windows 与 Pigeon 防火墙权限都是“专用”；
- 确认 iPhone VPN 或代理没有阻止局域网访问；
- 如果窗口列出多个地址，选择与 iPhone 同一网段的地址。

## 5. `/check` 返回错误

- `403 Invalid token`：Shortcut 中的 `token` 与 Windows 当前 token 不一致。重新复制，避免首尾空格。
- `415 Content-Type must be application/json`：`Get Contents of URL` 的 Request Body 不是 JSON。
- `400`：字段名或 JSON 结构错误。字段名必须严格是 `token`。

## 6. `/otp` 能连接但不复制

- `422 OTP not found`：短信没有唯一的 4–8 位数字，或包含多个无法判定的数字。
- Windows 显示 `OTP copied` 但无法粘贴：检查目标应用是否禁止粘贴，并手动测试 Windows 剪贴板。
- 自动化没有触发：确认 Message 条件、`Run Immediately` 和“运行现有 Shortcut”均已配置。

## 7. IP 改变了怎么办

Pigeon 每 5 秒检测一次当前私有 IPv4 地址，窗口会自动生成新的完整 `/otp` URL。复制新 URL，打开普通 `Send to Pigeon` Shortcut，用它完整替换旧 URL。个人自动化不需要重建。

如果经常连接同一台路由器，可以在路由器中为 Windows 配置 DHCP 地址保留，减少地址变化。该设置只应在自己的受信任路由器上完成。
