from __future__ import annotations


DEFAULT_LANGUAGE = "zh-CN"
SUPPORTED_LANGUAGES = ("zh-CN", "en")
LANGUAGE_NAMES = {"zh-CN": "中文", "en": "English"}


_TEXT = {
    "zh-CN": {
        "app_name": "信鸽",
        "status": "状态",
        "shortcut_url": "快捷指令 URL",
        "pairing_token": "配对 token",
        "available_ips": "可用 IP 地址",
        "last_event": "最近事件",
        "copy": "复制",
        "show": "显示",
        "hide": "隐藏",
        "setup_help": "设置帮助",
        "regenerate_token": "重新生成 token",
        "exit": "退出",
        "no_private_ip": "未检测到私有 IPv4 地址，请连接可信路由器或启用 Windows 移动热点。",
        "network_error": "网络：{error}",
        "status_stopped": "已停止",
        "status_running": "运行中",
        "status_degraded": "网络不可用",
        "clipboard_error": "剪贴板错误",
        "regenerate_title": "重新生成配对 token？",
        "regenerate_message": "现有 iPhone Shortcut 将停止工作，直到你更新其中的 token。",
        "regenerate_error": "无法重新生成 token",
        "language_error": "无法保存 Language",
        "setup_title": "信鸽设置",
        "setup_message": (
            "1. 将 Windows Wi-Fi 网络配置文件设为 Private（专用网络）。\n"
            "2. 只允许信鸽通过 Private 网络的 Windows 防火墙。\n"
            "3. 将 iPhone 连接到同一台可信路由器或 Windows 移动热点。\n"
            "4. 把窗口中的快捷指令 URL 和配对 token 填入 Shortcut。\n"
            "5. 先手动运行 Shortcut，再创建短信个人自动化。"
        ),
    },
    "en": {
        "app_name": "Pigeon",
        "status": "Status",
        "shortcut_url": "Shortcut URL",
        "pairing_token": "Pairing token",
        "available_ips": "Available IP addresses",
        "last_event": "Last event",
        "copy": "Copy",
        "show": "Show",
        "hide": "Hide",
        "setup_help": "Setup help",
        "regenerate_token": "Regenerate token",
        "exit": "Exit",
        "no_private_ip": "No private IPv4 address detected. Connect to a trusted router or enable Windows Mobile Hotspot.",
        "network_error": "Network: {error}",
        "status_stopped": "Stopped",
        "status_running": "Running",
        "status_degraded": "Degraded",
        "clipboard_error": "Clipboard error",
        "regenerate_title": "Regenerate pairing token?",
        "regenerate_message": "The existing iPhone Shortcut will stop working until you update its token.",
        "regenerate_error": "Could not regenerate token",
        "language_error": "Could not save Language",
        "setup_title": "Pigeon setup",
        "setup_message": (
            "1. Set the Windows Wi-Fi network profile to Private.\n"
            "2. Allow Pigeon through Windows Firewall on Private networks only.\n"
            "3. Connect the iPhone to the same trusted router or Windows hotspot.\n"
            "4. Enter the Shortcut URL and pairing token shown here.\n"
            "5. Run the Shortcut once, then create a Message Personal Automation."
        ),
    },
}


_ZH_EVENT_EXACT = {
    "Ready to start": "准备启动",
    "Local IP address updated": "本地 IP 地址已更新",
    "No private IPv4 address; enable Windows Mobile Hotspot": "未检测到私有 IPv4 地址，请连接可信路由器或启用 Windows 移动热点",
    "Pairing token regenerated; update the iPhone Shortcut": "配对 token 已重新生成，请更新 iPhone Shortcut",
    "Server stopped": "服务已停止",
    "Request rejected: public client": "请求已拒绝：客户端不是私有网络地址",
    "Request rejected: invalid token": "请求已拒绝：token 无效",
    "iPhone connection check succeeded": "iPhone 连接检查成功",
    "Message received; OTP not found": "已收到短信，但未找到 OTP",
}

_ZH_EVENT_PREFIXES = {
    "Listening on port ": "正在监听端口 ",
    "Local address unavailable: ": "本地地址不可用：",
    "OTP copied: ": "OTP 已复制：",
    "Request failed: ": "请求失败：",
}


def text(language: str, key: str, **values: object) -> str:
    return _TEXT[language][key].format(**values)


def translate_status(language: str, status: str) -> str:
    key = {
        "Stopped": "status_stopped",
        "Running": "status_running",
        "Degraded": "status_degraded",
    }.get(status)
    return text(language, key) if key else status


def translate_event(language: str, event: str) -> str:
    if language != "zh-CN":
        return event

    timestamp, separator, message = event.partition("  ")
    localized = _ZH_EVENT_EXACT.get(message)
    if localized is None:
        localized = message
        for prefix, replacement in _ZH_EVENT_PREFIXES.items():
            if message.startswith(prefix):
                localized = replacement + message[len(prefix) :]
                break
    return f"{timestamp}{separator}{localized}" if separator else localized
