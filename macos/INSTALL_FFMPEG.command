#!/usr/bin/env bash
cd "$(dirname "$0")"

echo ""
echo "  TriCamSync - FFmpeg Installer"
echo "  =============================="
echo "  This installs FFmpeg which is required for audio processing."
echo "  You only need to run this once."
echo ""

if command -v ffmpeg &>/dev/null; then
    echo "FFmpeg is already installed. You're good to go!"
    echo ""
    read -rp "Press Enter to close..."
    exit 0
fi

if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
fi

echo "Installing FFmpeg..."
brew install ffmpeg

echo ""
echo "Done! FFmpeg is now installed."
echo ""
read -rp "Press Enter to close..."
