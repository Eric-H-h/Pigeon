from __future__ import annotations

import re
import unicodedata


_KEYWORD = (
    r"(?:验证码|校验码|动态码|短信码|OTP|verification\s*code|"
    r"one[\s-]*time\s*(?:password|code)|passcode|code)"
)

_SPLIT_PATTERNS = (
    re.compile(
        _KEYWORD
        + r"[^0-9]{0,20}(?<![0-9])([0-9]{3})[-\s]([0-9]{3})(?![0-9])",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?<![0-9])([0-9]{3})[-\s]([0-9]{3})(?![0-9])[^0-9]{0,20}"
        + _KEYWORD,
        re.IGNORECASE,
    ),
)

_PATTERNS = (
    re.compile(
        _KEYWORD + r"[^0-9]{0,20}(?<![0-9])([0-9]{4,8})(?![0-9])",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?<![0-9])([0-9]{4,8})(?![0-9])[^0-9]{0,20}" + _KEYWORD,
        re.IGNORECASE,
    ),
)


def extract_otp(text: str) -> str | None:
    """Return one unambiguous 4-8 digit OTP, otherwise ``None``."""
    if not isinstance(text, str) or not text:
        return None

    normalized = unicodedata.normalize("NFKC", text)

    for pattern in _SPLIT_PATTERNS:
        match = pattern.search(normalized)
        if match:
            return match.group(1) + match.group(2)

    for pattern in _PATTERNS:
        match = pattern.search(normalized)
        if match:
            return match.group(1)

    candidates = re.findall(r"(?<![0-9])[0-9]{4,8}(?![0-9])", normalized)
    if len(candidates) == 1:
        return candidates[0]
    return None
