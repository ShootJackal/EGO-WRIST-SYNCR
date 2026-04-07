#!/usr/bin/env python3
"""Compatibility entrypoint for macOS.

Usage:
    python3 match_3cams.py
    python3 match_3cams.py "/Volumes/MySSD/NOT UPLOADED"
"""

from __future__ import annotations

import argparse

from licensing import check_or_prompt
from sync_pipeline import resolve_root, run_match


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Back-compatible 3-cam matcher (macOS)")
    parser.add_argument("root", nargs="?", default=None, help="Optional root path, e.g. /Volumes/MySSD/NOT UPLOADED")
    parser.add_argument("--root", dest="root_flag", default=None, help="Optional root path override")
    args = parser.parse_args()

    check_or_prompt()
    chosen_root = args.root_flag if args.root_flag else args.root
    run_match(resolve_root(chosen_root))
