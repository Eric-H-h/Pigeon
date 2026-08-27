# OTPigeon V0.2 完整修改方案

> 文档状态：已执行本地实现；等待 iPhone 真机门槛与 GitHub 远端授权
> 制定日期：2026-08-27  
> 执行快照：2026-08-28
> 项目名称：OTPigeon  
> 当前目标版本：V0.2 可分享 MVP  
> iPhone 验证基线：iOS 18.4.1  

## 1. 这份方案要解决什么问题

当前个人 PoC 已经证明了核心链路可行：iPhone 收到验证码短信后，Message Personal Automation 能在锁屏状态下运行 Shortcuts，把短信通过局域网发给 Windows；Windows 随后提取验证码并写入剪贴板。

V0.2 不再验证“能不能做到”，而是解决“其他人能不能安全、稳定地装起来并长期使用”。最终希望普通用户只经历一次安装和配置：

```text
下载 OTPigeon.exe
→ 双击运行
→ 安装 Send to OTPigeon Shortcut
→ 手动创建一次 Message Personal Automation
→ 以后收到验证码时直接在 Windows Ctrl+V
```

这份文档最初只用于制定方案。用户确认执行后，本地代码、测试、文档、Git 基线、EXE 和预发布 ZIP 已完成；GitHub 远端创建/推送与 iPhone V0.2 真机验收仍按文末门槛处理。

## 2. 已确认的产品决策

### 2.1 隐私边界

OTPigeon 运行时保持零云端：

- 短信正文和 OTP 不发送给云服务器、LLM、分析平台或第三方接口。
- Windows 只在内存中处理短信，不保存完整短信历史。
- OTP 只写入当前 Windows 剪贴板，不进入应用日志。
- 共享 Shortcut 可以按 Apple 的机制经 iCloud 链接或文件分发，但其中不得嵌入创建者的地址和 Token。

这里需要区分“运行时数据”和“Shortcut 定义文件”：Apple 说明，共享 Shortcut 时会接收一份 Shortcut 副本用于验证。因此公开表述应是“短信和 OTP 在运行时不经过云端”，而不是笼统声称“任何内容都不经过云端”。

### 2.2 网络支持范围

V0.2 按以下层级定义支持范围：

1. **正式支持：Windows Mobile Hotspot。**这是默认安装教程和必须通过的验收路径。
2. **条件支持：家庭私有局域网。**如果同一套 mDNS 实现可以自然工作，则提供支持；不为特殊路由器单独增加复杂实现。
3. **不承诺支持：酒店、校园、公司访客网络等公共 Wi-Fi。**这类网络可能启用 AP/Client Isolation，使设备即使在同一 Wi-Fi 下也无法互访。
4. **明确不支持：公网访问和云中转。**

家庭局域网失败不会阻塞 V0.2 发布。用户应改用 Windows 热点，而不是继续调试路由器。

### 2.3 平台边界

- iPhone 的首个正式验证版本为 iOS 18.4.1。
- Windows 首先支持 Windows 11 x64。
- 发布前必须在一台没有安装 Python 的干净 Windows 11 机器上验证 EXE。
- Windows 10 只做尽力兼容，不在没有实测证据时写入正式支持列表。

### 2.4 V0.2 不包含的功能

- 浏览器自动填充或自动提交验证码。
- 自动点击网站的“发送验证码”。
- iOS 原生 App、Android App 或浏览器扩展。
- 云端发现、云端中转、用户账号或遥测。
- 自动更新、复杂 Installer、开机自启动和系统托盘。
- 二维码自动配对。二维码可在后续版本实现，但不能在未验证 Shortcuts 本地配置持久化前加入核心范围。

## 3. 当前目录与主要问题

当前目录只有：

```text
otp_bridge.py
iPhone_Windows_OTP_Bridge_Codex_Handoff.md
```

目录尚未初始化为 Git 仓库。

### 3.1 应当保留的行为

- iPhone 只转发短信，OTP 解析留在 Windows。
- `GET /health` 和 `POST /otp` 的基本行为。
- 4～8 位数字 OTP 的核心提取规则。
- Token 验证、掩码状态输出和不记录完整短信的原则。
- Windows 监听局域网、成功后写入剪贴板的完整链路。

### 3.2 公开前必须修正的问题

