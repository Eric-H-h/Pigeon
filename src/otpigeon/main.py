from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
import threading

from .clipboard import copy_sensitive
from .config import AppConfig, ConfigError, ConfigStore
from .network import LocalEndpointPublisher, NetworkSnapshot
from .server import BridgeEvent, BridgeServer


@dataclass(frozen=True, slots=True)
class AppSnapshot:
    status: str
    address: str
    numeric_addresses: tuple[str, ...]
    token: str
    last_event: str
    network_error: str | None


class AppController:
    """Own the application lifecycle and expose one small interface to the GUI."""

    def __init__(self, config_store: ConfigStore | None = None) -> None:
        self._config_store = config_store or ConfigStore()
        self._config = self._config_store.load_or_create()
        self._lock = threading.Lock()
        self._last_event = "Ready to start"
        self._network_snapshot = NetworkSnapshot(
            self._config.hostname, (), "stopped"
        )
        self._server = BridgeServer(
            "0.0.0.0",
            self._config.port,
            token_provider=self.get_token,
            clipboard_writer=copy_sensitive,
            event_sink=self._on_bridge_event,
        )
        self._publisher = LocalEndpointPublisher(
            self._config.install_id,
            self._config.port,
            on_change=self._on_network_change,
        )

    def start(self) -> None:
        self._server.start()
        self._publisher.start()

    def stop(self) -> None:
        self._publisher.stop()
        self._server.stop()

    def snapshot(self) -> AppSnapshot:
        with self._lock:
            config = self._config
            network = self._network_snapshot
            last_event = self._last_event

        if not self._server.running:
            status = "Stopped"
        elif network.state == "running":
            status = "Running"
        else:
            status = "Degraded"

        numeric_addresses = tuple(
            f"{candidate.interface_name}: http://{candidate.address}:{config.port}"
            for candidate in network.addresses
        )
        return AppSnapshot(
            status=status,
            address=config.base_url,
            numeric_addresses=numeric_addresses,
            token=config.token,
            last_event=last_event,
            network_error=network.error,
        )

    def get_token(self) -> str:
        with self._lock:
            return self._config.token

    def copy_token(self) -> None:
        copy_sensitive(self.get_token())

    def regenerate_token(self) -> AppConfig:
        updated = self._config_store.regenerate_token()
        with self._lock:
            self._config = updated
            self._last_event = self._timestamp(
                "Pairing token regenerated; update the iPhone Shortcut"
            )
        return updated

    def _on_bridge_event(self, event: BridgeEvent) -> None:
        with self._lock:
            self._last_event = self._timestamp(event.message)

    def _on_network_change(self, snapshot: NetworkSnapshot) -> None:
        with self._lock:
            self._network_snapshot = snapshot
            if snapshot.state == "running":
                self._last_event = self._timestamp("Local address published")
            elif snapshot.error:
                self._last_event = self._timestamp(
                    f"Local address unavailable: {snapshot.error}"
                )
            else:
                self._last_event = self._timestamp(
                    "No private IPv4 address; enable Windows Mobile Hotspot"
                )

    @staticmethod
    def _timestamp(message: str) -> str:
        return f"{datetime.now():%H:%M:%S}  {message}"


def main() -> int:
    if os.name != "nt":
        raise SystemExit("OTPigeon V0.2 supports Windows only.")

    from tkinter import messagebox

    from .ui import run_ui

    try:
        controller = AppController()
        controller.start()
    except ConfigError as exc:
        messagebox.showerror("OTPigeon configuration error", str(exc))
        return 2
    except OSError as exc:
        messagebox.showerror(
            "OTPigeon could not start",
            f"The local server could not start. Port 8765 may already be in use.\n\n{exc}",
        )
        return 3

    try:
        run_ui(controller)
    finally:
        controller.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
