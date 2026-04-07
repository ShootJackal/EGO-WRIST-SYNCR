# Tri-Cam Sync One-Click Setup

## Works with any SSD you plug in
The matcher auto-finds the first drive that contains all three folders:
- `\NOT UPLOADED\HEAD`
- `\NOT UPLOADED\LEFT`
- `\NOT UPLOADED\RIGHT`

Override priority:
1. CLI `--root "E:\NOT UPLOADED"`
2. Env var `TRI_CAM_ROOT=E:\NOT UPLOADED`
3. Auto-detect drives
4. Fallback `D:\NOT UPLOADED`

## Folder layout (exact)
- `X:\NOT UPLOADED\HEAD`
- `X:\NOT UPLOADED\LEFT`
- `X:\NOT UPLOADED\RIGHT`

(`X:` can be D:, E:, F:, etc.)

## First-time setup on a new Windows PC
1. Put this folder anywhere.
2. Double-click `ONE_CLICK_SETUP.bat`.
3. Wait for install to finish.
4. Drop videos into `HEAD`, `LEFT`, and `RIGHT` under your SSD root.

## Run matching (same as before)
- Old-compatible command:
  - `python match_3cams.py`
- Optional explicit root:
  - `python match_3cams.py "E:\NOT UPLOADED"`
- Or helper button:
  - Double-click `RUN_MATCH.bat`
- Or explicit CLI:
  - `python sync_pipeline.py match --root "E:\NOT UPLOADED"`

Output:
- `X:\NOT UPLOADED\matched_triplets.csv`

## Package matched sets
- Double-click `RUN_PACKAGE.bat`
  - Uses `%TRI_CAM_ROOT%` automatically if set.
- Or run:
  - `python sync_pipeline.py package --root "E:\NOT UPLOADED"`

Output folder:
- `X:\NOT UPLOADED\UPLOAD_READY\SET_001_HEAD.mov`
- `X:\NOT UPLOADED\UPLOAD_READY\SET_001_LEFT.mov`
- `X:\NOT UPLOADED\UPLOAD_READY\SET_001_RIGHT.mov`

## Requirements
- Python
- FFmpeg (`ffmpeg` and `ffprobe` available in PATH)
- NumPy