1. `otp_bridge.py` 和交接文档包含固定测试 Token，不能原样进入公开 Git 历史。
2. `clip.exe` 无法阻止 OTP 进入 Windows Clipboard History 或 Cloud Clipboard。
3. HTTP 请求体没有大小上限，JSON 和字段类型没有严格验证。
4. 所有异常统一返回 500，无法区分用户配置错误和程序错误。
5. IP 检测如果依赖“默认路由”或“第一个 IPv4”，会被 VPN、代理或 VMware 网卡误导。
6. 没有配置持久化、GUI、自动化测试、打包配置和公开 README。
7. 没有 GitHub Release、校验值、许可证和第三方许可证说明。

## 4. 用户最终使用流程

### 4.1 Windows

1. 用户从 GitHub Release 下载 `OTPigeon.exe`。
2. 第一次运行时，程序创建本机配置和随机 Token。
3. Windows 防火墙提示出现时，用户只允许 Private Network。
4. GUI 显示运行状态、稳定局域网名称、数字地址候选和掩码 Token。
5. 用户把稳定地址和 Token 填入共享 Shortcut 的导入问题。

GUI 中的主地址应类似：

```text
http://otpigeon-a1b2c3d4.local:8765
```

数字 IP 只作为故障回退，不作为日常配置入口。

### 4.2 iPhone

1. 用户安装 `Send to OTPigeon` 普通 Shortcut。
2. 导入时填写：
   - `PC Address`：稳定的 `.local` 地址；
   - `Pairing Token`：Windows GUI 显示的随机 Token。
3. 用户手动创建 Message Personal Automation：
   - Message Contains：`验证码`；
   - Run Immediately；
   - Run Shortcut：`Send to OTPigeon`；
   - Input：`Shortcut Input`。
4. 用户手动运行一次 Shortcut 做连接测试。
5. 后续收到短信时，Shortcut 在后台发送正文，Windows 自动复制 OTP。

Personal Automation 本身不能作为项目主要分享单元，所以 GitHub 需要提供逐步截图或清晰图文说明。

## 5. IP 变化的最终方案

### 5.1 为什么不能只“自动检测一个 IP”

用户电脑可能同时存在 Wi-Fi、Windows Hotspot、VPN、代理隧道、Hyper-V、VMware 和 APIPA 地址。当前开发机的默认路由会返回 `198.18.0.1` 的代理/隧道地址，而 iPhone 实际需要访问的是 `192.168.0.x` 或 Windows 热点的 `192.168.137.1`。

因此以下实现都不可靠：

- 取 `socket.gethostbyname(hostname)` 的结果；
- 通过连接公共 DNS 推导默认出口地址；
- 取枚举结果中的第一个非回环 IPv4；
- 直接使用 Windows 计算机名加 `.local`，因为系统可能把它解析到错误的虚拟接口。

### 5.2 主方案：自定义 mDNS 稳定名称

首次启动生成一个稳定安装 ID，例如 `a1b2c3d4`，并构造：

```text
主机名：otpigeon-a1b2c3d4.local.
服务类型：_otpigeon._tcp.local.
端口：8765
```

Shortcut 保存主机名，而不是数字 IP。IP 改变后，Windows 重新广播相同主机名和新的接口地址，Shortcut 无需修改。

### 5.3 必须按网络接口分别发布

不能把所有 IPv4 地址装进同一个 mDNS 记录。否则 iPhone 可能收到 Wi-Fi、VMware 和 VPN 地址，并选中无法到达的那个。

`network.py` 应为每个符合条件的接口分别创建发布实例：

```text
Windows Hotspot 接口
→ 在该接口发布 otpigeon-a1b2c3d4.local → 192.168.137.1

家庭 Wi-Fi 接口
→ 在该接口发布 otpigeon-a1b2c3d4.local → 192.168.0.x
```

iPhone 在哪个本地链路发出 mDNS 查询，就只会收到该链路上的有效响应。

### 5.4 地址筛选规则

默认只考虑正在使用的 IPv4 接口，并排除：

- `127.0.0.0/8` 回环地址；
- `169.254.0.0/16` APIPA 地址；
- `198.18.0.0/15` 基准测试/代理隧道地址；
- `0.0.0.0`、广播、多播和无效地址；
- 明确识别出的 VPN、隧道接口。

对 RFC1918 私有地址逐接口发布即可。VMware 等仅在宿主机内部存在的接口即使被发布，iPhone 也不会在那个链路收到广播；仍应尽量在地址清单中标注并降低显示优先级。

