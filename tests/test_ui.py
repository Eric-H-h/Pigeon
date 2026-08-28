from otpigeon import ui


def test_project_footer_metadata() -> None:
    assert ui.PROJECT_URL == "https://github.com/Eric-H-h/OTPigeon"
    assert ui.PROJECT_URL_DISPLAY == "github.com/Eric-H-h/OTPigeon"
    assert ui.AUTHOR_CREDIT == "@eric"


def test_project_link_opens_in_browser(monkeypatch) -> None:
    opened: list[tuple[str, int]] = []
    monkeypatch.setattr(
        ui.webbrowser,
        "open",
        lambda url, new: opened.append((url, new)),
    )

    window = object.__new__(ui.OTPigeonWindow)
    window._open_project_url(None)

    assert opened == [(ui.PROJECT_URL, 2)]
