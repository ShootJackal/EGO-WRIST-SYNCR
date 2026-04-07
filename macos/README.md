# TriCamSync  --  macOS

**Multi-camera audio sync for photographers and videographers.**

Automatically matches clips across HEAD, LEFT and RIGHT cameras using
audio fingerprinting. Works with weddings, events, drone footage,
interviews -- any multi-cam shoot.

## What's in this folder

| File | What it does |
|------|-------------|
| `TriCamSync` | The main program |
| `RUN_MATCH.command` | Double-click to match clips across cameras |
| `RUN_PACKAGE.command` | Double-click to copy matched sets into UPLOAD_READY |
| `INSTALL_FFMPEG.command` | One-time FFmpeg install (required for audio processing) |
| `license.key` | Your license file (you provide this) |

## Getting started

1. Double-click **`INSTALL_FFMPEG.command`** (first time only -- installs FFmpeg).
2. Place your `license.key` file in this folder.
3. Plug in your SSD with footage in `NOT UPLOADED/HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`RUN_MATCH.command`** to find matching clips.
5. Double-click **`RUN_PACKAGE.command`** to organize them for upload.

That's it. No command line, no configuration.

## SSD auto-detection

The program scans `/Volumes/` for any attached SSD containing a folder named
**`NOT UPLOADED`** with **`HEAD`**, **`LEFT`**, and **`RIGHT`** sub-folders.

Override with `TRI_CAM_ROOT` environment variable if needed:
`export TRI_CAM_ROOT="/Volumes/MySSD/NOT UPLOADED"`

## Expected folder layout

```
/Volumes/<SSD>/NOT UPLOADED/
  HEAD/   <- head-cam / main camera clips
  LEFT/   <- left camera clips
  RIGHT/  <- right camera clips
```

## Output

- `matched_triplets.csv` -- match results with confidence scores
- `UPLOAD_READY/` -- organized files ready for delivery

## License

Purchase at: https://github.com/ShootJackal