### 5.5 网络变化监控

V0.2 不需要复杂的 Windows 网络事件订阅。`network.py` 每 5 秒重新计算一次符合条件的接口集合：

1. 集合未变化：不执行操作。
2. 新接口出现：在新接口注册 mDNS。
3. 地址变化：更新该接口的 A/SRV 记录。
4. 接口消失：注销并关闭旧发布实例。

轮询逻辑应隐藏在网络模块内部，GUI 和 HTTP 服务器只读取稳定名称、当前地址列表和状态。

### 5.6 iOS 18.4.1 真机验证门槛

mDNS 必须先通过一个独立的小实验，再进入正式实现。实验不重构 PoC，只验证寻址假设。

验证步骤：

1. Windows 开启 Mobile Hotspot，iPhone 连接该热点。
2. Windows 临时发布 `otpigeon-test.local`，指向当前热点接口。
3. iOS 18.4.1 Shortcuts 使用 `Get Contents of URL` 请求：

   ```text
   http://otpigeon-test.local:8765/health
   ```

4. 在解锁状态确认返回健康响应。
5. 锁屏后通过 Message Automation → Run Shortcut 完成一次真实 POST。
6. 重启服务、关闭并重新开启热点，确认名称仍能恢复解析。
7. 同时开启 Meta Tunnel/VPN，确认 iPhone 不会拿到隧道地址。

通过条件：七项全部成功，并且不要求用户安装 Bonjour 或修改 iPhone DNS。

### 5.7 mDNS 验证失败时的降级方案

按以下顺序排查，但不扩大范围：

1. 确认 Windows 防火墙允许该 EXE 在 Private Network 上使用 TCP 8765 和 UDP 5353。
2. 确认 `python-zeroconf` 绑定的是热点接口，而不是默认路由。
3. 用 Windows 原生 `DnsServiceRegister` 做一次对照实验，判断问题来自第三方库还是 iOS/网络。
4. 如果 iOS 18.4.1 的 Shortcut 仍无法稳定解析，则 V0.2 退回“热点专用数字地址模式”：GUI 动态显示当前热点地址，Shortcut 通过导入问题保存该地址。

降级后应明确承认限制：如果数字地址变化，用户需要重新配置 Shortcut。不能为了隐藏这个限制而加入云发现、管理员级网络改写或未验证的扫描逻辑。家庭局域网同时延期。

## 6. 安全与隐私修改

### 6.1 Token 生成和存储

首次运行使用 `secrets` 生成至少 128 位随机 Token。配置保存到：

```text
%LOCALAPPDATA%\OTPigeon\config.json
```

选择 `LOCALAPPDATA` 而不是漫游的 `APPDATA`，因为 Token 和设备 ID 都属于当前电脑，不应随账号漫游到其他机器。

配置字段：

```json
{
  "schema_version": 1,
  "install_id": "a1b2c3d4...",
  "token": "随机生成的 token",
  "port": 8765
}
```

要求：

- 使用临时文件加 `os.replace` 原子写入，避免断电产生半个 JSON。
- 日志中不打印完整 Token。
- GUI 默认掩码显示，只有明确点击后才复制或显示。
- “重新生成 Token”必须二次确认，并提示旧 Shortcut 会立即失效。
- 不引入 DPAPI：同一 Windows 用户本来就能读取当前剪贴板，DPAPI 对当前威胁模型增加的价值不足以抵消实现复杂度。

### 6.2 HTTP 输入限制

`POST /otp` 和 `POST /check` 必须执行：

- 请求体最大 16 KiB；
- `Content-Type` 必须是 JSON；
- 顶层必须是 JSON Object；
- `token` 必须是字符串；
- `text` 必须是字符串且长度受限；
- Token 使用 `hmac.compare_digest`；
- 连接和读取设置超时；
- 异常响应不得包含短信、Token 或 Python 堆栈。

推荐状态码：

| 状态码 | 含义 |
|---|---|
| 200 | 请求成功 |
| 400 | JSON 或字段格式错误 |
| 403 | Token 错误 |
| 404 | 路径不存在 |
| 413 | 请求体过大 |
| 415 | Content-Type 不受支持 |
| 422 | 没有识别到唯一 OTP |
| 500 | 服务器内部错误 |

### 6.3 敏感剪贴板

