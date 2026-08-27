# iPhone → Windows OTP Bridge：Codex 交接文档

> **给本地 Codex 的接手指令**
>
> 当前只继续推进 **iPhone 短信验证码 → Windows 自动接收/提取/复制到剪贴板 → 可分享给其他用户** 这一条链路。
>
> **暂时不要继续招聘网站 Autofill、Notion、浏览器自动填验证码、自动点击发送验证码、自动提交。**
>
> 当前个人 MVP 已经实际验证成功，请优先在现有可用链路上做“可分发化”，不要重新发明底层方案，也不要先做大规模重构。

---

## 1. 项目目标

解决一个非常具体的问题：

```text
用户在 Windows 浏览器点击「发送验证码」
                ↓
iPhone 收到短信（允许锁屏）
                ↓
iOS Shortcuts Message Automation 自动触发
                ↓
通过局域网 HTTP POST 把短信正文发给 Windows
                ↓
Windows OTP Bridge 提取 4~8 位验证码
                ↓
验证码自动进入 Windows Clipboard
                ↓
用户在网页 Ctrl+V
```

当前目标不是无人值守，也不是绕过验证码；用户仍然亲自点击“发送验证码”，OTP Bridge 只消除：

```text
拿手机 → 解锁 → 打开短信 → 看验证码 → 记住 → 回电脑输入
```

---

## 2. 当前状态：已经验证成功

以下链路已在真实 iPhone + Windows 环境中打通：

- Windows 端 `otp_bridge.py` 可以运行并监听局域网。
- iPhone 可以通过 Windows 自建热点访问电脑。
- `GET /health` 已验证返回 `OTP Bridge OK`。
- iPhone Shortcuts 可以向 Windows 发送 HTTP POST。
- `POST /otp` 已验证可被 Windows 服务接收。
- Windows 可以从短信文本中提取验证码。
- 验证码可以自动写入 Windows Clipboard。
- iPhone **锁屏状态下 Message Automation 也能正常触发**。
- 用户当前已经可以做到：收到短信后不碰手机，直接在电脑 `Ctrl+V` 获取验证码。

因此：

> **核心技术可行性已经验证完毕。后续重点是产品化/可分发化，而不是再验证 iOS 是否能自动转发短信。**

---

## 3. 当前网络方案

当前采用的稳定方案是 Windows 自建热点，而不是依赖公共 Wi-Fi 中的设备互通。

```text
公共 Wi-Fi / 其他上网链路
          ↓
      Windows PC
          ↓
   Windows Mobile Hotspot
          ↓
        iPhone
```

原因：公共路由器可能存在 Client Isolation / AP Isolation，导致 iPhone 与 PC 即使连接同一公共 Wi-Fi 也不能互访。

当前测试环境中 Windows 热点 IP 使用过：

```text
192.168.137.1
```

但**不能在可分发版本中写死该 IP**；应动态检测或让用户选择。

---

## 4. 当前 iPhone Shortcuts 配置

### 4.1 Personal Automation 触发器

在 iPhone（英文界面）：

```text
Shortcuts
→ Automation
→ +
→ Message
```

当前触发条件：

```text
Message Contains: 验证码
Run Immediately
```

`Sender` 不限制。

当前已经确认锁屏时也能触发。

### 4.2 Automation 中的核心动作

当前思路：不要在 iPhone 上解析 OTP；iPhone 只负责把短信内容发给 Windows，解析放在 Windows 上完成。

推荐结构：

```text
Text
[Shortcut Input]

↓

URL
http://<PC_IP>:8765/otp

↓

Get Contents of URL
Method: POST
Request Body: JSON

{
  "token": "<pairing-token>",
  "text":  [Text]
}
```

其中 `[Shortcut Input]` / `[Text]` 是 Shortcuts 的蓝色变量，不是字面字符串。

### 4.3 当前已知点

- 用户的 iOS 版本中没有 `Get Details of Messages` Action，因此不要依赖它。
- 直接把 `Shortcut Input` 放入 `Text` Action 已经可用于当前链路。
- `Settings → Privacy & Security → Local Network` 中未显示 Shortcuts，但实际 HTTP 已成功，因此不要以该设置项是否出现作为链路判断依据。

---

## 5. Windows OTP Bridge 当前基线逻辑

