# TriCamSync

**Multi-camera audio sync for photographers and videographers.**

Automatically matches clips across multiple cameras using audio
fingerprinting. Whether you're shooting weddings, events, drone footage,
interviews, or any multi-cam setup -- TriCamSync matches your HEAD, LEFT
and RIGHT camera clips by their audio tracks and packages them into
organized, upload-ready sets.

No more manually scrubbing through hours of footage to find matching clips.
Just drop your files in, double-click, and let the software do the work.

---

## Downloads

Go to [**Releases**](../../releases) and download the ZIP for your platform:

| Platform | Download |
|----------|----------|
| **Windows** | `TriCamSync-Windows.zip` |
| **macOS** | `TriCamSync-macOS.zip` |

## License

A valid license key is required. Place your `license.key` file in the same
folder as the program.

Contact [ShootJackal](https://github.com/ShootJackal) to purchase a license.

---

## How it works

1. **Install FFmpeg** (first time only) -- double-click `INSTALL_FFMPEG`
   in your downloaded folder.

2. **Plug in your SSD** with your camera footage organized into three folders:
   - `HEAD` -- head-cam / main camera
   - `LEFT` -- left wrist / secondary camera
   - `RIGHT` -- right wrist / third camera

3. **Double-click `RUN_MATCH`** -- the program scans all three folders,
   extracts audio fingerprints, and cross-correlates them to find matching
   clips across cameras. Results are saved to `matched_triplets.csv`.

4. **Double-click `RUN_PACKAGE`** -- copies matched files into an
   `UPLOAD_READY` folder with organized naming (`SET_001_HEAD.mov`, etc.).

## Perfect for

- **Wedding photographers** -- match ceremony and reception footage across
  multiple cameras instantly
- **Event videographers** -- sync multi-angle coverage without timecode
- **Drone + ground combos** -- match aerial footage to ground cameras by audio
- **Interview setups** -- align multi-cam interview recordings
- **Any multi-camera shoot** where cameras record the same audio environment

## SSD auto-detection

The program automatically scans attached drives for a folder named
`NOT UPLOADED` containing `HEAD`, `LEFT`, and `RIGHT` sub-folders.

- **Windows** -- scans every drive letter (D:\, E:\, F:\, ...)
- **macOS** -- scans `/Volumes/`

No configuration needed. Just plug in your SSD and run.
