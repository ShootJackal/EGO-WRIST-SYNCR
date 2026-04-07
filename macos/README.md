# Tri-Cam Sync  --  macOS

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## SSD auto-detection

The scripts scan `/Volumes/` for any attached SSD containing a folder named
**`NOT UPLOADED`** with **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.

You can override auto-detection:
- Pass an explicit `--root` argument, **or**
- Set the `TRI_CAM_ROOT` environment variable
  (`export TRI_CAM_ROOT="/Volumes/MySSD/NOT UPLOADED"`).

## First-time setup

1. Put this folder anywhere (Desktop, Documents, etc.).
2. Double-click **`ONE_CLICK_SETUP.command`** (or run `bash setup_macos.sh`).
3. Wait for Homebrew, Python 3.12, FFmpeg and pip packages to install.
4. Drop your videos into the `HEAD`, `LEFT`, `RIGHT` folders on your SSD.

## Run matching

- Double-click **`RUN_MATCH.command`**, or
- `python3 match_3cams.py`, or
- `python3 sync_pipeline.py match`

This writes `matched_triplets.csv` inside your `NOT UPLOADED` folder.

## Package matched sets

- Double-click **`RUN_PACKAGE.command`**, or
- `python3 sync_pipeline.py package`

This copies matched files into `NOT UPLOADED/UPLOAD_READY/`.

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