下面是讨论阶段使用的基线实现。**Codex 在本地开始工作前，应先检查用户现有目录中的实际 `otp_bridge.py`，不要无条件覆盖已经跑通的版本。**

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import subprocess
import time

HOST = "0.0.0.0"
PORT = 8765

# 仅测试阶段使用。分发版必须改成首次启动随机生成。
TOKEN = "replace-before-running"

PATTERNS = [
    re.compile(
        r"(?:验证码|校验码|动态码|短信码|OTP|verification\s*code|code)"
        r"\D{0,20}(\d{4,8})",
        re.IGNORECASE
    ),
    re.compile(
        r"(\d{4,8})\D{0,20}"
        r"(?:验证码|校验码|动态码|短信码|OTP|code)",
        re.IGNORECASE
    ),
]


def extract_otp(text):
    for pattern in PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)

    candidates = re.findall(r"(?<!\d)\d{4,8}(?!\d)", text)

    if len(candidates) == 1:
        return candidates[0]

    return None


def copy_to_clipboard(text):
    subprocess.run(
        ["clip.exe"],
        input=text,
        text=True,
        check=True
    )


class Handler(BaseHTTPRequestHandler):

    def send_text(self, status, text):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.send_text(200, "OTP Bridge OK")
        else:
            self.send_text(404, "Not Found")

    def do_POST(self):
        if self.path != "/otp":
            self.send_text(404, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))

            if body.get("token") != TOKEN:
                self.send_text(403, "Invalid token")
                return

            text = str(body.get("text", ""))
            otp = extract_otp(text)

            if not otp:
                print(
                    time.strftime("%H:%M:%S"),
                    "收到短信，但没有找到唯一验证码"
                )
                self.send_text(422, "OTP not found")
                return

            copy_to_clipboard(otp)

            masked = otp[0] + "*" * (len(otp) - 2) + otp[-1]
            print(
                time.strftime("%H:%M:%S"),
                f"验证码已复制到剪贴板: {masked}"
            )

            self.send_text(200, "OK")

        except Exception as e:
            print("Error:", e)
            self.send_text(500, "Error")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"OTP Bridge running on port {PORT}")
    print("等待 iPhone...")
    print("Ctrl+C 退出")
    server.serve_forever()
```

### 当前接口约定

```text
GET  /health
→ 200 "OTP Bridge OK"

POST /otp
Content-Type: application/json

{
  "token": "...",
  "text": "完整短信正文"
}
```

成功：

```text
200 OK
```

Token 错误：

```text
403 Invalid token
```

没有识别到唯一 OTP：

```text
422 OTP not found
```

---

## 6. 当前 MVP 的安全原则

OTP 属于短期认证凭据，分发版本应继续遵守：

- 不上传云端。
- 不调用 LLM 处理短信。
- 不存完整短信历史。
- 不写 OTP 到长期日志。
- 控制台最多显示掩码，例如 `6****1`。
- Windows 防火墙只开放 Private Network。
- 服务只用于局域网。
- Token 不得在所有用户之间共享。
- 不自动点击网站的“发送验证码”。
- 不自动点击最终“提交/确认”。

---

## 7. 为什么当前版本不能直接分享给普通用户

个人 PoC 当前存在这些分发问题：

### 7.1 Windows 依赖 Python

当前用户需要：

```text
安装 Python
打开终端
python otp_bridge.py
```

普通用户体验不好。

### 7.2 IP 写死/需要手查

当前 Shortcut 使用类似：

```text
http://192.168.137.1:8765/otp
```

不同电脑可能不同。

### 7.3 Token 是测试常量

例如：

```text
replace-before-running
```

分发版绝对不能所有人共用。

### 7.4 Personal Automation 本身不适合作为主要可分享单元

应把 HTTP POST 的核心逻辑放进一个普通 Shortcut，例如：

```text
Send OTP to PC
```

用户只需自己创建一次 Personal Automation：

```text
Message Contains: 验证码
Run Immediately
→ Run Shortcut: Send OTP to PC
→ Input: Shortcut Input
```

这样绝大多数逻辑可以通过普通 Shortcut 分享，而 Personal Automation 只剩很少的人工配置步骤。

---

## 8. 下一阶段目标：V0.2 可分享 MVP

目标用户：普通 Windows + iPhone 用户，不要求安装 Python，不要求理解 HTTP。

### 用户最终安装体验建议

#### Windows

```text
下载 OTPBridge.exe
→ 双击
```

界面显示：

```text
OTP Bridge

