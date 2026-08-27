from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import threading
from typing import Callable, Protocol


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
    alias: str
    addresses: tuple[CandidateAddress, ...]
    state: str
    error: str | None = None


class Registration(Protocol):
    def close(self) -> None: ...


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


class _ZeroconfRegistration:
    def __init__(
        self,
        candidate: CandidateAddress,
        hostname_fqdn: str,
        install_id: str,
        port: int,
    ) -> None:
        from zeroconf import IPVersion, ServiceInfo, Zeroconf

        self._zeroconf = Zeroconf(
            interfaces=[candidate.address], ip_version=IPVersion.V4Only
        )
        self._info = ServiceInfo(
            "_otpigeon._tcp.local.",
            f"OTPigeon {install_id[:8]}._otpigeon._tcp.local.",
            parsed_addresses=[candidate.address],
            port=port,
            properties={"path": "/otp", "version": "0.2"},
            server=hostname_fqdn,
        )
        try:
            self._zeroconf.register_service(self._info)
        except Exception:
            self._zeroconf.close()
            raise

    def close(self) -> None:
        try:
            self._zeroconf.unregister_service(self._info)
        finally:
            self._zeroconf.close()


class LocalEndpointPublisher:
    """Publish one stable hostname independently on each private IPv4 link."""

    def __init__(
        self,
        install_id: str,
        port: int,
        on_change: Callable[[NetworkSnapshot], None] | None = None,
        poll_interval: float = 5.0,
        candidate_provider: Callable[[], tuple[CandidateAddress, ...]] = (
            enumerate_candidate_addresses
        ),
        registration_factory: Callable[
            [CandidateAddress, str, str, int], Registration
        ] = _ZeroconfRegistration,
    ) -> None:
        self.alias = f"otpigeon-{install_id[:8]}.local"
        self._hostname_fqdn = self.alias + "."
        self._install_id = install_id
        self._port = port
        self._on_change = on_change
        self._poll_interval = poll_interval
        self._candidate_provider = candidate_provider
        self._registration_factory = registration_factory
        self._registrations: dict[CandidateAddress, Registration] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._snapshot = NetworkSnapshot(self.alias, (), "stopped")

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

        desired = set(candidates)
        errors: list[str] = []

        with self._lock:
            for candidate in set(self._registrations) - desired:
                registration = self._registrations.pop(candidate)
                try:
                    registration.close()
                except Exception as exc:
                    errors.append(type(exc).__name__)

            for candidate in desired - set(self._registrations):
                try:
                    self._registrations[candidate] = self._registration_factory(
                        candidate,
                        self._hostname_fqdn,
                        self._install_id,
                        self._port,
                    )
                except Exception as exc:
                    errors.append(f"{candidate.interface_name}: {type(exc).__name__}")

            if self._registrations:
                state = "running" if not errors else "degraded"
            else:
                state = "degraded"
            error = "; ".join(errors) if errors else None
            snapshot = NetworkSnapshot(self.alias, candidates, state, error)
            changed = snapshot != self._snapshot
            self._snapshot = snapshot

        if changed and self._on_change:
            self._on_change(snapshot)
        return snapshot
    def stop(self) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread and thread is not threading.current_thread():
            thread.join(timeout=max(1.0, self._poll_interval + 1.0))

        with self._lock:
            registrations = list(self._registrations.values())
            self._registrations.clear()
        for registration in registrations:
            try:
                registration.close()
            except Exception:
                pass
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
        snapshot = NetworkSnapshot(self.alias, addresses, state, error)
        with self._lock:
            changed = snapshot != self._snapshot
            self._snapshot = snapshot
        if changed and self._on_change:
            self._on_change(snapshot)
        return snapshot
