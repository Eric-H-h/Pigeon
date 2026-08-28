from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import threading
from typing import Callable


_PRIVATE_NETWORKS = tuple(
    ipaddress.ip_network(network)
    for network in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)


@dataclass(frozen=True, slots=True, order=True)
class CandidateAddress:
    interface_name: str
    address: str


@dataclass(frozen=True, slots=True)
class NetworkSnapshot:
    addresses: tuple[CandidateAddress, ...]
    state: str
    error: str | None = None


def is_supported_private_ipv4(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    return isinstance(ip, ipaddress.IPv4Address) and any(
        ip in network for network in _PRIVATE_NETWORKS
    )


def enumerate_candidate_addresses() -> tuple[CandidateAddress, ...]:
    import ifaddr

    candidates: set[CandidateAddress] = set()
    for adapter in ifaddr.get_adapters():
        interface_name = adapter.nice_name or adapter.name
        for adapter_ip in adapter.ips:
            address = adapter_ip.ip
            if isinstance(address, str) and is_supported_private_ipv4(address):
                candidates.add(CandidateAddress(interface_name, address))
    return tuple(sorted(candidates))


class LocalAddressMonitor:
    """Track current RFC1918 IPv4 addresses without relying on name discovery."""

    def __init__(
        self,
        on_change: Callable[[NetworkSnapshot], None] | None = None,
        poll_interval: float = 5.0,
        candidate_provider: Callable[[], tuple[CandidateAddress, ...]] = (
            enumerate_candidate_addresses
        ),
    ) -> None:
        self._on_change = on_change
        self._poll_interval = poll_interval
        self._candidate_provider = candidate_provider
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._snapshot = NetworkSnapshot((), "stopped")

    @property
    def snapshot(self) -> NetworkSnapshot:
        with self._lock:
            return self._snapshot

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self.refresh()
        self._thread = threading.Thread(
            target=self._run, name="otpigeon-mdns", daemon=True
        )
        self._thread.start()

    def refresh(self) -> NetworkSnapshot:
        try:
            candidates = tuple(sorted(set(self._candidate_provider())))
        except Exception as exc:
            return self._set_snapshot((), "degraded", type(exc).__name__)
        state = "running" if candidates else "degraded"
        return self._set_snapshot(candidates, state, None)

    def stop(self) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread and thread is not threading.current_thread():
            thread.join(timeout=max(1.0, self._poll_interval + 1.0))
        self._set_snapshot((), "stopped", None)

    def _run(self) -> None:
        while not self._stop_event.wait(self._poll_interval):
            self.refresh()

    def _set_snapshot(
        self,
        addresses: tuple[CandidateAddress, ...],
        state: str,
        error: str | None,
    ) -> NetworkSnapshot:
        snapshot = NetworkSnapshot(addresses, state, error)
        with self._lock:
            changed = snapshot != self._snapshot
            self._snapshot = snapshot
        if changed and self._on_change:
            self._on_change(snapshot)
        return snapshot
