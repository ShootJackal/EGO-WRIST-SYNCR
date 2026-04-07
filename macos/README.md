# Tri-Cam Sync  --  macOS

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## License key

On first run you will be asked for a license key.

- **Community (free):** `EWS-COMMUNITY-FREE-2025`
- **Pro:** purchase at <your-store-url>

The key is saved locally (`.tricamsync_license`) so you only enter it once.

## SSD auto-detection

The scripts scan **external** volumes under `/Volumes/` for any attached SSD
containing a folder named **`NOT UPLOADED`** with **`HEAD`**, **`LEFT`**, and
**`RIGHT`** sub-folders. Internal volumes (Macintosh HD) are skipped.

If no external volume with the expected layout is found, you will be prompted
to enter a **volume name** (e.g. `MySSD`) or a **full folder path**
(e.g. `/Volumes/MySSD/NOT UPLOADED`).

You can also override auto-detection:
- Pass an explicit `--root` argument, **or**
- Set the `TRI_CAM_ROOT` environment variable
  (`export TRI_CAM_ROOT="/Volumes/MySSD/NOT UPLOADED"`).

## First-time setup

1. Put this folder anywhere (Desktop, Documents, etc.).
2. Double-click **`ONE_CLICK_SETUP.command`** (or run `bash setup_macos.sh`).
3. Wait for Homebrew, Python 3.12, FFmpeg and pip packages to install.
4. Drop your videos into the `HEAD`, `LEFT`, `RIGHT` folders on your SSD.

## Run (recommended)

- Double-click **`LAUNCH.command`** for the interactive menu.

The launcher lets you:
- **Full scan + match + package** — does everything in one go
- **Package only** — if you already have a `matched_triplets.csv`
- **Re-scan only** — regenerate the CSV

### Packaging modes

| Mode | What it does |
|------|-------------|
| **Copy** | Duplicates matched files into `UPLOAD_READY` on the same SSD |
| **Move / reorganize** | Moves files into `UPLOAD_READY` (saves disk space) |
| **Transfer** | Copies files + CSV to a different SSD/drive |

## Legacy scripts

These still work for backwards compatibility:

- **`RUN_MATCH.command`** — runs audio scan only
- **`RUN_PACKAGE.command`** — copies matched files (copy mode)
- `python3 match_3cams.py`
- `python3 sync_pipeline.py match`

## Expected folder layout

```
/Volumes/<SSD>/NOT UPLOADED/
  HEAD/   <- head-cam clips
  LEFT/   <- left-cam clips
  RIGHT/  <- right-cam clips
```

## Requirements

- macOS 12+
- Python 3.10+
- FFmpeg (`ffmpeg` and `ffprobe` in PATH)
- NumPy (installed automatically by the setup script)
