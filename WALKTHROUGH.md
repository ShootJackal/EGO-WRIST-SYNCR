# EGO-WRIST-SYNCR — Complete Walkthrough

This document shows every screen and step of the tool from install to
finished output. An engineer can follow this to verify the tool works
end-to-end.

To see these screens live, run: `python demo.py`

---

## Table of Contents

1. [Installation](#1-installation)
2. [First Launch — License Key](#2-first-launch--license-key)
3. [SSD Detection](#3-ssd-detection)
4. [Main Menu](#4-main-menu)
5. [Step 1: Scanning Camera Folders](#5-step-1-scanning-camera-folders)
6. [Step 2: Audio Fingerprint Matching](#6-step-2-audio-fingerprint-matching)
7. [Step 3: Building Triplets (Cross-Validated)](#7-step-3-building-triplets-cross-validated)
8. [Match Results Summary](#8-match-results-summary)
9. [Output File: matched_sets.txt](#9-output-file-matched_setstxt)
10. [Packaging — Mode Selection](#10-packaging--mode-selection)
11. [Packaging — Copy Mode](#11-packaging--copy-mode)
12. [Packaging — Transfer to Different Drive](#12-packaging--transfer-to-different-drive)
13. [Disk Space Warning](#13-disk-space-warning)
14. [Crash / Disconnect Recovery](#14-crash--disconnect-recovery)
15. [Resume Packaging](#15-resume-packaging)
16. [Returning User — Menu with Existing Data](#16-returning-user--menu-with-existing-data)
17. [Architecture Overview](#17-architecture-overview)

---

## 1. Installation

### Windows

User double-clicks `ONE_CLICK_SETUP.bat`:

```
==================================================
TRI-CAM SYNC ONE-CLICK SETUP  (Windows)
==================================================
This installs Python, FFmpeg, Python packages,
and creates NOT UPLOADED\HEAD LEFT RIGHT on your SSD.

=== Checking winget ===
=== Installing Python ===
=== Installing FFmpeg ===
=== Installing Python packages ===
=== Creating folder layout ===
=== Setup complete ===
Using project root:
  E:\NOT UPLOADED
Put files in:
  E:\NOT UPLOADED\HEAD
  E:\NOT UPLOADED\LEFT
  E:\NOT UPLOADED\RIGHT
```

### macOS

User double-clicks `ONE_CLICK_SETUP.command`:

```
=== Checking for Homebrew ===
=== Installing Python ===
=== Installing FFmpeg ===
=== Installing Python packages ===
=== Creating folder layout ===
=== Setup complete ===
Using project root:
  /Volumes/MySSD/NOT UPLOADED
Put files in:
  /Volumes/MySSD/NOT UPLOADED/HEAD
  /Volumes/MySSD/NOT UPLOADED/LEFT
  /Volumes/MySSD/NOT UPLOADED/RIGHT
```

---

## 2. First Launch — License Key

On first launch, the user sees the banner and is prompted for a key.
The free community key is displayed right there:

```
  ╔═══════════════════════════════════════════════════════╗
  ║                                                       ║
  ║   EGO-WRIST-SYNCR  v2.1.0                            ║
  ║   Tri-Cam Audio Sync & Packaging                     ║
  ║                                                       ║
  ╚═══════════════════════════════════════════════════════╝

  ──────────────────────────────────────────────────
              LICENSE KEY REQUIRED
  ──────────────────────────────────────────────────

    Community key (free):  EWS-COMMUNITY-FREE-2025
    Pro keys:  purchase at <your-store-url>

    Enter key: EWS-COMMUNITY-FREE-2025
    Activated: COMMUNITY license
```

The key is saved to `.tricamsync_license` — never asked again.

---

## 3. SSD Detection

### Auto-detection (multiple drives found)

```
    Found 2 drives with 'NOT UPLOADED':
      1) E:\NOT UPLOADED
      2) F:\NOT UPLOADED

    Pick [1-2]: 1

    Source SSD: E:\NOT UPLOADED
```

### Manual entry (no drives found)

```
  ┌─────────────────────────────────────────────────┐
  │  No external drive with NOT UPLOADED found.     │
  │  Enter a drive letter or full folder path.      │
  └─────────────────────────────────────────────────┘

    Examples:  E
               E:\NOT UPLOADED
               F:\MyProject\NOT UPLOADED

    Drive letter or path: E
    ✓ Found HEAD/LEFT/RIGHT in: E:\NOT UPLOADED

    Source SSD: E:\NOT UPLOADED
```

---

## 4. Main Menu

### First run (no match file yet)

```
  ┌─────────────────────────────────────────────────┐
  │  What would you like to do?                     │
  │                                                 │
  │  1) Full scan + match + package                 │
  │     Scans HEAD/LEFT/RIGHT, matches audio,       │
  │     then packages files                         │
  │                                                 │
  │  2) Scan only (generate match file first)       │
  │     Run the audio scan without packaging        │
  │                                                 │
  │  0) Exit                                        │
  └─────────────────────────────────────────────────┘

    Choose [0/1/2]: 1
```

### Returning (match file + interrupted job detected)

```
  ┌─────────────────────────────────────────────────┐
  │  What would you like to do?                     │
  │                                                 │
  │  1) Full scan + match + package                 │
  │  2) Package only (match file exists)            │
  │  3) Re-scan only (regenerate match file)        │
  │                                                 │
  │  4) Resume packaging                            │
  │     Continue a previous copy/transfer that      │
  │     was interrupted                             │
  │                                                 │
  │  0) Exit                                        │
  └─────────────────────────────────────────────────┘

    Choose [0/1/2/3/4]: 4
```

---

## 5. Step 1: Scanning Camera Folders

Each folder is scanned with a live progress bar showing file count
and elapsed time:

```
  ── STEP 1/3 : Scanning camera folders ─────────────────

  ⠹ Scanning HEAD  [████████████████░░░░░░░░░░░░░░] 53.3%  10/18  4s
```

When done:

```
  ✓ Scanning HEAD  — 18 files found (8s)
  ✓ Scanning LEFT  — 22 files found (10s)
  ✓ Scanning RIGHT — 20 files found (9s)

    Total: 60 files  (42.8 GB)
```

---

## 6. Step 2: Audio Fingerprint Matching

Pairs are compared with audio correlation. Progress shows pair count:

```
  ── STEP 2/3 : Audio fingerprint matching ──────────────

  ⠼ HEAD → LEFT  [██████████████████░░░░░░░░░░░░░] 62.1%  246/396  1m 12s
```

When done:

```
  ✓ HEAD → LEFT  — 16 candidates (2m 5s)
  ✓ HEAD → RIGHT — 15 candidates (1m 58s)
```

---

## 7. Step 3: Building Triplets (Cross-Validated)

The tool assembles HEAD+LEFT+RIGHT sets and validates that all three
pairs agree. Sets where LEFT-RIGHT don't match are rejected:

```
  ── STEP 3/3 : Building triplets (cross-validated) ─────

  ✓ Assembled 15 matched triplet(s)
    Rejected 2 triplet(s): LEFT-RIGHT cross-validation failed
```

---

## 8. Match Results Summary

```
  ┌─────────────────────────────────────────────────┐
  │  ✓  Matched sets : 15                           │
  │     HIGH: 12   MEDIUM: 2   LOW: 1   REVIEW: 0  │
  │     Written to  : matched_sets.txt              │
  └─────────────────────────────────────────────────┘
```

---

## 9. Output File: matched_sets.txt

The output is a plain text file with **full absolute paths** that can be
copy-pasted directly into File Explorer (Windows) or Finder (macOS):

```
EGO-WRIST-SYNCR  Matched Sets
Generated: 2026-04-07 15:30:00
Source:    E:\NOT UPLOADED
Total:     15 set(s)
======================================================================

--- SET_001  [HIGH] ---

  HEAD:   E:\NOT UPLOADED\HEAD\GX010042.MP4
  LEFT:   E:\NOT UPLOADED\LEFT\GX080091.MP4
  RIGHT:  E:\NOT UPLOADED\RIGHT\GX050033.MP4

  Duration  HEAD 245.30s  LEFT 245.10s  RIGHT 245.50s
  Size      HEAD 1820.5 MB  LEFT 1795.2 MB  RIGHT 1810.8 MB
  Audio     H-L 0.7823  H-R 0.7541  L-R 0.6912
  Score     0.7425  (min consensus hits: 3)

--- SET_002  [HIGH] ---

  HEAD:   E:\NOT UPLOADED\HEAD\GX010043.MP4
  LEFT:   E:\NOT UPLOADED\LEFT\GX080092.MP4
  RIGHT:  E:\NOT UPLOADED\RIGHT\GX050034.MP4

  Duration  HEAD 312.80s  LEFT 312.60s  RIGHT 313.10s
  Size      HEAD 2340.1 MB  LEFT 2318.7 MB  RIGHT 2329.4 MB
  Audio     H-L 0.8201  H-R 0.7892  L-R 0.7345
  Score     0.7813  (min consensus hits: 4)

--- SET_003  [MEDIUM] ---

  HEAD:   E:\NOT UPLOADED\HEAD\GX010044.MP4
  LEFT:   E:\NOT UPLOADED\LEFT\GX080093.MP4
  RIGHT:  E:\NOT UPLOADED\RIGHT\GX050035.MP4

  Duration  HEAD 198.40s  LEFT 199.10s  RIGHT 198.80s
  Size      HEAD 1480.2 MB  LEFT 1465.9 MB  RIGHT 1472.1 MB
  Audio     H-L 0.4512  H-R 0.4103  L-R 0.3211
  Score     0.4275  (min consensus hits: 2)

======================================================================
Copy any path above and paste into File Explorer to navigate there.
```

---

## 10. Packaging — Mode Selection

```
  ┌─────────────────────────────────────────────────┐
  │  How would you like to package the files?       │
  │                                                 │
  │  1) Copy (duplicate on same SSD)                │
  │     Keeps originals, creates UPLOAD_READY copy  │
  │                                                 │
  │  2) Move / reorganize (same SSD)                │
  │     Moves files into UPLOAD_READY (no copy)     │
  │     Saves disk space — originals are relocated  │
  │                                                 │
  │  3) Transfer to a different drive               │
  │     Copies files + match file to another SSD    │
  │     and creates the folder structure there      │
  └─────────────────────────────────────────────────┘

    Choose [1/2/3]:
```

---

## 11. Packaging — Copy Mode

```
    Choose [1/2/3]: 1

  ⠸ Copying files [████████████████░░░░░░░░░░░░░░] 53.3%  24/45  1820.5 MB

  ✓ Copying complete — 45 files (42.8 GB, 3m 42s)

  ┌─────────────────────────────────────────────────┐
  │  ✓  45 files packaged                           │
  │     Output: E:\NOT UPLOADED\UPLOAD_READY        │
  └─────────────────────────────────────────────────┘
```

---

## 12. Packaging — Transfer to Different Drive

```
    Choose [1/2/3]: 3

    Where should UPLOAD_READY be created?
    Enter a drive letter or full folder path.

    Examples:  F
               G:\Projects\UPLOAD_READY

    Destination drive or path: F
    ✓ Will use: F:\UPLOAD_READY

  ⠼ Transferring files [████████████░░░░░░░░░░░░░░░] 40.0%  18/45  2340.1 MB

  ✓ Transferring complete — 45 files (42.8 GB, 5m 15s)
    Match file copied to: F:\UPLOAD_READY\matched_sets.txt

  ┌─────────────────────────────────────────────────┐
  │  ✓  45 files packaged                           │
  │     Output: F:\UPLOAD_READY                     │
  └─────────────────────────────────────────────────┘
```

---

## 13. Disk Space Warning

If the destination doesn't have enough space:

```
  ┌─────────────────────────────────────────────────┐
  │  ⚠  NOT ENOUGH DISK SPACE                      │
  │     Need:      42.8 GB                          │
  │     Available:  12.3 GB                         │
  │                                                 │
  │  Options:                                       │
  │   - Free up space and re-run                    │
  │   - Use mode 2 (move) to avoid doubling         │
  │   - Use mode 3 (transfer) to a bigger drive     │
  └─────────────────────────────────────────────────┘

    Continue anyway? (y/n):
```

---

## 14. Crash / Disconnect Recovery

If the SSD disconnects or the process crashes mid-copy:

```
  ⠴ Transferring files [██████████░░░░░░░░░░░░░░░░░] 48.9%  22/45

    ⚠  Error on file: clip015_HEAD.mp4
       [Errno 5] Input/output error: 'F:\UPLOAD_READY\SET_008_HEAD.mp4'

    The drive may have been disconnected or run out of space.
    Progress saved — 22 of 45 files done.
    Re-run packaging to resume from where it stopped.
```

---

## 15. Resume Packaging

On re-launch after a crash, the menu shows a **Resume** option:

```
  │  4) Resume packaging                            │
  │     Continue a previous copy/transfer that      │
  │     was interrupted                             │

    Choose [0/1/2/3/4]: 4

  ✓ Transferring complete — 45 files (42.8 GB, 2m 10s)
    (22 files already done from previous run)

  ┌─────────────────────────────────────────────────┐
  │  ✓  45 files packaged                           │
  │     Output: F:\UPLOAD_READY                     │
  └─────────────────────────────────────────────────┘
```

---

## 16. Returning User — Menu with Existing Data

When a user returns and a match file already exists:

```
  ┌─────────────────────────────────────────────────┐
  │  What would you like to do?                     │
  │                                                 │
  │  1) Full scan + match + package                 │
  │  2) Package only (match file exists)            │
  │  3) Re-scan only (regenerate match file)        │
  │  0) Exit                                        │
  └─────────────────────────────────────────────────┘
```

Option 2 skips the entire scan (which can take a long time) and goes
straight to packaging using the existing match file.

---

## 17. Architecture Overview

### Data flow

```
SSD plugged in
    │
    ▼
┌──────────────────────┐
│  Auto-detect drives  │  Scans external drives only (skips C:\ / Macintosh HD)
│  Find NOT UPLOADED   │  Prompts if not found
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  License check       │  Community key: EWS-COMMUNITY-FREE-2025
│                      │  Pro key: EWS-XXXX-XXXX-YYYY-YYYY (HMAC-signed)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Scan HEAD/LEFT/     │  ffprobe each file for duration + size
│  RIGHT folders       │  Progress bar per folder
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Audio fingerprint   │  Extract 20s PCM samples at up to 4 points
│  matching            │  Cross-correlate amplitude envelopes
│                      │  Greedy 1:1 assignment by score
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Cross-validation    │  HEAD-LEFT must match ✓
│  (3-way gate)        │  HEAD-RIGHT must match ✓
│                      │  LEFT-RIGHT must match ✓  ← NEW: enforced
│                      │  Consensus: 2+ sample points must agree
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Write results       │  matched_sets.txt with full absolute paths
│                      │  Copy-paste ready for File Explorer / Finder
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Package files       │  Mode 1: Copy to UPLOAD_READY (same SSD)
│                      │  Mode 2: Move/reorganize (same SSD, saves space)
│                      │  Mode 3: Transfer to different SSD
│                      │
│  Safety:             │  Disk space check before start
│                      │  Per-file checkpoint for crash recovery
│                      │  Resume from where it stopped
└──────────────────────┘
```

### Matching thresholds

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `MIN_AUDIO_SCORE` | 0.28 | Minimum audio correlation to consider a pair |
| `MIN_CONSENSUS_HITS` | 2 | How many sample points must agree |
| `MIN_LR_AUDIO_SCORE` | 0.20 | LEFT-RIGHT cross-validation threshold |
| `DURATION_TOL_SEC` | 75 | Max duration difference between clips |
| `MAX_SIZE_RATIO` | 1.8 | Max file size ratio between clips |
| `SAMPLE_SECONDS` | 20 | Length of each audio sample |
| `MAX_SHIFT_SEC` | 25 | Maximum allowed time offset between clips |

### Confidence levels

| Level | Requirements |
|-------|-------------|
| **HIGH** | avg_total >= 0.60, avg_audio >= 0.50, consensus hits >= 2 |
| **MEDIUM** | avg_total >= 0.42, avg_audio >= 0.32, consensus hits >= 2 |
| **LOW** | avg_total >= 0.28, avg_audio >= 0.28 |
| **REVIEW** | Below LOW thresholds — manual check recommended |

### Score composition

```
total_score = (audio_correlation × 0.75) + (duration_similarity × 0.15) + (size_similarity × 0.10)
```

### File structure on SSD

```
E:\NOT UPLOADED\              ← Source root
├── HEAD\                     ← Head camera clips
│   ├── GX010042.MP4
│   └── ...
├── LEFT\                     ← Left wrist camera clips
│   ├── GX080091.MP4
│   └── ...
├── RIGHT\                    ← Right wrist camera clips
│   ├── GX050033.MP4
│   └── ...
├── matched_sets.txt          ← Generated match file
├── .tricamsync_license       ← Saved license key
└── UPLOAD_READY\             ← Packaged output (if copy/move mode)
    ├── SET_001_HEAD.mp4
    ├── SET_001_LEFT.mp4
    ├── SET_001_RIGHT.mp4
    └── ...
```
