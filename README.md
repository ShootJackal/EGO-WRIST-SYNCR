# EGO-WRIST-SYNCR  --  Tri-Cam Sync

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## Releasing (for repo owner)

1. Merge all changes into `main`.
2. Tag and push: `git tag v2.1.0 && git push origin v2.1.0`
3. GitHub Actions will automatically:
   - Compile `TriCamSync.exe` (Windows) and `TriCamSync` (macOS) via PyInstaller
   - Bundle them with launcher scripts and READMEs (no `.py` source files)
   - Create a GitHub Release with `TriCamSync-Windows.zip` and `TriCamSync-macOS.zip`
4. Share the release download links with customers.

**What's in the release ZIPs (no source code):**
- `TriCamSync.exe` / `TriCamSync` — compiled executable
- `LAUNCH.bat` / `LAUNCH.command` — double-click launcher
- `ONE_CLICK_SETUP.bat` / `ONE_CLICK_SETUP.command` — installs FFmpeg
- `RUN_MATCH.bat` / `RUN_MATCH.command` — legacy shortcut
- `RUN_PACKAGE.bat` / `RUN_PACKAGE.command` — legacy shortcut
- `README.md` — consumer docs
- `setup_windows.ps1` / `setup_macos.sh` — setup scripts
- `requirements.txt` — for reference

**What stays private (never in ZIPs):**
- `keygen.py` — Pro license key generator
- All `.py` source files — compiled into the executable
- `.github/` — CI workflows
- `.git/` — repo history

## Generating Pro license keys

```bash
python keygen.py              # 1 key to stdout
python keygen.py -n 50        # 50 keys to stdout
python keygen.py -n 100 -o keys.txt   # 100 keys to file
```

Community key (free, give to anyone): `EWS-COMMUNITY-FREE-2025`

## Quick start (for customers)

### Windows
1. Download `TriCamSync-Windows.zip` from Releases.
2. Unzip, double-click **`ONE_CLICK_SETUP.bat`**.
3. Plug in SSD with `NOT UPLOADED\HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`LAUNCH.bat`**.

### macOS
1. Download `TriCamSync-macOS.zip` from Releases.
2. Unzip, double-click **`ONE_CLICK_SETUP.command`**.
3. Plug in SSD with `NOT UPLOADED/HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`LAUNCH.command`**.

## Features

- **Unified launcher** with interactive menu
- **Audio fingerprint matching** with multi-sample consensus and 3-way cross-validation
- **Human-readable output** (`matched_sets.txt`) with copy-paste file paths
- **3 packaging modes**: copy, move/reorganize, transfer to different SSD
- **Disk space checking** before copy/transfer
- **Crash/disconnect recovery** with automatic resume
- **License key system** with free community tier and sellable Pro keys
- **External-only drive scanning** (skips system drives)

## Repository layout

```
keygen.py                <- Pro key generator (PRIVATE — never shipped)
.github/workflows/       <- CI: compiles and releases

windows/                 <- Windows source (compiled for release)
  sync_pipeline.py
  licensing.py
  match_3cams.py
  LAUNCH.bat
  ONE_CLICK_SETUP.bat
  RUN_MATCH.bat
  RUN_PACKAGE.bat
  setup_windows.ps1
  requirements.txt
  README.md

macos/                   <- macOS source (compiled for release)
  sync_pipeline.py
  licensing.py
  match_3cams.py
  LAUNCH.command
  ONE_CLICK_SETUP.command
  RUN_MATCH.command
  RUN_PACKAGE.command
  setup_macos.sh
  requirements.txt
  README.md
```
