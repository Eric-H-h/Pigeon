from otpigeon.config import ConfigStore
from otpigeon.main import AppController


def test_controller_uses_stable_address_and_rotates_only_token(tmp_path) -> None:
    controller = AppController(ConfigStore(tmp_path / "config.json"))
    before = controller.snapshot()

    controller.regenerate_token()
    after = controller.snapshot()

    assert after.address == before.address
    assert after.token != before.token
    assert after.status == "Stopped"
