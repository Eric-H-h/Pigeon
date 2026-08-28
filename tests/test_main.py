from otpigeon.config import ConfigStore
from otpigeon.main import AppController
from otpigeon.network import CandidateAddress, NetworkSnapshot


def test_controller_rotates_only_token(tmp_path) -> None:
    controller = AppController(ConfigStore(tmp_path / "config.json"))
    before = controller.snapshot()

    controller.regenerate_token()
    after = controller.snapshot()

    assert after.address == before.address
    assert after.token != before.token
    assert after.status == "Stopped"


def test_controller_displays_current_numeric_address(tmp_path) -> None:
    controller = AppController(ConfigStore(tmp_path / "config.json"))

    controller._on_network_change(  # noqa: SLF001 - focused controller state test
        NetworkSnapshot((CandidateAddress("WLAN", "192.168.5.101"),), "running")
    )

    snapshot = controller.snapshot()
    assert snapshot.address == "http://192.168.5.101:8765"
    assert snapshot.numeric_addresses == (
        "WLAN: http://192.168.5.101:8765",
    )