`clip.exe` 应替换为 Win32 Clipboard 实现，并在写入 `CF_UNICODETEXT` 的同时设置：

- `ExcludeClipboardContentFromMonitorProcessing`；
- `CanIncludeInClipboardHistory = 0`；
- `CanUploadToCloudClipboard = 0`。

目标是阻止 Windows Clipboard History 和 Cloud Clipboard 收录 OTP。第三方剪贴板管理器未必遵守这些标记，因此 README 仍需说明这个边界。

### 6.4 日志原则

日志只记录：

- 时间；
- 成功、认证失败、未识别、网络错误等事件类型；
- OTP 掩码，例如 `6****1`；
- 必要时记录客户端局域网 IP。

不得记录完整短信、完整 OTP、完整 Token、请求体或配置文件内容。V0.2 默认不写持久日志文件，GUI 只显示本次运行的最近状态。

### 6.5 HTTP 明文的适用边界

V0.2 不实现自签名 HTTPS，因为 iOS Shortcut 的证书信任和普通用户配置成本会显著扩大范围。HTTP 只允许在 Windows 热点或可信私有局域网中使用；Token 用于防止未经授权的请求，但不能把不可信公共网络变成安全网络。

## 7. Windows 模块设计

V0.2 使用少量深模块：每个模块对外暴露小接口，把平台细节和错误处理藏在内部。

| 文件 | 模块职责 | 对外接口 | 主要验证方式 |
|---|---|---|---|
| `config.py` | 创建、校验、原子保存配置 | `load_or_create()`、`regenerate_token()` | 临时目录单元测试 |
| `otp.py` | 纯文本 OTP 提取 | `extract_otp(text)` | 表驱动单元测试 |
| `clipboard.py` | 写入敏感 Windows 剪贴板 | `copy_sensitive(text)` | Windows 集成测试、Win+V 手测 |
| `network.py` | 枚举接口、发布稳定名称、监听变化 | `LocalEndpointPublisher` | 模拟接口快照、真机 mDNS 测试 |
| `server.py` | HTTP 路由、验证、状态码和生命周期 | `BridgeServer.start()`、`stop()` | localhost 集成测试 |
| `ui.py` | 展示状态和用户操作 | `run_ui(runtime)` | 手动 UI 验收 |
| `main.py` | 组合配置、网络、服务器、剪贴板和 GUI | `main()` | 启动/关闭烟雾测试 |

不再继续拆分 HTTP Handler、正则表达式或按钮回调。只有当一个变化点出现第二种真实实现时，才增加新的 Adapter 或接口。

### 7.1 建议目录

```text
src/
└─ otpigeon/
   ├─ __init__.py
   ├─ main.py
   ├─ config.py
   ├─ network.py
   ├─ server.py
   ├─ otp.py
   ├─ clipboard.py
   └─ ui.py
```

### 7.2 OTP 提取规则

V0.2 正式承诺：

- 支持与“验证码、校验码、动态码、短信码、OTP、verification code、one-time code、code”邻近的 4～8 位数字。
- 支持短信中只有一个独立 4～8 位数字时的兜底提取。
- 使用 Unicode NFKC 规范化，把常见全角数字转换为 ASCII 数字。
- 多个候选且无法通过关键词确定时返回 `None`。

V0.2 不承诺字母数字混合码。`123-456` 是否支持由测试样本决定；如果加入，应只在关键词邻近时合并，避免把日期或订单号误判为 OTP。

## 8. HTTP 接口定稿

### 8.1 健康检查

```text
GET /health
→ 200 OTPigeon OK
```

保持无认证，便于用户判断网络和防火墙是否连通。它只暴露本地服务存在，不返回 Token、配置或地址清单。

### 8.2 配置检查

```text
POST /check
Content-Type: application/json

{
  "token": "..."
}
```

正确 Token 返回 200，错误 Token 返回 403。这个接口不解析短信、不修改剪贴板，用于 Shortcut 安装后的首次测试。

### 8.3 OTP 接收

```text
POST /otp
Content-Type: application/json

{
  "token": "...",
  "text": "完整短信正文"
}
```

继续保留当前 JSON 字段，避免无收益的协议迁移。成功后先完成剪贴板写入，再返回 200。

## 9. Windows GUI 方案

使用 Python 标准库 `tkinter`，避免引入大型 GUI 框架。

主窗口只显示：

