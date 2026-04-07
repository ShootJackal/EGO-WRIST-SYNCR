#!/usr/bin/env python3
"""Compatibility entrypoint to preserve old workflow.

Usage:
    python match_3cams.py
    python match_3cams.py "E:\\NOT UPLOADED"
"""

from __future__ import annotations

import sys

from sync_pipeline import resolve_root, run_match


if __name__ == "__main__":
    root_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_match(resolve_root(root_arg))
