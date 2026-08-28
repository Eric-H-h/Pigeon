from otpigeon.network import (
    CandidateAddress,
    LocalAddressMonitor,
    is_supported_private_ipv4,
)


def test_supported_addresses_are_limited_to_rfc1918() -> None:
    assert is_supported_private_ipv4("192.168.137.1")
    assert is_supported_private_ipv4("172.16.2.3")
    assert is_supported_private_ipv4("10.0.0.8")
    assert not is_supported_private_ipv4("127.0.0.1")
    assert not is_supported_private_ipv4("169.254.1.2")
    assert not is_supported_private_ipv4("198.18.0.1")
    assert not is_supported_private_ipv4("8.8.8.8")


def test_monitor_reports_each_private_interface() -> None:
    candidates = (
        CandidateAddress("Wi-Fi", "192.168.0.10"),
        CandidateAddress("Hotspot", "192.168.137.1"),
    )
    monitor = LocalAddressMonitor(candidate_provider=lambda: candidates)

    snapshot = monitor.refresh()

    assert snapshot.state == "running"
    assert set(snapshot.addresses) == set(candidates)


def test_monitor_degrades_without_private_address() -> None:
    monitor = LocalAddressMonitor(candidate_provider=lambda: ())

    snapshot = monitor.refresh()

    assert snapshot.state == "degraded"
    assert snapshot.addresses == ()


def test_monitor_reports_address_changes() -> None:
    current = [CandidateAddress("WLAN", "192.168.5.101")]
    changes = []
    monitor = LocalAddressMonitor(
        on_change=changes.append,
        candidate_provider=lambda: tuple(current),
    )

    first = monitor.refresh()
    current[0] = CandidateAddress("WLAN", "192.168.5.102")
    second = monitor.refresh()

    assert first.addresses[0].address == "192.168.5.101"
    assert second.addresses[0].address == "192.168.5.102"
    assert changes == [first, second]