- 服务状态：Starting、Running、Degraded、Stopped；
- 稳定地址：`http://otpigeon-xxxxxxxx.local:8765`；
- 当前数字地址列表；
- 掩码 Token；
- 最近一次接收或错误状态。

按钮：

- `Copy Address`；
- `Copy Token`；
- `Show/Hide Token`；
- `Regenerate Token`；
- `Open Setup Guide`；
- `Stop/Start`（如果不会显著增加线程状态复杂度，否则 V0.2 只提供退出并重启）。

GUI 主线程不得运行 HTTP Server 或网络轮询。后台状态通过线程安全队列传给 GUI，Tkinter 更新仍只发生在主线程。

关闭窗口时依次停止 HTTP Server、mDNS 发布和后台线程，避免 EXE 进程残留。

## 10. iOS 18.4.1 Shortcut 方案

普通 Shortcut 名称：

```text
Send to OTPigeon
```

导入问题：

1. `What is your OTPigeon PC address?`
2. `What is your OTPigeon pairing token?`

主流程：

```text
读取 Shortcut Input
→ 如果输入为空：POST /check，显示连接测试结果
→ 如果输入不为空：POST /otp
→ 成功时保持安静
→ 网络、认证或解析失败时显示简短通知
```

必须验证：

- 普通 Shortcut 包装后，Message Automation 仍能把真实短信正文作为 `Shortcut Input` 传入。
- iOS 18.4.1 锁屏状态下仍会完整运行。
- `Get Contents of URL` 能访问 `.local` 地址。
- 请求失败时不会持续弹出不可关闭的界面或阻断后续自动化。
- 导出的共享 Shortcut 不含开发者的真实地址和 Token。

GitHub 同时提供：

- Apple 导出的 `Send to OTPigeon.shortcut` 文件；
- 可选 iCloud 分享链接；
- `shortcuts/README.md` 中的逐动作复现说明。

即使未来 iCloud 链接失效，用户仍能通过 GitHub 文件或动作说明重新创建。

## 11. GitHub 仓库规划

### 11.1 目标结构

```text
otpigeon/
├─ src/otpigeon/
├─ tests/
│  ├─ test_otp.py
│  ├─ test_config.py
│  ├─ test_server.py
│  └─ test_network.py
├─ shortcuts/
│  ├─ Send to OTPigeon.shortcut
│  └─ README.md
├─ docs/
│  ├─ iphone-setup.md
│  ├─ troubleshooting.md
│  ├─ privacy-and-security.md
│  ├─ architecture.md
│  └─ development-history.md
├─ .github/workflows/
│  ├─ test.yml
│  └─ release.yml
├─ pyproject.toml
├─ otpigeon.spec
├─ README.md
├─ SECURITY.md
├─ THIRD_PARTY_NOTICES.md
├─ LICENSE
└─ .gitignore
```

### 11.2 现有文件如何处理

| 当前文件 | 计划 |
|---|---|
| `otp_bridge.py` | 作为行为基线使用；实施时由测试覆盖后迁移到 `src/otpigeon/`，不长期保留两套运行入口 |
| `iPhone_Windows_OTP_Bridge_Codex_Handoff.md` | 脱敏、删除面向 Codex 的直接指令，整理为 `docs/development-history.md` |
| `OTPigeon_V0.2_Modification_Plan.md` | 执行阶段移动为 `docs/v0.2-modification-plan.md`，保留决策和验收依据 |

### 11.3 第一次 Git 提交前的秘密处理

不能先把当前文件提交为所谓“原始基线”，因为固定 Token 会留在 Git 历史中。正确顺序是：

1. 在仓库外创建仅本地备份。
2. 替换脚本和文档中的真实或测试 Token。
3. 确认没有配置文件、短信样本或个人 IP 信息需要脱敏。
4. 再执行 `git init` 和第一次提交。
5. V0.2 首次运行后重新生成用户自己的 Token，使旧 PoC Token 失效。

### 11.4 许可证

项目自身代码计划采用 MIT License。

`python-zeroconf` 使用 LGPL-2.1-or-later，因此：

- 在 `THIRD_PARTY_NOTICES.md` 中写明名称、版本、项目主页和许可证；
- 发布 ZIP 中包含项目 LICENSE 和第三方许可证文本；
- 依赖版本写入锁定文件，发布时能够复现；
- 保存或链接发布版本对应的源代码，并保留完整构建说明；
- 在发布单 EXE 前单独核对 LGPL 对捆绑和替换依赖的要求，不能把“附许可证文本”当成全部合规结论。

