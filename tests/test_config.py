from dataclasses import replace
import json

import pytest

from otpigeon.config import (
    AppConfig,
    ConfigError,
    ConfigStore,
    SCHEMA_VERSION,
    default_config_path,
)
from otpigeon.i18n import DEFAULT_LANGUAGE


def test_load_or_create_persists_configuration(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")

    first = store.load_or_create()
    second = store.load_or_create()

    assert first == second
    assert first.schema_version == SCHEMA_VERSION
    assert first.install_id
    assert first.port == 8765
    assert first.language == DEFAULT_LANGUAGE


def test_regenerate_token_preserves_device_identity(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    before = store.load_or_create()

    after = store.regenerate_token()

    assert after.install_id == before.install_id
    assert after.port == before.port
    assert after.language == before.language
    assert after.token != before.token
    assert store.load_or_create() == after


def test_save_rejects_invalid_port(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    config = store.load_or_create()

    with pytest.raises(ConfigError):
        store.save(replace(config, port=70000))


def test_save_rejects_invalid_language(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    config = store.load_or_create()

    with pytest.raises(ConfigError):
        store.save(replace(config, language="invalid"))


def test_legacy_config_defaults_to_chinese(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "install_id": "a" * 32,
                "token": "x" * 20,
                "port": 8765,
            }
        ),
        encoding="utf-8",
    )

    assert ConfigStore(path).load_or_create().language == DEFAULT_LANGUAGE


def test_default_store_migrates_old_product_directory(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    old_path = tmp_path / "OTPigeon" / "config.json"
    old_path.parent.mkdir()
    old_path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "install_id": "a" * 32,
                "token": "x" * 20,
                "port": 8765,
                "language": DEFAULT_LANGUAGE,
            }
        ),
        encoding="utf-8",
    )

    migrated = ConfigStore().load_or_create()

    assert migrated.install_id == "a" * 32
    assert migrated.token == "x" * 20
    assert default_config_path() == tmp_path / "Pigeon" / "config.json"
    assert default_config_path().exists()
    assert old_path.exists()


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
