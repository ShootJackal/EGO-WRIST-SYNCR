# Tri-Cam Sync  --  Windows

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## License key

On first run you will be asked for a license key.

- **Community (free):** `EWS-COMMUNITY-FREE-2025`
- **Pro:** purchase at <your-store-url>

The key is saved locally (`.tricamsync_license`) so you only enter it once.

## SSD auto-detection

The scripts scan every **external** (non-system) drive for a folder named
**`NOT UPLOADED`** containing **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.
The system drive (usually C:\) is skipped.

If no external drive with the expected layout is found, you will be prompted
to enter a **drive letter** (e.g. `E`) or a **full folder path**
(e.g. `E:\NOT UPLOADED`).

You can also override auto-detection:
- Pass an explicit `--root` argument, **or**
- Set the `TRI_CAM_ROOT` environment variable
  (`setx TRI_CAM_ROOT "E:\NOT UPLOADED"`).

## First-time setup

1. Put this folder anywhere (Desktop, Documents, etc.).
2. Double-click **`ONE_CLICK_SETUP.bat`**.
3. Wait for Python, FFmpeg and pip packages to install.
4. Drop your videos into the `HEAD`, `LEFT`, `RIGHT` folders on your SSD.

## Run (recommended)

- Double-click **`LAUNCH.bat`** for the interactive menu.

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

- **`RUN_MATCH.bat`** — runs audio scan only
- **`RUN_PACKAGE.bat`** — copies matched files (copy mode)
- `python match_3cams.py`
- `python sync_pipeline.py match`

## Expected folder layout

```
<SSD>\NOT UPLOADED\
  HEAD\   <- head-cam clips
  LEFT\   <- left-cam clips
  RIGHT\  <- right-cam clips
```

## Requirements

- Windows 10/11
- Python 3.10+
- FFmpeg (`ffmpeg` and `ffprobe` in PATH)
- NumPy (installed automatically by the setup script)
