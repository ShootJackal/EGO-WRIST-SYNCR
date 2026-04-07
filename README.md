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
4. Double-click **`LAUNCH.bat`** — follow the interactive menu.

### macOS
1. Download and unzip **TriCamSync-macOS.zip**.
2. Double-click **`ONE_CLICK_SETUP.command`** to install Homebrew, Python, FFmpeg and dependencies.
3. Plug in your SSD containing `NOT UPLOADED/HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`LAUNCH.command`** — follow the interactive menu.

## License key

On first launch you will be prompted for a license key.

| Tier | Key | Features |
|------|-----|----------|
| **Community (free)** | `EWS-COMMUNITY-FREE-2025` | Full scan + match + package |
| **Pro** | Unique per-customer key | Same features, supports the project |

The key is saved locally so you only enter it once.

## Unified launcher

The new **LAUNCH** script gives you a single interactive menu:

1. **Full scan + match + package** — scans all cameras, writes `matched_triplets.csv`, then packages files.
2. **Package only** (when CSV already exists) — skip scanning, go straight to packaging.
3. **Re-scan / scan only** — regenerate the CSV without packaging.
0. **Exit**

### Packaging modes

When packaging, you choose one of three modes:

| Mode | What it does |
|------|-------------|
| **Copy** | Duplicates matched files into `UPLOAD_READY` on the same SSD |
| **Move / reorganize** | Moves files into `UPLOAD_READY` (saves disk space, originals are relocated) |
| **Transfer** | Copies files + CSV to a different SSD/drive |

## SSD auto-detection

Both versions scan **external** drives/volumes for a folder named **`NOT UPLOADED`**
containing **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.
Internal/system drives (C:\ on Windows, Macintosh HD on macOS) are skipped.

- **Windows**: scans every non-system drive letter (E:\, F:\, G:\, ...)
- **macOS**: scans external volumes under `/Volumes/`

If no matching external drive is found, you will be prompted to enter a
**drive letter** (Windows) or **volume name** (macOS), or a full folder path.

Override auto-detection entirely with `--root` or the `TRI_CAM_ROOT` environment variable.

## Repository layout

```
keygen.py             <- Pro license key generator (repo owner only)

windows/              <- Windows release files
  LAUNCH.bat             <- Unified launcher (recommended)
  ONE_CLICK_SETUP.bat
  RUN_MATCH.bat          <- Legacy — still works
  RUN_PACKAGE.bat        <- Legacy — still works
  setup_windows.ps1
  sync_pipeline.py
  match_3cams.py
  licensing.py
  requirements.txt
  README.md

macos/                <- macOS release files
  LAUNCH.command         <- Unified launcher (recommended)
  ONE_CLICK_SETUP.command
  RUN_MATCH.command      <- Legacy — still works
  RUN_PACKAGE.command    <- Legacy — still works
  setup_macos.sh
  sync_pipeline.py
  match_3cams.py
  licensing.py
  requirements.txt
  README.md
```
