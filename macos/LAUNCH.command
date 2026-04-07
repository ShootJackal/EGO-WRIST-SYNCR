#!/usr/bin/env bash
cd "$(dirname "$0")"
python3 sync_pipeline.py launch ${TRI_CAM_ROOT:+--root "$TRI_CAM_ROOT"}
echo ""
read -rp "Press Enter to close..."
