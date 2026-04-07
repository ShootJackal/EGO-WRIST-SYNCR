# Tri-Cam Sync One-Click Setup

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## SSD auto-detection

The scripts scan every attached SSD for a folder named **`NOT UPLOADED`**
containing **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.

| Platform | Scan locations |
|----------|---------------|
| Windows  | Every drive letter (`D:\`, `E:\`, `F:\`, ...) |
| macOS    | `/Volumes/<name>/NOT UPLOADED/...` |

You can override the auto-detection at any time:
- Pass an explicit `--root` argument, **or**
- Set the `TRI_CAM_ROOT` environment variable.

---

## Windows setup

1. Put this folder anywhere (Desktop, Documents, etc.).
2. Double-click **`ONE_CLICK_SETUP.bat`**.
3. Wait for Python, FFmpeg and pip packages to install.
4. Drop your videos into the `HEAD`, `LEFT`, `RIGHT` folders on your SSD.

### Run matching (Windows)
- Double-click **`RUN_MATCH.bat`**, or
- `python match_3cams.py`, or
- `python sync_pipeline.py match`

### Package matched sets (Windows)
- Double-click **`RUN_PACKAGE.bat`**, or
- `python sync_pipeline.py package`

---

## macOS setup

1. Put this folder anywhere.
2. Double-click **`ONE_CLICK_SETUP.command`** (or run `bash setup_macos.sh`).
3. Wait for Homebrew, Python 3.12, FFmpeg and pip packages to install.
4. Drop your videos into the `HEAD`, `LEFT`, `RIGHT` folders on your SSD.

### Run matching (macOS)
- Double-click **`RUN_MATCH.command`**, or
- `python3 match_3cams.py`, or
- `python3 sync_pipeline.py match`

### Package matched sets (macOS)
- Double-click **`RUN_PACKAGE.command`**, or
- `python3 sync_pipeline.py package`

---

## Expected folder layout

```
<SSD>/NOT UPLOADED/
  HEAD/   ← head-cam clips
  LEFT/   ← left-cam clips
  RIGHT/  ← right-cam clips
```

## Output

**`matched_triplets.csv`** is written inside the `NOT UPLOADED` folder.

Packaging copies files into:
```
NOT UPLOADED/UPLOAD_READY/
  SET_001_HEAD.mov
  SET_001_LEFT.mov
  SET_001_RIGHT.mov
  ...
```

## Requirements

- Python 3.10+
- FFmpeg (`ffmpeg` and `ffprobe` in PATH)
- NumPy (installed automatically by the setup scripts)
