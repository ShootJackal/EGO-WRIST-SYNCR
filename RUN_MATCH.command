#!/usr/bin/env bash
cd "$(dirname "$0")"
python3 match_3cams.py ${TRI_CAM_ROOT:+"$TRI_CAM_ROOT"}
echo ""
read -rp "Press Enter to close..."
