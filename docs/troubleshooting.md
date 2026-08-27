# 故障排查

按从底层到上层的顺序检查，不要一上来重建自动化。

## 1. Windows 是否在运行

OTPigeon 窗口应显示 `Running` 或 `Degraded`，并列出 `PC address`。若提示端口被占用，关闭另一个 OTPigeon 实例或占用 8765 的程序后重启。

## 2. iPhone 与 Windows 是否在同一网络

推荐：Windows 开启移动热点，iPhone 的 Wi-Fi 明确连接该热点。关闭 iPhone 的 VPN 或会接管局域网流量的代理后再测试。

家庭 Wi-Fi 需要关闭 AP isolation / Client isolation；访客网络通常默认隔离设备。

## 3. 先测数字地址

在 Windows 窗口的 `Available links` 找到数字地址，在 iPhone Safari 打开：

```text
http://数字地址:8765/health
```

如果看不到 `OTPigeon OK`：

- 确认 Windows 防火墙允许 OTPigeon 的专用网络访问；
- 确认 iPhone 没有连到另一个 Wi-Fi；
- 确认地址来自当前正在使用的接口。

## 4. 再测稳定名称

数字地址成功后，打开：

```text
http://otpigeon-xxxxxxxx.local:8765/health
```

数字地址成功、`.local` 失败，说明 HTTP 服务正常，问题只在 mDNS/名称解析。可以重启 OTPigeon、切换一次 iPhone Wi-Fi，或临时把 Shortcut 改成数字地址。请在 issue 中附上脱敏后的网络接口名称和错误类型，不要附 token。

部分代理/VPN 的 Fake-IP 模式会让 **Windows 自己**把 `.local` 映射到 `198.18.0.0/15` 测试网段。OTPigeon 不会发布这个网段；看到 `198.18.x.x` 通常表示系统 DNS 被代理接管，不能据此判断 iPhone 的 mDNS 一定失败。关闭代理的 Fake-IP/DNS 劫持，或把 `*.local` 加入直连/真实解析规则后重试。最终仍以 iPhone Safari 打开稳定地址为准。

## 5. `/check` 返回错误

- `403 Invalid token`：Shortcut 中的 `token` 与 Windows 当前 token 不一致。重新复制，避免首尾空格。
- `415 Content-Type must be application/json`：`Get Contents of URL` 的 Request Body 不是 JSON。
- `400`：字段名或 JSON 结构错误。字段名必须严格是 `token`。

## 6. `/otp` 能连接但不复制

- `422 OTP not found`：短信没有唯一的 4–8 位数字，或包含多个无法判定的数字。
- Windows 显示 `OTP copied` 但无法粘贴：检查目标应用是否禁止粘贴，并手动测试 Windows 剪贴板。
- 自动化没有触发：确认 Message 条件、`Run Immediately` 和「运行现有 Shortcut」均已配置。

## 7. IP 改变了怎么办

Shortcut 使用 `otpigeon-xxxxxxxx.local` 时通常无需修改。若正在用数字 IP，先恢复稳定名称；只有 `.local` 在当前网络确实不可用时才更新数字地址。
