# Tri-Cam Sync One-Click Setup

## Folder layout (exact)
- `D:\NOT UPLOADED\HEAD`
- `D:\NOT UPLOADED\LEFT`
- `D:\NOT UPLOADED\RIGHT`

## First-time setup on a new Windows PC
1. Put this folder anywhere (for example Desktop).
2. Double-click `ONE_CLICK_SETUP.bat`.
3. Wait for install to finish.
4. Drop your videos into `HEAD`, `LEFT`, `RIGHT`.

## Run matching (same as before)
- Old-compatible command:
  - `python match_3cams.py`
- Or via helper button:
  - Double-click `RUN_MATCH.bat`
- Or explicit CLI:
  - `python sync_pipeline.py match --root "D:\NOT UPLOADED"`

This writes:
- `D:\NOT UPLOADED\matched_triplets.csv`

## Package matched sets
- Double-click `RUN_PACKAGE.bat`
- Or run:
  - `python sync_pipeline.py package --root "D:\NOT UPLOADED"`

This writes files like:
- `D:\NOT UPLOADED\UPLOAD_READY\SET_001_HEAD.mov`
- `D:\NOT UPLOADED\UPLOAD_READY\SET_001_LEFT.mov`
- `D:\NOT UPLOADED\UPLOAD_READY\SET_001_RIGHT.mov`

## Requirements
- Python
- FFmpeg (`ffmpeg` and `ffprobe` commands available in PATH)
- NumPy
