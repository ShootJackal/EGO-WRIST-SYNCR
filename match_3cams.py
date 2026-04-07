#!/usr/bin/env python3
"""Compatibility entrypoint to preserve old workflow:

    python match_3cams.py
"""

from sync_pipeline import run_match
from pathlib import Path


if __name__ == "__main__":
    run_match(Path(r"D:\NOT UPLOADED"))
