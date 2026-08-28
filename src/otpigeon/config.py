from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import os
from pathlib import Path
import secrets
import tempfile
import uuid

from .i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


SCHEMA_VERSION = 1
DEFAULT_PORT = 8765


class ConfigError(RuntimeError):
    """Raised when an existing OTPigeon configuration is invalid."""


@dataclass(frozen=True, slots=True)
class AppConfig:
    schema_version: int
    install_id: str
    token: str
    port: int
    language: str


def default_config_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "OTPigeon" / "config.json"
    return Path.home() / "AppData" / "Local" / "OTPigeon" / "config.json"


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_config_path()

    def load_or_create(self) -> AppConfig:
        if not self.path.exists():
            config = self._new_config()
            self.save(config)
            return config

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ConfigError(
                f"Configuration is unreadable: {self.path}. "
                "Move or delete it, then restart OTPigeon."
            ) from exc

        return self._validate(data)

    def regenerate_token(self) -> AppConfig:
        config = self.load_or_create()
        updated = replace(config, token=secrets.token_urlsafe(16))
        self.save(updated)
        return updated

    def set_language(self, language: str) -> AppConfig:
        config = self.load_or_create()
        updated = replace(config, language=language)
        self.save(updated)
        return updated

    def save(self, config: AppConfig) -> None:
        self._validate(asdict(config))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(config), ensure_ascii=False, indent=2) + "\n"

        fd, raw_temp_path = tempfile.mkstemp(
            prefix="config-", suffix=".tmp", dir=self.path.parent
        )
        temp_path = Path(raw_temp_path)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, self.path)
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
        finally:
            temp_path.unlink(missing_ok=True)

    @staticmethod
    def _new_config() -> AppConfig:
        return AppConfig(
            schema_version=SCHEMA_VERSION,
            install_id=uuid.uuid4().hex,
            token=secrets.token_urlsafe(16),
            port=DEFAULT_PORT,
            language=DEFAULT_LANGUAGE,
        )

    @staticmethod
    def _validate(data: object) -> AppConfig:
        if not isinstance(data, dict):
            raise ConfigError("Configuration root must be a JSON object.")

        schema_version = data.get("schema_version")
        install_id = data.get("install_id")
        token = data.get("token")
        port = data.get("port")
        language = data.get("language", DEFAULT_LANGUAGE)

        if schema_version != SCHEMA_VERSION:
            raise ConfigError(f"Unsupported configuration schema: {schema_version!r}.")
        if (
            not isinstance(install_id, str)
            or len(install_id) != 32
            or any(char not in "0123456789abcdef" for char in install_id)
        ):
            raise ConfigError("Configuration install_id is invalid.")
        if not isinstance(token, str) or len(token) < 20:
            raise ConfigError("Configuration token is invalid.")
        if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
            raise ConfigError("Configuration port is invalid.")
        if language not in SUPPORTED_LANGUAGES:
            raise ConfigError("Configuration language is invalid.")

        return AppConfig(
            schema_version=schema_version,
            install_id=install_id,
            token=token,
            port=port,
            language=language,
        )
