#!/usr/bin/env python3
"""Compatibility entrypoint to preserve old workflow.

Usage:
    python match_3cams.py
    python match_3cams.py "E:\\NOT UPLOADED"
    python match_3cams.py "/Volumes/MySSD/NOT UPLOADED"
"""

from __future__ import annotations

import argparse

from sync_pipeline import resolve_root, run_match


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Back-compatible 3-cam matcher entrypoint")
    parser.add_argument("root", nargs="?", default=None, help="Optional root path, e.g. E:\\NOT UPLOADED")
    parser.add_argument("--root", dest="root_flag", default=None, help="Optional root path override")
    args = parser.parse_args()

    chosen_root = args.root_flag if args.root_flag else args.root
    run_match(resolve_root(chosen_root))
