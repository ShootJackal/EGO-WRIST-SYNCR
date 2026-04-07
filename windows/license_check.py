"""Offline license-key validation.

Key format:  <payload-base64>.<signature-hex>
Payload JSON: {"user": "...", "exp": "YYYY-MM-DD"}

Keys are generated with generate_key.py (kept by the seller, not shipped).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
from datetime import date
from pathlib import Path

_SECRET = b"EGO-WRIST-SYNCR-2026-SECRET-CHANGE-ME"

LICENSE_FILE_NAME = "license.key"


def _find_license_file() -> Path | None:
    candidates = [
        Path.cwd() / LICENSE_FILE_NAME,
        Path(getattr(sys, "_MEIPASS", "")) / LICENSE_FILE_NAME,
        Path(__file__).resolve().parent / LICENSE_FILE_NAME,
    ]
    env = os.environ.get("TRICAM_LICENSE_FILE", "").strip()
    if env:
        candidates.insert(0, Path(env))
    for p in candidates:
        if p.is_file():
            return p
    return None


def _verify(key_text: str) -> tuple[bool, str]:
    key_text = key_text.strip()
    if "." not in key_text:
        return False, "Malformed key."

    payload_b64, sig_hex = key_text.rsplit(".", 1)
    try:
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
    except Exception:
        return False, "Malformed key."

    expected = hmac.new(_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig_hex):
        return False, "Invalid key."

    try:
        data = json.loads(payload_bytes)
    except Exception:
        return False, "Corrupt key payload."

    exp_str = data.get("exp", "")
    if exp_str:
        try:
            exp_date = date.fromisoformat(exp_str)
        except ValueError:
            return False, "Corrupt expiration."
        if date.today() > exp_date:
            return False, f"License expired on {exp_str}."

    return True, data.get("user", "licensed user")


def require_license() -> str:
    """Check for a valid license. Exits the process if invalid."""
    license_path = _find_license_file()
    if license_path is None:
        print("=" * 55)
        print("  LICENSE KEY REQUIRED")
        print("  Place your license.key file next to this program.")
        print("  Purchase at: https://github.com/ShootJackal")
        print("=" * 55)
        raise SystemExit(1)

    key_text = license_path.read_text(encoding="utf-8").strip()
    ok, info = _verify(key_text)
    if not ok:
        print("=" * 55)
        print(f"  LICENSE ERROR: {info}")
        print("  Contact: https://github.com/ShootJackal")
        print("=" * 55)
        raise SystemExit(1)

    return info
