#!/usr/bin/env python3
"""EGO-WRIST-SYNCR Pro license-key generator.

Usage:
    python keygen.py                     # generate 1 key
    python keygen.py -n 10               # generate 10 keys
    python keygen.py -n 50 -o keys.txt   # generate 50, save to file

Keys are formatted as:
    EWS-XXXX-XXXX-YYYY-YYYY
where XXXX-XXXX is a random serial and YYYY-YYYY is an HMAC signature.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import secrets
import sys

_SALT = b"EWS-TriCamSync-2025-HMAC"


def _compute_sig(serial_hex: str) -> str:
    return hmac.new(
        _SALT, serial_hex.encode("ascii"), hashlib.sha256
    ).hexdigest()[:8].upper()


def generate_key() -> str:
    serial = secrets.token_hex(4).upper()
    sig = _compute_sig(serial)
    return f"EWS-{serial[:4]}-{serial[4:]}-{sig[:4]}-{sig[4:]}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate EGO-WRIST-SYNCR Pro license keys")
    parser.add_argument("-n", "--count", type=int, default=1, help="Number of keys to generate")
    parser.add_argument("-o", "--output", default=None, help="Write keys to this file (default: stdout)")
    args = parser.parse_args()

    keys = [generate_key() for _ in range(args.count)]

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(keys) + "\n")
        print(f"Wrote {len(keys)} key(s) to {args.output}")
    else:
        for k in keys:
            print(k)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
