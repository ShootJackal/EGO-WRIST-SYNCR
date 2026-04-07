#!/usr/bin/env python3
"""EGO-WRIST-SYNCR Demo — shows every screen of the tool without real video files.

Run:  python demo.py
      python demo.py --step license     (show just the license screen)
      python demo.py --step menu        (show the main menu)
      python demo.py --step scan        (show the scan + match flow)
      python demo.py --step package     (show the package mode picker)
      python demo.py --step space       (show the disk space warning)
      python demo.py --step resume      (show the resume flow)
      python demo.py --step output      (show what matched_sets.txt looks like)
      python demo.py --step all         (run everything end-to-end, default)
"""

from __future__ import annotations

import argparse
import os
import sys
import time

APP_NAME = "EGO-WRIST-SYNCR"
VERSION = "2.1.0"
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
BAR_FILL = "█"
BAR_EMPTY = "░"
BAR_WIDTH = 30


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "    Press Enter to continue..."):
    input(msg)


def fake_progress(label: str, total: int, duration: float = 2.0):
    t0 = time.time()
    for i in range(total + 1):
        pct = i / total * 100
        filled = int(BAR_WIDTH * pct / 100)
        bar = BAR_FILL * filled + BAR_EMPTY * (BAR_WIDTH - filled)
        spin = SPINNER_FRAMES[i % len(SPINNER_FRAMES)] if i < total else "✓"
        elapsed = time.time() - t0
        m, s = divmod(int(elapsed), 60)
        t_str = f"{m}m {s}s" if m else f"{s}s"
        extra = f"{i}/{total}  {t_str}"
        sys.stdout.write(f"\r  {spin} {label} [{bar}] {pct:5.1f}%  {extra}")
        sys.stdout.flush()
        time.sleep(duration / total)
    sys.stdout.write(f"\r  ✓ {label:<55}\n")
    sys.stdout.flush()