本方案不是法律意见。如果单 EXE 的 LGPL 分发要求无法得到清晰确认，应优先改用 Windows 原生 `DnsServiceRegister`，再相应删除该依赖和许可证条目。

### 11.5 README 必须包含

- 一句话用途和完整工作流。
- 支持平台和网络范围。
- 从 GitHub Release 下载 EXE 的步骤。
- Windows 防火墙只允许 Private Network 的说明。
- iOS 18.4.1 Shortcut 与 Personal Automation 图文步骤。
- 零云端运行边界和 Shortcut 分享验证边界。
- HTTP 明文只适用于可信局域网的说明。
- SmartScreen 预期提示。
- 常见问题：无法访问、Token 错误、没有识别 OTP、公共网络隔离、数字地址变化。
- 卸载方式：退出程序并删除 EXE、删除 `%LOCALAPPDATA%\OTPigeon`、删除 Shortcut 和 Personal Automation。

## 12. 打包和发布方案

### 12.1 PyInstaller

V0.2 使用 PyInstaller 构建 Windows x64 单 EXE：

- `--onefile`；
- `--windowed`；
- 明确包含 Tkinter 和 mDNS 依赖；
- 通过 `.spec` 文件固定图标、版本信息和隐藏导入；
- 构建必须在 Windows Runner 上完成。

源码运行和 EXE 运行应使用同一入口 `otpigeon.main:main`，避免打包版本拥有另一套行为。

### 12.2 GitHub Actions

`test.yml`：

- 在 Windows Runner 安装锁定依赖；
- 运行全部单元测试和不触碰真实剪贴板的集成测试；
- 运行静态语法检查；
- 不上传配置、Token 或测试短信日志。

`release.yml`：

- 只在版本 Tag 或手动触发时构建；
- 生成 `OTPigeon-v0.2.0-windows-x64.zip`；
- ZIP 包含 EXE、LICENSE、THIRD_PARTY_NOTICES 和简短安装说明；
- 生成 SHA-256；
- 默认创建 Draft Release，人工检查后发布。

### 12.3 SmartScreen

第一个未签名 EXE 大概率出现“Windows 已保护你的电脑”。V0.2 应：

- 在 README 和 Release Notes 中提前说明；
- 提供 SHA-256 和可复现构建配置；
- 不使用自签名证书伪装正式签名；
- 项目公开稳定后再评估 SignPath Foundation、Artifact Signing 或 Microsoft Store。

SmartScreen 问题不会阻止技术验收，但会影响公开分发体验，因此必须进入发布说明和后续路线图。

## 13. 分阶段执行计划

### 阶段 0：保护现有成果和清理秘密

修改内容：

- 创建仓库外本地备份。
- 记录当前两个文件的哈希。
- 清理固定 Token 和个人化示例。
- 初始化 Git，提交脱敏后的 PoC 基线。

完成证据：

- 公开候选目录中搜索不到旧 Token。
- Git 历史中不存在旧 Token。
- PoC 基线仍能在原开发机运行。

### 阶段 1：用测试固定现有行为

修改内容：

- 建立 `pyproject.toml`、包目录和测试目录。
- 为 `extract_otp` 建立表驱动测试。
- 为 `/health`、`/otp`、403 和 422 建立 HTTP 测试。
- 用假的剪贴板函数测试服务器，避免测试污染真实剪贴板。

完成证据：

- 现有可用短信样本全部通过。
- 重构前后的 HTTP 行为一致。
- 测试不依赖真实网络和真实剪贴板。

### 阶段 2：安全配置和敏感剪贴板

修改内容：

- 随机 Token、设备 ID 和配置原子持久化。
- 请求大小、字段、Content-Type 和错误响应校验。
- Win32 敏感剪贴板实现。
- 新增 `/check`。

完成证据：

- 首次启动生成 Token，重启后保持不变。
- Token 重置后旧 Token 返回 403。
- 超大请求返回 413，错误 JSON 返回 400。
- Win+V 中看不到 OTP，Cloud Clipboard 不接收该项目。

### 阶段 3：先验证、再实现稳定名称

修改内容：

