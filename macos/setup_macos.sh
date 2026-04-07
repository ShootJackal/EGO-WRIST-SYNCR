#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-}"

step() { printf '\n\033[36m=== %s ===\033[0m\n' "$1"; }

resolve_root() {
    if [ -n "$PROJECT_ROOT" ]; then
        echo "$PROJECT_ROOT"
        return
    fi

    if [ -n "${TRI_CAM_ROOT:-}" ]; then
        echo "$TRI_CAM_ROOT"
        return
    fi

    for vol in /Volumes/*/; do
        candidate="${vol}NOT UPLOADED"
        if [ -d "$candidate/HEAD" ] && [ -d "$candidate/LEFT" ] && [ -d "$candidate/RIGHT" ]; then
            echo "$candidate"
            return
        fi
    done

    for vol in /Volumes/*/; do
        candidate="${vol}NOT UPLOADED"
        if [ -d "$candidate" ]; then
            echo "$candidate"
            return
        fi
    done

    echo "$HOME/NOT UPLOADED"
}

step "Checking for Homebrew"
if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
fi

step "Installing Python"
brew install python@3.12 || brew upgrade python@3.12 || true

step "Installing FFmpeg"
brew install ffmpeg || brew upgrade ffmpeg || true

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "Python not found after install. Restart your terminal and run this script again."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

step "Installing Python packages"
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r "$SCRIPT_DIR/requirements.txt"

RESOLVED_ROOT="$(resolve_root)"

step "Creating folder layout"
mkdir -p "$RESOLVED_ROOT/HEAD"
mkdir -p "$RESOLVED_ROOT/LEFT"
mkdir -p "$RESOLVED_ROOT/RIGHT"

step "Setup complete"
echo "Using project root:"
echo "  $RESOLVED_ROOT"
echo ""
echo "Put files in:"
echo "  $RESOLVED_ROOT/HEAD"
echo "  $RESOLVED_ROOT/LEFT"
echo "  $RESOLVED_ROOT/RIGHT"
echo ""
echo "Tip: export TRI_CAM_ROOT=\"/Volumes/MySSD/NOT UPLOADED\" to pin a specific SSD."
