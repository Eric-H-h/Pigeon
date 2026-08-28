from otpigeon.i18n import text, translate_event, translate_status


def test_chinese_ui_keeps_technical_terms_in_english() -> None:
    assert text("zh-CN", "app_name") == "Pigeon"
    assert text("zh-CN", "shortcut_url") == "快捷指令 URL"
    assert text("zh-CN", "pairing_token") == "配对 token"
    assert text("zh-CN", "available_ips") == "可用 IP 地址"


def test_english_app_name_is_pigeon() -> None:
    assert text("en", "app_name") == "Pigeon"


def test_status_is_localized() -> None:
    assert translate_status("zh-CN", "Running") == "运行中"
    assert translate_status("en", "Running") == "Running"


def test_timestamped_event_is_localized_without_changing_otp() -> None:
    event = "09:30:01  OTP copied: 1****6"

    assert translate_event("zh-CN", event) == "09:30:01  OTP 已复制：1****6"
    assert translate_event("en", event) == event
