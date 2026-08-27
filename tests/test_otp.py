import pytest

from otpigeon.otp import extract_otp


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("【服务】验证码 123456，5 分钟内有效", "123456"),
        ("Your verification code is 654321.", "654321"),
        ("Use 246810 as your one-time code.", "246810"),
        ("您的验证码是 123-456", "123456"),
        ("验证码：１２３４５６", "123456"),
        ("订单号 123456，验证码 654321", "654321"),
        ("仅有一个数字 7788", "7788"),
        ("订单 123456，金额 7788", None),
        ("验证码 123", None),
        ("验证码 123456789", None),
        ("Use A1B2C3 as your code", None),
        ("没有数字", None),
        ("", None),
    ],
)
def test_extract_otp(message: str, expected: str | None) -> None:
    assert extract_otp(message) == expected
