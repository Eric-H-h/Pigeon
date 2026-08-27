from __future__ import annotations

import argparse
import json
from pathlib import Path

from otpigeon.config import default_config_path
from otpigeon.network import enumerate_candidate_addresses


SERVICE_TYPE = "_otpigeon._tcp.local."


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query a running OTPigeon instance over raw mDNS without printing its token."
    )
    parser.add_argument("--config", type=Path, default=default_config_path())
    args = parser.parse_args()

    try:
        data = json.loads(args.config.read_text(encoding="utf-8"))
        install_id = data["install_id"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Could not read OTPigeon install ID: {type(exc).__name__}")
        return 2

    if not isinstance(install_id, str) or len(install_id) < 8:
        print("OTPigeon install ID is invalid")
        return 2

    candidates = enumerate_candidate_addresses()
    if not candidates:
        print("No RFC1918 IPv4 interface found")
        return 3

    from zeroconf import IPVersion, Zeroconf

    service_name = f"OTPigeon {install_id[:8]}.{SERVICE_TYPE}"
    expected = {candidate.address for candidate in candidates}
    discovered: set[str] = set()

    print(f"Alias: otpigeon-{install_id[:8]}.local")
    for candidate in candidates:
        zeroconf = Zeroconf(
            interfaces=[candidate.address], ip_version=IPVersion.V4Only
        )
        try:
            info = zeroconf.get_service_info(
                SERVICE_TYPE, service_name, timeout=3000
            )
        finally:
            zeroconf.close()

        addresses = info.parsed_addresses() if info else []
        discovered.update(addresses)
        print(f"{candidate.interface_name}: {candidate.address} -> {addresses or 'not found'}")

    if discovered & expected:
        print("mDNS record matches a current private interface")
        return 0
    print("mDNS record was not found on a current private interface")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