- 先执行 iOS 18.4.1 mDNS 真机实验。
- 实验通过后实现逐接口发布和 5 秒网络快照刷新。
- GUI 状态模型先以数据对象形式完成，不立即做界面。

完成证据：

- VPN/Meta Tunnel 与热点同时开启时仍解析到热点地址。
- 热点重启后相同 `.local` 名称恢复可用。
- 锁屏 Message Automation 能通过名称完成 POST。

停止条件：

- 如果经过防火墙、接口绑定和原生 Windows mDNS 对照后仍不稳定，则记录证据并启用热点数字地址降级方案，不继续投入家庭局域网适配。

### 阶段 4：极简 GUI 和生命周期

修改内容：

- Tkinter 主窗口。
- 后台启动/停止 HTTP Server 和 mDNS。
- 地址、Token、最近状态和复制按钮。
- 安全退出。

完成证据：

- 窗口可正常关闭，没有残留进程或占用端口。
- GUI 卡顿测试通过。
- 服务器错误不会导致 GUI 崩溃。

### 阶段 5：Shortcut 与用户文档

修改内容：

- 创建普通 Shortcut 和导入问题。
- 逐步编写 iOS 18.4.1 Personal Automation 教程。
- 编写 README、隐私、安全和故障排查文档。

完成证据：

- 第二台 iPhone 导入时看不到开发者地址或 Token。
- 无输入手动运行能完成 `/check`。
- 锁屏收到短信后能自动完成 `/otp`。
- iCloud 链接失效时仍能靠 GitHub 文件或说明重建。

### 阶段 6：打包与干净机器验证

修改内容：

- PyInstaller `.spec`。
- GitHub Actions 测试和 Draft Release 工作流。
- 生成 EXE、ZIP 和 SHA-256。

完成证据：

- 没有 Python 的干净 Windows 11 x64 能直接运行。
- 防火墙教程可以让 iPhone 访问 `/health`。
- EXE 完成与源码相同的 OTP 链路。

### 阶段 7：公开发布前第二用户测试

记录：

- Windows 版本、iPhone 型号和 iOS 版本。
- 使用 Windows 热点还是家庭局域网。
- mDNS 是否成功、首次配置耗时和失败点。
- 防火墙、SmartScreen、Shortcut 导入和短信格式问题。

至少完成一次非开发者机器的端到端测试，再发布 V0.2 正式 Release。

## 14. 测试矩阵

### 14.1 单元测试

| 范围 | 必测情况 |
|---|---|
| OTP 提取 | 中文关键词、英文关键词、唯一数字、多个数字、无数字、全角数字、边界长度 |
| 配置 | 首次创建、重复加载、损坏 JSON、原子替换、Token 重置、Schema 版本 |
| HTTP | 正常请求、错误 Token、错误 JSON、错误类型、超大请求、未知路径 |
| 网络 | 接口增加、删除、地址变化、过滤回环/APIPA/隧道、无有效接口 |

### 14.2 Windows 集成测试

- 真实 Win32 Clipboard 写入和粘贴。
- Win+V 历史排除。
- HTTP Server 启停、端口占用和优雅退出。
- PyInstaller EXE 启动、配置目录和资源加载。
- Private/Public 防火墙配置差异。

### 14.3 iPhone 18.4.1 手动测试

- 解锁状态 `/health`。
- 手动运行 Shortcut `/check`。
- 锁屏 Message Automation `/otp`。
- Windows 热点关闭再开启。
- Windows 同时开启代理/VPN。
- Token 错误、Windows 未启动、iPhone 未连热点时的错误提示。

### 14.4 家庭局域网测试

家庭局域网只做一次普通路由器验证：

- 同一私有 Wi-Fi；
- Windows Network Profile 为 Private；
- mDNS 和 `/health` 可达；
- 真实 OTP POST 成功。

如果失败原因是路由器隔离或多播过滤，记录为已知限制并使用 Windows 热点，不增加路由器专用代码。

## 15. 发布验收清单

### Windows

- [ ] 用户无需安装 Python。
- [ ] 首次启动生成随机 Token 和稳定设备 ID。
- [ ] 配置重启后保持不变。
- [ ] 稳定 `.local` 地址在 Windows 热点下可用，或已按停止条件启用数字地址降级。
- [ ] VPN/代理存在时不会显示或广播错误主地址。
- [ ] `/health`、`/check`、`/otp` 状态码符合文档。
- [ ] OTP 不进入 Clipboard History 和 Cloud Clipboard。
- [ ] 不记录完整短信、OTP 或 Token。
- [ ] 程序退出后端口和后台线程释放。

