#!/usr/bin/env python3
"""Compatibility entrypoint to preserve old workflow:

    python match_3cams.py
"""

from sync_pipeline import resolve_root, run_match


if __name__ == "__main__":
    run_match(resolve_root())
