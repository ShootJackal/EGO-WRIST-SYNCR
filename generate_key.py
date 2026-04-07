#!/usr/bin/env python3
"""Generate license keys for TriCamSync.

Usage:
    python generate_key.py "Customer Name" 2027-12-31
    python generate_key.py "Customer Name"              # no expiration

KEEP THIS FILE PRIVATE. Do NOT ship it to customers.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sys
from datetime import date

_SECRET = b"EGO-WRIST-SYNCR-2026-SECRET-CHANGE-ME"


def generate(user: str, exp: str | None = None) -> str:
    payload: dict = {"user": user}
    if exp:
        date.fromisoformat(exp)
        payload["exp"] = exp

    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode()
    sig = hmac.new(_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_key.py <user> [YYYY-MM-DD]")
        raise SystemExit(1)

    user = sys.argv[1]
    exp = sys.argv[2] if len(sys.argv) > 2 else None
    key = generate(user, exp)

    print(f"User : {user}")
    if exp:
        print(f"Expires: {exp}")
    else:
        print("Expires: never")
    print()
    print(key)
    print()
    print("Save this key to a file named 'license.key' for the customer.")
