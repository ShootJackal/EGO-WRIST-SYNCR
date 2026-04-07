# TriCamSync  --  Windows

**Multi-camera audio sync for photographers and videographers.**

Automatically matches clips across HEAD, LEFT and RIGHT cameras using
audio fingerprinting. Works with weddings, events, drone footage,
interviews -- any multi-cam shoot.

## What's in this folder

| File | What it does |
|------|-------------|
| `TriCamSync.exe` | The main program |
| `RUN_MATCH.bat` | Double-click to match clips across cameras |
| `RUN_PACKAGE.bat` | Double-click to copy matched sets into UPLOAD_READY |
| `INSTALL_FFMPEG.bat` | One-time FFmpeg install (required for audio processing) |
| `license.key` | Your license file (you provide this) |

## Getting started

1. Double-click **`INSTALL_FFMPEG.bat`** (first time only -- installs FFmpeg).
2. Place your `license.key` file in this folder.
3. Plug in your SSD with footage in `NOT UPLOADED\HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`RUN_MATCH.bat`** to find matching clips.
5. Double-click **`RUN_PACKAGE.bat`** to organize them for upload.

That's it. No command line, no configuration.

## SSD auto-detection

The program scans every attached drive for a folder named **`NOT UPLOADED`**
containing **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.

Override with `TRI_CAM_ROOT` environment variable if needed:
`setx TRI_CAM_ROOT "E:\NOT UPLOADED"`

## Expected folder layout

```
<SSD>\NOT UPLOADED\
  HEAD\   <- head-cam / main camera clips
  LEFT\   <- left camera clips
  RIGHT\  <- right camera clips
```

## Output

- `matched_triplets.csv` -- match results with confidence scores
- `UPLOAD_READY\` -- organized files ready for delivery

## License

Purchase at: https://github.com/ShootJackal
