from otpigeon.network import (
    CandidateAddress,
    LocalEndpointPublisher,
    is_supported_private_ipv4,
)


class FakeRegistration:
    def __init__(self, *args) -> None:
        self.args = args
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_supported_addresses_are_limited_to_rfc1918() -> None:
    assert is_supported_private_ipv4("192.168.137.1")
    assert is_supported_private_ipv4("172.16.2.3")
    assert is_supported_private_ipv4("10.0.0.8")
    assert not is_supported_private_ipv4("127.0.0.1")
    assert not is_supported_private_ipv4("169.254.1.2")
    assert not is_supported_private_ipv4("198.18.0.1")
    assert not is_supported_private_ipv4("8.8.8.8")


def test_publisher_registers_each_interface_independently() -> None:
    candidates = (
        CandidateAddress("Wi-Fi", "192.168.0.10"),
        CandidateAddress("Hotspot", "192.168.137.1"),
    )
    registrations: list[FakeRegistration] = []

    def factory(*args):
        registration = FakeRegistration(*args)
        registrations.append(registration)
        return registration

    publisher = LocalEndpointPublisher(
        "a" * 32,
        8765,
        candidate_provider=lambda: candidates,
        registration_factory=factory,
    )

    snapshot = publisher.refresh()
    publisher.stop()

    assert snapshot.state == "running"
    assert set(snapshot.addresses) == set(candidates)
    assert len(registrations) == 2
    assert all(registration.closed for registration in registrations)


def test_publisher_degrades_without_private_address() -> None:
    publisher = LocalEndpointPublisher(
        "b" * 32,
        8765,
        candidate_provider=lambda: (),
        registration_factory=FakeRegistration,
    )

    snapshot = publisher.refresh()

    assert snapshot.state == "degraded"
    assert snapshot.addresses == ()