Status: Running
PC Address: 192.168.xxx.xxx:8765
Pairing Token: XXXXXXXX...

[Copy Address]
[Copy Token]
```

#### iPhone

```text
安装可分享的普通 Shortcut：Send OTP to PC
```

第一次配置时填写：

```text
PC Address
Pairing Token
```

然后用户手动创建一次：

```text
Shortcuts
→ Automation
→ Message
→ Message Contains: 验证码
→ Run Immediately
→ Run Shortcut: Send OTP to PC
```

之后日常使用：

```text
点击网页「发送验证码」
→ iPhone 锁屏收到短信
→ Windows Clipboard 自动获得 OTP
→ Ctrl+V
```

---

## 9. V0.2 推荐技术实现

### 9.1 Windows 打包

建议：

```text
Python + PyInstaller
```

目标：

```text
OTPBridge.exe
```

用户机器无需 Python。

第一版不需要 Installer，也不需要管理员权限；先做到单 EXE 可运行。

### 9.2 极简 GUI

优先考虑 Python 标准库 `tkinter`，避免引入大型 GUI 框架。

界面只需要：

- Running / Stopped 状态。
- 检测到的 LAN IP。
- Port。
- Pairing Token（默认部分掩码，可复制）。
- `Copy Address`。
- `Copy Token`。
- 最近一次接收状态（不要显示完整 OTP）。

不要在 V0.2 一开始做复杂 UI。

### 9.3 Token

首次运行：

```text
secrets.token_urlsafe(...)
```

生成随机 Token。

保存到本地配置文件，例如：

```text
%APPDATA%/OTPBridge/config.json
```

要求：

- 首次生成。
- 后续保持稳定。
- 支持“重新生成 Token”。
- 不在日志中完整打印。

### 9.4 IP 检测

不要硬编码 `192.168.137.1`。

至少实现：

- 枚举当前 IPv4 地址。
- 排除 `127.0.0.1`。
- 优先识别 Windows Mobile Hotspot 对应地址，若不确定则展示多个候选。
- 给用户一个测试按钮或 `/health` 提示。

注意：不要假设所有 Windows 热点都必然使用相同网段。

### 9.5 配置层

建议拆成：

```text
config.py
server.py
otp.py
clipboard.py
network.py
gui.py
main.py
```

但以“保持简单”为优先，不要为了架构漂亮而过度拆分。

---

## 10. 普通 Shortcut 的建议设计

普通 Shortcut 名称：

```text
Send OTP to PC
```

输入：

```text
Shortcut Input = Message Automation 传入的短信
```

动作：

```text
Text
[Shortcut Input]

URL
http://<PC_ADDRESS>/otp

