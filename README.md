# EGO-WRIST-SYNCR  --  Tri-Cam Sync

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## Downloads

Go to [**Releases**](../../releases) and download the ZIP for your platform:

| Platform | Download | What's inside |
|----------|----------|---------------|
| **Windows** | `TriCamSync-Windows.zip` | `.bat` launchers, PowerShell setup, Python scripts |
| **macOS** | `TriCamSync-macOS.zip` | `.command` launchers, Bash/Homebrew setup, Python scripts |

Each ZIP is self-contained -- just unzip and double-click the setup script.

## Quick start

### Windows
1. Download and unzip **TriCamSync-Windows.zip**.
2. Double-click **`ONE_CLICK_SETUP.bat`** to install Python, FFmpeg and dependencies.
3. Plug in your SSD containing `NOT UPLOADED\HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`RUN_MATCH.bat`** to match clips.
5. Double-click **`RUN_PACKAGE.bat`** to copy matched sets into `UPLOAD_READY`.

### macOS
1. Download and unzip **TriCamSync-macOS.zip**.
2. Double-click **`ONE_CLICK_SETUP.command`** to install Homebrew, Python, FFmpeg and dependencies.
3. Plug in your SSD containing `NOT UPLOADED/HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`RUN_MATCH.command`** to match clips.
5. Double-click **`RUN_PACKAGE.command`** to copy matched sets into `UPLOAD_READY`.

## SSD auto-detection

Both versions scan attached drives/volumes for a folder named **`NOT UPLOADED`**
containing **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.

- **Windows**: scans every drive letter (D:\, E:\, F:\, ...)
- **macOS**: scans `/Volumes/`

Override with `--root` or the `TRI_CAM_ROOT` environment variable.

## Repository layout

```
windows/          <- Windows release files
  ONE_CLICK_SETUP.bat
  RUN_MATCH.bat
  RUN_PACKAGE.bat
  setup_windows.ps1
  sync_pipeline.py
  match_3cams.py
  requirements.txt
  README.md

macos/            <- macOS release files
  ONE_CLICK_SETUP.command
  RUN_MATCH.command
  RUN_PACKAGE.command
  setup_macos.sh
  sync_pipeline.py
  match_3cams.py
  requirements.txt
  README.md
```
