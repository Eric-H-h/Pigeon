from dataclasses import replace
import json

import pytest

from otpigeon.config import AppConfig, ConfigError, ConfigStore, SCHEMA_VERSION


def test_load_or_create_persists_configuration(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")

    first = store.load_or_create()
    second = store.load_or_create()

    assert first == second
    assert first.schema_version == SCHEMA_VERSION
    assert first.hostname.startswith("otpigeon-")
    assert first.base_url.endswith(":8765")


def test_regenerate_token_preserves_device_identity(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    before = store.load_or_create()

    after = store.regenerate_token()

    assert after.install_id == before.install_id
    assert after.port == before.port
    assert after.token != before.token
    assert store.load_or_create() == after


def test_save_rejects_invalid_port(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    config = store.load_or_create()

    with pytest.raises(ConfigError):
        store.save(replace(config, port=70000))


def test_invalid_json_fails_with_actionable_error(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ConfigError, match="Move or delete"):
        ConfigStore(path).load_or_create()


def test_invalid_schema_is_rejected(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 999,
                "install_id": "a" * 32,
                "token": "x" * 20,
                "port": 8765,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Unsupported"):
        ConfigStore(path).load_or_create()