Get Contents of URL
POST
JSON
{
  "token": "<PAIRING_TOKEN>",
  "text": [Text]
}
```

注意：

- 不在 iPhone 解析 OTP。
- 不保存短信。
- 不加入不必要的第三方网络服务。
- 后续可考虑安装时询问 PC Address / Token，但 V0.2 可以先用明确的配置说明。

---

## 11. V0.2 验收标准

Codex 完成第一版可分享 MVP 后，应至少满足：

### Windows

- [ ] 一台没有安装 Python 的 Windows 机器可以直接运行 EXE。
- [ ] 启动后能显示服务状态。
- [ ] 能显示当前可用 PC Address。
- [ ] 首次启动自动生成随机 Token。
- [ ] Token 重启后保持不变。
- [ ] `GET /health` 正常。
- [ ] `POST /otp` 正常。
- [ ] Token 错误返回 403。
- [ ] 合法短信能提取 4~8 位 OTP。
- [ ] OTP 自动写入 Clipboard。
- [ ] 不在日志中暴露完整 OTP 或完整短信。

### iPhone

- [ ] 普通 Shortcut 能接收 Shortcut Input。
- [ ] 能向用户配置的 Windows 地址 POST。
- [ ] 锁屏时 Message Automation → Run Shortcut 仍能工作。
- [ ] 网络失败时至少有可理解的错误提示。

### 文档

- [ ] README 包含安装步骤。
- [ ] README 包含 Windows Firewall / Private Network 说明。
- [ ] README 包含 iPhone 英文界面创建 Automation 的步骤。
- [ ] README 明确说明 OTP 不经过云端。

---

## 12. 建议 Codex 的开发顺序

### Step 0：先检查本地现状

Codex 应先：

1. 查看当前目录结构。
2. 找到实际已跑通的 `otp_bridge.py`。
3. 运行现有测试/手动验证，不要先覆盖。
4. 把现有代码提交/备份为 working baseline（若仓库已使用 Git）。

### Step 1：重构但保持行为不变

把：

```text
HTTP server
OTP extraction
Clipboard
Config
```

做最小必要分离。

要求：原来的 `/health`、`/otp` 行为保持兼容。

### Step 2：随机 Token + 配置持久化

先完成安全问题。

### Step 3：自动检测 IP + 极简 GUI

让用户不再需要 `ipconfig`。

### Step 4：PyInstaller 打包

生成：

```text
OTPBridge.exe
```

在干净 Windows 环境验证。

### Step 5：整理可分享 Shortcut 与 README

不要把 Personal Automation 的全部逻辑写死在用户设备上；尽量把可维护逻辑集中到普通 Shortcut。

### Step 6：邀请第二个用户测试

重点记录：

- Windows 版本。
- iOS 版本。
- 热点/局域网方式。
- IP 检测是否正确。
- Shortcuts 锁屏触发是否稳定。
- 不同验证码短信格式是否能解析。

---

## 13. 当前不要做的事情

为了避免 Codex 把范围扩张，V0.2 暂时不要做：

- 浏览器 Extension 自动填 OTP。
- 自动点击“发送验证码”。
- 自动点击确认/提交。
- 云服务器中转。
- 用户账号系统。
- iOS 原生 App。
- Android App。
- AI/LLM 解析验证码。
- Notion 同步。
- 招聘表单 Autofill。
- 自动更新系统。
- 复杂 Installer。

先把“小而稳、别人能装”的版本做出来。

---

## 14. 后续版本设想（非当前任务）

### V0.3

- 系统托盘运行。
- 开机自启动。
- 更完善的网络适配器选择。
- Shortcut 配置体验优化。

### V0.4

- Windows GUI 显示 QR Code。
- QR 中包含 Address + Token 配对信息。
- iPhone 扫码减少手动输入。

### V1.0

在 OTP Bridge 独立稳定后，再考虑：

```text
Windows OTP Bridge
        ↓
Chrome/Edge Extension
        ↓
识别当前 OTP 输入框
        ↓
自动填写
```

但仍然不自动点击最终提交。

---

## 15. 给 Codex 的直接继续 Prompt

```text
请先阅读这份交接文档，并先检查当前本地项目目录和已经跑通的 otp_bridge.py。

当前个人 MVP 已经验证成功：iPhone 在锁屏状态下收到包含“验证码”的短信后，Shortcuts 可以通过局域网 POST 给 Windows，Windows 可以提取验证码并写入剪贴板。

现在不要重新研究验证码链路，也不要做浏览器 Autofill / Notion / 自动提交。

我们的目标是把当前个人 PoC 做成 V0.2“可分享 MVP”：
1. 普通用户无需安装 Python，直接运行 OTPBridge.exe；
2. 首次启动随机生成并持久化 pairing token；
3. 自动检测/展示可用 LAN IP 和端口；
4. 提供极简 GUI；
5. 保持 GET /health 和 POST /otp；
6. OTP 只进内存/剪贴板，不上传云端、不长期存储；
7. 给 iPhone 提供一个可分享的普通 Shortcut（Send OTP to PC），用户只手动创建一次 Message Personal Automation；
8. 写清楚 README 和测试步骤。

请先 review 本地现有代码，告诉我：
- 当前文件结构和现有实现；
- 哪些内容应该保留不动；
- V0.2 最小改动计划；
- 你准备新增/修改哪些文件。

确认方案后再开始改代码。优先保证已经跑通的链路不被破坏，不要过度设计。
```

---

## 16. 一句话项目定义

> **OTP Bridge 是一个本地优先的 iPhone → Windows 短信验证码桥接工具：iOS Shortcuts 在收到验证码短信时通过局域网把短信正文发送给 Windows，Windows 本地提取 OTP 并写入剪贴板，从而让用户无需解锁手机查看验证码。**
