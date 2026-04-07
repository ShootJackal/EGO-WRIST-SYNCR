# Tri-Cam Sync  --  Windows

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## SSD auto-detection

The scripts scan every attached drive for a folder named **`NOT UPLOADED`**
containing **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.

You can override auto-detection:
- Pass an explicit `--root` argument, **or**
- Set the `TRI_CAM_ROOT` environment variable
  (`setx TRI_CAM_ROOT "E:\NOT UPLOADED"`).

## First-time setup

1. Put this folder anywhere (Desktop, Documents, etc.).
2. Double-click **`ONE_CLICK_SETUP.bat`**.
3. Wait for Python, FFmpeg and pip packages to install.
4. Drop your videos into the `HEAD`, `LEFT`, `RIGHT` folders on your SSD.

## Run matching

- Double-click **`RUN_MATCH.bat`**, or
- `python match_3cams.py`, or
- `python sync_pipeline.py match`

This writes `matched_triplets.csv` inside your `NOT UPLOADED` folder.

## Package matched sets

- Double-click **`RUN_PACKAGE.bat`**, or
- `python sync_pipeline.py package`

This copies matched files into `NOT UPLOADED\UPLOAD_READY\`.

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