def banner():
    print()
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║                                                       ║")
    print(f"  ║   {APP_NAME}  v{VERSION}                        ║")
    print("  ║   Tri-Cam Audio Sync & Packaging                     ║")
    print("  ║                                                       ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print()


# ─── STEP DEMOS ───────────────────────────────────────────────────

def demo_license():
    clear()
    banner()
    print("  ──────────────────────────────────────────────────")
    print("              LICENSE KEY REQUIRED")
    print("  ──────────────────────────────────────────────────")
    print()
    print("    Community key (free):  EWS-COMMUNITY-FREE-2025")
    print("    Pro keys:  purchase at <your-store-url>")
    print()
    print("    Enter key: EWS-COMMUNITY-FREE-2025")
    print("    Activated: COMMUNITY license")
    print()
    print("    License: COMMUNITY")
    print()
    pause()


def demo_drive_detection():
    clear()
    banner()
    print("    License: COMMUNITY")
    print()
    print("    Found 2 drives with 'NOT UPLOADED':")
    print("      1) E:\\NOT UPLOADED")
    print("      2) F:\\NOT UPLOADED")
    print()
    print("    Pick [1-2]: 1")
    print()
    print("    Source SSD: E:\\NOT UPLOADED")
    print()
    pause()


def demo_drive_prompt():
    clear()
    banner()
    print("    License: COMMUNITY")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  No external drive with NOT UPLOADED found.     │")
    print("  │  Enter a drive letter or full folder path.      │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Examples:  E")
    print("               E:\\NOT UPLOADED")
    print("               F:\\MyProject\\NOT UPLOADED")
    print()
    print("    Drive letter or path: E")
    print("    ✓ Found HEAD/LEFT/RIGHT in: E:\\NOT UPLOADED")
    print()
    print("    Source SSD: E:\\NOT UPLOADED")
    print()
    pause()


def demo_menu_no_csv():
    clear()
    banner()
    print("    License: COMMUNITY")
    print("    Source SSD: E:\\NOT UPLOADED")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  What would you like to do?                     │")
    print("  │                                                 │")
    print("  │  1) Full scan + match + package                 │")
    print("  │     Scans HEAD/LEFT/RIGHT, matches audio,       │")
    print("  │     then packages files                         │")
    print("  │                                                 │")
    print("  │  2) Scan only (generate match file first)       │")
    print("  │     Run the audio scan without packaging        │")
    print("  │                                                 │")
    print("  │  0) Exit                                        │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Choose [0/1/2]: 1")
    print()
    pause()


def demo_menu_with_csv():
    clear()
    banner()
    print("    License: PRO")
    print("    Source SSD: E:\\NOT UPLOADED")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  What would you like to do?                     │")
    print("  │                                                 │")
    print("  │  1) Full scan + match + package                 │")
    print("  │     Scans HEAD/LEFT/RIGHT, matches audio,       │")
    print("  │     then packages files                         │")
    print("  │                                                 │")
    print("  │  2) Package only (match file exists)            │")
    print("  │     Skip scanning — use existing match file     │")
    print("  │     to copy / move / transfer matched files     │")
    print("  │                                                 │")
    print("  │  3) Re-scan only (regenerate match file)        │")
    print("  │     Run the audio scan again without packaging  │")
    print("  │                                                 │")
    print("  │  4) Resume packaging                            │")
    print("  │     Continue a previous copy/transfer that      │")
    print("  │     was interrupted                             │")
    print("  │                                                 │")
    print("  │  0) Exit                                        │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Choose [0/1/2/3/4]: 2")
    print()
    pause()


def demo_scan():
    clear()
    print()
    print("  ── STEP 1/3 : Scanning camera folders ─────────────────")
    print()
    fake_progress("Scanning HEAD ", 18, 2.5)
    fake_progress("Scanning LEFT ", 22, 2.5)
    fake_progress("Scanning RIGHT", 20, 2.5)
    print()
    print("    Total: 60 files  (42.8 GB)")
    print()
    print("  ── STEP 2/3 : Audio fingerprint matching ──────────────")
    print()
    fake_progress("HEAD → LEFT ", 396, 3.0)
    fake_progress("HEAD → RIGHT", 360, 3.0)
    print()
    print("  ── STEP 3/3 : Building triplets (cross-validated) ─────")
    print()
    fake_progress("Assembling sets", 18, 1.5)
    print("    Rejected 2 triplet(s): LEFT-RIGHT cross-validation failed")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  ✓  Matched sets : 15                           │")
    print("  │     HIGH: 12   MEDIUM: 2   LOW: 1   REVIEW: 0  │")
    print("  │     Written to  : matched_sets.txt              │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    pause()


def demo_package_menu():
    clear()
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  How would you like to package the files?       │")
    print("  │                                                 │")
    print("  │  1) Copy (duplicate on same SSD)                │")
    print("  │     Keeps originals, creates UPLOAD_READY copy  │")
    print("  │                                                 │")
    print("  │  2) Move / reorganize (same SSD)                │")
    print("  │     Moves files into UPLOAD_READY (no copy)     │")
    print("  │     Saves disk space — originals are relocated  │")
    print("  │                                                 │")
    print("  │  3) Transfer to a different drive               │")
    print("  │     Copies files + match file to another SSD    │")
    print("  │     and creates the folder structure there      │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Choose [1/2/3]: 1")
    print()
    fake_progress("Copying files", 45, 3.0)
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  ✓  45 files packaged                           │")
    print("  │     Output: E:\\NOT UPLOADED\\UPLOAD_READY        │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Total time: 3m 42s")
    print()
    pause()


def demo_transfer():
    clear()
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  How would you like to package the files?       │")
    print("  │                                                 │")
    print("  │  1) Copy (duplicate on same SSD)                │")
    print("  │  2) Move / reorganize (same SSD)                │")
    print("  │  3) Transfer to a different drive               │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Choose [1/2/3]: 3")
    print()
    print("    Where should UPLOAD_READY be created?")
    print("    Enter a drive letter or full folder path.")
    print()
    print("    Examples:  F")
    print("               G:\\Projects\\UPLOAD_READY")
    print()
    print("    Destination drive or path: F")
    print("    ✓ Will use: F:\\UPLOAD_READY")
    print()
    fake_progress("Transferring files", 45, 3.0)
    print("    Match file copied to: F:\\UPLOAD_READY\\matched_sets.txt")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  ✓  45 files packaged                           │")
    print("  │     Output: F:\\UPLOAD_READY                     │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    pause()


def demo_space_warning():
    clear()
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  ⚠  NOT ENOUGH DISK SPACE                      │")
    print("  │     Need:      42.8 GB                          │")
    print("  │     Available:  12.3 GB                         │")
    print("  │                                                 │")
    print("  │  Options:                                       │")
    print("  │   - Free up space and re-run                    │")
    print("  │   - Use mode 2 (move) to avoid doubling         │")
    print("  │   - Use mode 3 (transfer) to a bigger drive     │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Continue anyway? (y/n): n")
    print("    Aborted. Re-run when ready.")
    print()
    pause()


def demo_crash_recovery():
    clear()
    print()
    fake_progress("Transferring files", 22, 2.0)
    print()
    print("    ⚠  Error on file: clip015_HEAD.mp4")
    print("       [Errno 5] Input/output error: 'F:\\UPLOAD_READY\\SET_008_HEAD.mp4'")
    print()
    print("    The drive may have been disconnected or run out of space.")
    print("    Progress saved — 22 of 45 files done.")
    print("    Re-run packaging to resume from where it stopped.")
    print()
    pause()

    clear()
    banner()
    print("    License: COMMUNITY")
    print("    Source SSD: E:\\NOT UPLOADED")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  What would you like to do?                     │")
    print("  │                                                 │")
    print("  │  1) Full scan + match + package                 │")
    print("  │  2) Package only (match file exists)            │")
    print("  │  3) Re-scan only (regenerate match file)        │")
    print("  │                                                 │")
    print("  │  4) Resume packaging                            │")
    print("  │     Continue a previous copy/transfer that      │")
    print("  │     was interrupted                             │")
    print("  │                                                 │")
    print("  │  0) Exit                                        │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Choose [0/1/2/3/4]: 4")
    print()
    fake_progress("Transferring files", 45, 2.5)
    print("    (22 files already done from previous run)")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  ✓  45 files packaged                           │")
    print("  │     Output: F:\\UPLOAD_READY                     │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    pause()


def demo_output():
    clear()
    print()
    print("  Contents of matched_sets.txt:")
    print("  " + "─" * 68)
    print()
    print("  EGO-WRIST-SYNCR  Matched Sets")
    print("  Generated: 2026-04-07 15:30:00")
    print("  Source:    E:\\NOT UPLOADED")
    print("  Total:     15 set(s)")
    print("  " + "=" * 68)
    print()
    print("  --- SET_001  [HIGH] ---")
    print()
    print("    HEAD:   E:\\NOT UPLOADED\\HEAD\\GX010042.MP4")
    print("    LEFT:   E:\\NOT UPLOADED\\LEFT\\GX080091.MP4")
    print("    RIGHT:  E:\\NOT UPLOADED\\RIGHT\\GX050033.MP4")
    print()
    print("    Duration  HEAD 245.30s  LEFT 245.10s  RIGHT 245.50s")
    print("    Size      HEAD 1820.5 MB  LEFT 1795.2 MB  RIGHT 1810.8 MB")
    print("    Audio     H-L 0.7823  H-R 0.7541  L-R 0.6912")
    print("    Score     0.7425  (min consensus hits: 3)")
    print()
    print("  --- SET_002  [HIGH] ---")
    print()
    print("    HEAD:   E:\\NOT UPLOADED\\HEAD\\GX010043.MP4")
    print("    LEFT:   E:\\NOT UPLOADED\\LEFT\\GX080092.MP4")
    print("    RIGHT:  E:\\NOT UPLOADED\\RIGHT\\GX050034.MP4")
    print()
    print("    Duration  HEAD 312.80s  LEFT 312.60s  RIGHT 313.10s")
    print("    Size      HEAD 2340.1 MB  LEFT 2318.7 MB  RIGHT 2329.4 MB")
    print("    Audio     H-L 0.8201  H-R 0.7892  L-R 0.7345")
    print("    Score     0.7813  (min consensus hits: 4)")
    print()
    print("  --- SET_003  [MEDIUM] ---")
    print()
    print("    HEAD:   E:\\NOT UPLOADED\\HEAD\\GX010044.MP4")
    print("    LEFT:   E:\\NOT UPLOADED\\LEFT\\GX080093.MP4")
    print("    RIGHT:  E:\\NOT UPLOADED\\RIGHT\\GX050035.MP4")
    print()
    print("    Duration  HEAD 198.40s  LEFT 199.10s  RIGHT 198.80s")
    print("    Size      HEAD 1480.2 MB  LEFT 1465.9 MB  RIGHT 1472.1 MB")
    print("    Audio     H-L 0.4512  H-R 0.4103  L-R 0.3211")
    print("    Score     0.4275  (min consensus hits: 2)")
    print()
    print("  " + "=" * 68)
    print("  Copy any path above and paste into File Explorer to navigate there.")
    print()
    pause()


# ─── MAIN ─────────────────────────────────────────────────────────

STEPS = {
    "license": ("License Key Entry", demo_license),
    "drive": ("Drive Detection", demo_drive_detection),
    "prompt": ("Manual Drive Entry", demo_drive_prompt),
    "menu": ("Main Menu (first run)", demo_menu_no_csv),
    "menu2": ("Main Menu (with existing match file + resume)", demo_menu_with_csv),
    "scan": ("Full Scan + Match", demo_scan),
    "package": ("Package Mode Picker + Copy", demo_package_menu),
    "transfer": ("Transfer to Different Drive", demo_transfer),
    "space": ("Disk Space Warning", demo_space_warning),
    "resume": ("Crash Recovery + Resume", demo_crash_recovery),
    "output": ("Match File Output", demo_output),
}


def run_all():
    clear()
    print()
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║       EGO-WRIST-SYNCR  DEMO WALKTHROUGH              ║")
    print("  ║                                                       ║")
    print("  ║  This will show every screen of the tool.             ║")
    print("  ║  Press Enter to advance through each step.            ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print()
    pause()

    order = ["license", "drive", "prompt", "menu", "scan",
             "package", "transfer", "space", "resume", "menu2", "output"]
    for i, key in enumerate(order, 1):
        title, func = STEPS[key]
        clear()
        print()
        print(f"  ── DEMO STEP {i}/{len(order)}: {title} ──")
        print()
        pause("    Press Enter to see this screen...")
        func()

    clear()
    print()
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║       DEMO COMPLETE                                   ║")
    print("  ║                                                       ║")
    print("  ║  You've seen every screen the tool can show:          ║")
    print("  ║   • License entry                                     ║")
    print("  ║   • Auto drive detection + manual prompt              ║")
    print("  ║   • Main menu (first run & returning)                 ║")
    print("  ║   • Scan with progress bars                           ║")
    print("  ║   • Package modes (copy / move / transfer)            ║")
    print("  ║   • Disk space warning                                ║")
    print("  ║   • Crash recovery + resume                           ║")
    print("  ║   • Output file format                                ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print()


def main():
    parser = argparse.ArgumentParser(description="EGO-WRIST-SYNCR Demo")
    parser.add_argument("--step", default="all",
                        choices=list(STEPS.keys()) + ["all"],
                        help="Which step to demo (default: all)")
    args = parser.parse_args()

    if args.step == "all":
        run_all()
    else:
        title, func = STEPS[args.step]
        func()


if __name__ == "__main__":
    main()