### iPhone 18.4.1

- [ ] 普通 Shortcut 能接收 Message Automation 的 `Shortcut Input`。
- [ ] 导入问题不包含开发者私人配置。
- [ ] 手动连接检查成功。
- [ ] 锁屏状态端到端成功。
- [ ] 网络和 Token 错误有可理解提示。

### GitHub

- [ ] Git 历史不存在旧 Token、短信样本和不应公开的个人信息。
- [ ] README、LICENSE、SECURITY 和第三方许可证齐全。
- [ ] 源码、测试、Shortcut、复现说明和构建配置齐全。
- [ ] Draft Release 包含 EXE、许可证、SHA-256 和安装说明。
- [ ] 第二位非开发者完成端到端测试。

## 16. 主要风险和处理方式

| 风险 | 影响 | 处理方式 |
|---|---|---|
| iOS 18.4.1 Shortcuts 无法稳定解析自定义 `.local` | IP 自动变化方案失效 | 阶段 3 先做真机门槛；失败则热点数字地址降级 |
| 路由器屏蔽多播或设备互访 | 家庭局域网不可用 | 不做路由器专用适配，切换 Windows 热点 |
| 多网卡把 VPN 地址广播给 iPhone | Shortcut 无法连接 | 逐接口发布，不使用默认路由或混合地址记录 |
| 防火墙拦截 TCP 8765 或 UDP 5353 | 健康检查失败 | 只允许 Private Network，并提供可验证的排查步骤 |
| OTP 进入系统或第三方剪贴板历史 | 隐私边界被破坏 | 设置 Windows 排除格式，并披露第三方工具边界 |
| 未签名 EXE 被 SmartScreen 警告 | 普通用户放弃安装 | 发布说明、SHA-256、可复现构建；后续申请正式签名 |
| Shortcut 分享文件意外包含 Token | 开发者秘密泄露 | 使用导入问题，第二台设备导入检查，发布前静态检查 |

## 17. 执行前仍需满足的门槛

开始实施前只需要确认以下操作授权，不需要重新讨论总体架构：

1. 允许在 `D:\github\otp` 中重构和新增文件。
2. 允许在仓库外创建一次仅本地 PoC 备份。
3. 确认项目自身使用 MIT License。
4. 提供或确认 GitHub 仓库归属；远程创建和推送必须单独获得执行授权。
5. iPhone 在阶段 3 和阶段 5 可用于手动真机验证。

在用户明确说“执行”之前，不进行以上操作。

## 18. 参考依据

### 当前项目证据

- [`legacy/otp_bridge_poc.py`](../../legacy/otp_bridge_poc.py)：脱敏归档的 PoC 实现。
- [`iPhone_Windows_OTP_Bridge_Codex_Handoff.md`](../archive/iPhone_Windows_OTP_Bridge_Codex_Handoff.md)：已经验证的个人链路、原方案和历史约束。

### 官方与上游资料

- [Apple Bonjour Overview](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/NetServices/Introduction.html)：mDNS、`.local` 名称和动态地址发现原理。
- [Microsoft DNS Service Registration](https://learn.microsoft.com/en-us/windows/win32/api/windns/ns-windns-dns_service_register_request)：Windows 10 及以上的 mDNS 注册能力。
- [python-zeroconf API](https://python-zeroconf.readthedocs.io/en/stable/api.html)：按接口注册和运行时刷新接口。
- [python-zeroconf repository](https://github.com/python-zeroconf/python-zeroconf)：LGPL-2.1-or-later 许可证和项目状态。
- [Microsoft Clipboard Formats](https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard-formats)：排除 Clipboard History 和 Cloud Clipboard 的注册格式。
- [Apple Shortcut Import Questions](https://support.apple.com/en-mt/guide/shortcuts/apdf330fd3a0/ios)：共享 Shortcut 时清除并重新询问私人配置。
- [Apple Share Shortcuts](https://support.apple.com/en-euro/guide/shortcuts/apdf01f8c054/ios)：Shortcut 文件和 iCloud 分享时的 Apple 验证机制。
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)：发布源码版本和二进制资产。
- [Microsoft SmartScreen Reputation](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)：未签名和新发布 Windows 程序的预期警告。
