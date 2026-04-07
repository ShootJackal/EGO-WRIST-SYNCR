"""License validation for EGO-WRIST-SYNCR / Tri-Cam Sync.

Two tiers:
  COMMUNITY — free universal key anyone can use
  PRO       — unique per-customer keys from keygen.py
"""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

_SALT = b"EWS-TriCamSync-2025-HMAC"
COMMUNITY_KEY = "EWS-COMMUNITY-FREE-2025"
_LICENSE_FILE = ".tricamsync_license"


def _compute_sig(serial_hex: str) -> str:
    return hmac.new(
        _SALT, serial_hex.encode("ascii"), hashlib.sha256
    ).hexdigest()[:8].upper()


def validate_key(key: str) -> tuple[bool, str]:
    """Return (is_valid, tier).  tier is 'COMMUNITY', 'PRO', or ''."""
    key = key.strip().upper()

    if key == COMMUNITY_KEY:
        return True, "COMMUNITY"

    parts = key.replace(" ", "").split("-")
    if len(parts) == 5 and parts[0] == "EWS":
        serial = parts[1] + parts[2]
        sig_given = parts[3] + parts[4]
        if len(serial) == 8 and len(sig_given) == 8:
            if _compute_sig(serial) == sig_given:
                return True, "PRO"

    return False, ""


def _license_path(base_dir: Path | None = None) -> Path:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent
    return base_dir / _LICENSE_FILE


def load_stored_key(base_dir: Path | None = None) -> str | None:
    p = _license_path(base_dir)
    if p.exists():
        text = p.read_text(encoding="utf-8").strip()
        if text:
            return text
    return None


def store_key(key: str, base_dir: Path | None = None) -> None:
    _license_path(base_dir).write_text(key.strip() + "\n", encoding="utf-8")


def check_or_prompt(base_dir: Path | None = None) -> tuple[str, str]:
    """Load saved key or prompt the user.  Returns (key, tier)."""
    stored = load_stored_key(base_dir)
    if stored:
        valid, tier = validate_key(stored)
        if valid:
            return stored, tier

    print()
    print("  ──────────────────────────────────────────────────")
    print("              LICENSE KEY REQUIRED")
    print("  ──────────────────────────────────────────────────")
    print()
    print(f"    Community key (free):  {COMMUNITY_KEY}")
    print( "    Pro keys:  purchase at <your-store-url>")
    print()

    while True:
        try:
            raw = input("    Enter key: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(1)
        if not raw:
            continue
        valid, tier = validate_key(raw)
        if valid:
            store_key(raw, base_dir)
            print(f"    Activated: {tier} license")
            return raw, tier
        print("    Invalid key — try again.")
