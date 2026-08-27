from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

MAX_SOURCE_BYTES = 10 * 1024 * 1024


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and verify source archives required by distribution licenses."
    )
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "third_party_sources.lock.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    args.destination.mkdir(parents=True, exist_ok=True)

    for source in manifest["sources"]:
        filename = source["filename"]
        if Path(filename).name != filename:
            raise ValueError(f"Unsafe source filename: {filename!r}")
        with urlopen(source["url"], timeout=30) as response:
            data = response.read(MAX_SOURCE_BYTES + 1)
        if len(data) > MAX_SOURCE_BYTES:
            raise RuntimeError(f"Source archive exceeds 10 MiB limit: {filename}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != source["sha256"]:
            raise RuntimeError(f"SHA-256 mismatch for {filename}")
        (args.destination / filename).write_bytes(data)
        print(f"Verified {filename}: {digest}")

    (args.destination / manifest_path.name).write_bytes(manifest_path.read_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
