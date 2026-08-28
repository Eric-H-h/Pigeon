from otpigeon.config import ConfigStore
from otpigeon.main import AppController
from otpigeon.network import CandidateAddress, NetworkSnapshot


def test_controller_rotates_only_token(tmp_path) -> None:
    controller = AppController(ConfigStore(tmp_path / "config.json"))
    before = controller.snapshot()

    controller.regenerate_token()
    after = controller.snapshot()

    assert after.shortcut_url == before.shortcut_url
    assert after.token != before.token
    assert after.status == "Stopped"


def test_controller_displays_complete_shortcut_url(tmp_path) -> None:
    controller = AppController(ConfigStore(tmp_path / "config.json"))

    controller._on_network_change(  # noqa: SLF001 - focused controller state test
        NetworkSnapshot((CandidateAddress("WLAN", "192.168.5.101"),), "running")
    )

    snapshot = controller.snapshot()
    assert snapshot.shortcut_url == "http://192.168.5.101:8765/otp"
    assert snapshot.numeric_addresses == (
        "WLAN: http://192.168.5.101:8765",
    )


def test_controller_persists_language(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    controller = AppController(store)

    controller.set_language("en")

    assert controller.snapshot().language == "en"
    assert AppController(store).snapshot().language == "en"
