# Tri-Cam Sync  --  Windows

Automatically matches HEAD, LEFT and RIGHT camera clips by audio
fingerprinting and packages them into upload-ready sets.

## License key

On first run you will be asked for a license key.

- **Community (free):** `EWS-COMMUNITY-FREE-2025`
- **Pro:** purchase at <your-store-url>

The key is saved locally so you only enter it once.

## First-time setup

1. Unzip this folder anywhere (Desktop, Documents, etc.).
2. Double-click **`ONE_CLICK_SETUP.bat`** to install FFmpeg.
3. Plug in your SSD with videos in `NOT UPLOADED\HEAD`, `LEFT`, `RIGHT`.
4. Double-click **`LAUNCH.bat`**.

## Usage

Double-click **`LAUNCH.bat`** — the interactive menu will guide you:

1. **Full scan + match + package** — does everything in one go
2. **Package only** — if you already have a `matched_sets.txt`
3. **Re-scan only** — regenerate the match file
4. **Resume packaging** — continue an interrupted copy/transfer
0. **Exit**

### Packaging modes

| Mode | What it does |
|------|-------------|
| **Copy** | Duplicates matched files into `UPLOAD_READY` on the same SSD |
| **Move / reorganize** | Moves files into `UPLOAD_READY` (saves disk space) |
| **Transfer** | Copies files + match file to a different SSD/drive |

Disk space is checked before copy/transfer.  If interrupted (SSD
unplugged, power loss), just re-run and choose **Resume packaging**.

## SSD auto-detection

Scans every **external** (non-system) drive for a folder named
**`NOT UPLOADED`** containing **`HEAD`**, **`LEFT`**, and **`RIGHT`**.
The system drive (usually C:\) is skipped.

If nothing is found, you'll be prompted for a drive letter or path.

Override with `TRI_CAM_ROOT` environment variable:
`setx TRI_CAM_ROOT "E:\NOT UPLOADED"`

## Output

Results are written to `matched_sets.txt` — a plain text file with full
file paths you can copy-paste directly into File Explorer.

## Expected folder layout

```
<SSD>\NOT UPLOADED\
  HEAD\   <- head-cam clips
  LEFT\   <- left-cam clips
  RIGHT\  <- right-cam clips
```

## Requirements

- Windows 10/11
- FFmpeg (`ffmpeg` and `ffprobe` in PATH)
  (installed automatically by the setup script)
