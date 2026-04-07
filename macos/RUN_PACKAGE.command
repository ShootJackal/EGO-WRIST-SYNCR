#!/usr/bin/env bash
cd "$(dirname "$0")"

echo ""
echo "  TriCamSync - Package Matched Sets"
echo "  ==================================="
echo ""

ROOT_ARG=""
if [ -n "${TRI_CAM_ROOT:-}" ]; then
    ROOT_ARG="--root $TRI_CAM_ROOT"
fi

./TriCamSync package $ROOT_ARG

echo ""
read -rp "Press Enter to close..."
