#!/usr/bin/env python3
"""EGO-WRIST-SYNCR  --  Tri-Cam Sync Pipeline  (macOS)

Unified launcher with license validation, progress bars, and flexible
packaging modes.  Run directly for the interactive menu, or use CLI
subcommands for scripted workflows.

Auto-detection scans external volumes under /Volumes/ for a folder named
``NOT UPLOADED`` containing ``HEAD``, ``LEFT``, and ``RIGHT``.
Internal volumes (Macintosh HD) are skipped.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

from licensing import check_or_prompt, validate_key, load_stored_key

# ── media config ────────────────────────────────────────────────────
EXTENSIONS = {".mov", ".mp4", ".mxf", ".avi"}
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

# ── matching thresholds ─────────────────────────────────────────────
DURATION_TOL_SEC = 75
MAX_SIZE_RATIO = 1.8
AUDIO_SR = 8000
SAMPLE_SECONDS = 20
HOP_MS = 100
MAX_SHIFT_SEC = 25
MIN_AUDIO_SCORE = 0.18

# ── branding ────────────────────────────────────────────────────────
APP_NAME = "EGO-WRIST-SYNCR"
VERSION = "2.0.0"

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
BAR_FILL = "█"
BAR_EMPTY = "░"
BAR_WIDTH = 30

# ═══════════════════════════════════════════════════════════════════
#  Terminal UI helpers
# ═══════════════════════════════════════════════════════════════════

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print()
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║                                                       ║")
    print(f"  ║   {APP_NAME}  v{VERSION}                        ║")
    print("  ║   Tri-Cam Audio Sync & Packaging                     ║")
    print("  ║                                                       ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print()


def progress_bar(current: int, total: int, label: str = "",
                 extra: str = "", width: int = BAR_WIDTH):
    if total <= 0:
        pct = 100.0
    else:
        pct = min(100.0, current / total * 100)
    filled = int(width * pct / 100)
    bar = BAR_FILL * filled + BAR_EMPTY * (width - filled)
    spin = SPINNER_FRAMES[current % len(SPINNER_FRAMES)] if current < total else "✓"
    line = f"\r  {spin} {label} [{bar}] {pct:5.1f}%  {extra}"
    sys.stdout.write(line)
    sys.stdout.flush()


def progress_done(label: str = ""):
    sys.stdout.write(f"\r  ✓ {label:<55}\n")
    sys.stdout.flush()


def format_size(nbytes: int) -> str:
    if nbytes < 1024:
        return f"{nbytes} B"
    if nbytes < 1024 ** 2:
        return f"{nbytes / 1024:.1f} KB"
    if nbytes < 1024 ** 3:
        return f"{nbytes / 1024**2:.1f} MB"
    return f"{nbytes / 1024**3:.2f} GB"


def elapsed_str(sec: float) -> str:
    m, s = divmod(int(sec), 60)
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def ask_choice(prompt: str, options: list[str]) -> str:
    while True:
        try:
            val = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(1)
        if val in options:
            return val


# ═══════════════════════════════════════════════════════════════════
#  Drive / root resolution  (external volumes only)
# ═══════════════════════════════════════════════════════════════════

def _find_camera_dirs(root: Path) -> dict[str, Path] | None:
    if not root.exists() or not root.is_dir():
        return None
    found: dict[str, Path] = {}
    for child in root.iterdir():
        if not child.is_dir():
            continue
        key = child.name.strip().upper()
        if key in {"HEAD", "LEFT", "RIGHT"}:
            found[key] = child
    if {"HEAD", "LEFT", "RIGHT"}.issubset(found):
        return found
    return None


def _is_internal_volume(vol: Path) -> bool:
    name = vol.name
    if name == "Macintosh HD" or name.startswith("Macintosh HD"):
        return True
    try:
        if vol.resolve() == Path("/").resolve():
            return True
    except OSError:
        pass
    return False


def _get_external_volumes() -> list[Path]:
    volumes = Path("/Volumes")
    if not volumes.exists():
        return []
    external: list[Path] = []
    for vol in sorted(volumes.iterdir()):
        if not vol.is_dir():
            continue
        if _is_internal_volume(vol):
            continue
        external.append(vol)
    return external


def _prompt_for_root() -> Path:
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  No external volume with NOT UPLOADED found.    │")
    print("  │  Enter a volume name or full folder path.       │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Examples:  MySSD")
    print("               /Volumes/MySSD/NOT UPLOADED")
    print("               ~/Desktop/NOT UPLOADED")
    print()

    while True:
        try:
            response = input("    Volume name or path: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(1)
        if not response:
            continue

        if response.startswith("/") or response.startswith("~"):
            candidate = Path(response).expanduser()
        else:
            candidate = Path("/Volumes") / response / "NOT UPLOADED"

        if candidate.exists():
            if _find_camera_dirs(candidate):
                print(f"    ✓ Found HEAD/LEFT/RIGHT in: {candidate}")
            else:
                print(f"    ⚠ '{candidate}' exists but is missing HEAD/LEFT/RIGHT sub-folders.")
            return candidate

        vol_path = Path("/Volumes") / response
        if vol_path.exists():
            print(f"    Volume '{response}' exists but has no 'NOT UPLOADED' folder.")
            yn = ask_choice(f"    Use '{candidate}' anyway? (y/n): ", ["y", "n", "Y", "N"])
            if yn.lower() == "y":
                return candidate
            continue

        print(f"    Path '{candidate}' does not exist. Try again.")


def _prompt_for_destination_volume() -> Path:
    """Ask the user for a destination volume/path for transfer mode."""
    print()
    print("    Where should UPLOAD_READY be created?")
    print("    Enter a volume name or full folder path.")
    print()
    print("    Examples:  MyOtherSSD")
    print("               /Volumes/MyOtherSSD/UPLOAD_READY")
    print()

    while True:
        try:
            response = input("    Destination volume or path: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(1)
        if not response:
            continue

        if response.startswith("/") or response.startswith("~"):
            candidate = Path(response).expanduser()
        else:
            candidate = Path("/Volumes") / response / "UPLOAD_READY"

        parent = candidate.parent
        if parent.exists():
            print(f"    ✓ Will use: {candidate}")
            return candidate
        print(f"    Path '{parent}' does not exist. Try again.")


def resolve_root(root_arg: str | None = None) -> Path:
    """Resolve project root across any plugged-in external SSD.

    Priority:
    1) explicit --root argument
    2) TRI_CAM_ROOT environment variable
    3) first external volume with NOT UPLOADED/HEAD, LEFT, RIGHT
    4) interactive prompt
    """
    if root_arg:
        return Path(root_arg).expanduser()

    env_root = os.environ.get("TRI_CAM_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser()

    external_vols = _get_external_volumes()
    candidates: list[Path] = []
    for vol in external_vols:
        candidate = vol / "NOT UPLOADED"
        if _find_camera_dirs(candidate):
            candidates.append(candidate)

    if candidates:
        if len(candidates) == 1:
            return candidates[0]
        print(f"\n    Found {len(candidates)} volumes with 'NOT UPLOADED':")
        for i, c in enumerate(candidates, 1):
            print(f"      {i}) {c}")
        choice = ask_choice(f"    Pick [1-{len(candidates)}]: ",
                            [str(i) for i in range(1, len(candidates) + 1)])
        return candidates[int(choice) - 1]

    return _prompt_for_root()


# ═══════════════════════════════════════════════════════════════════
#  FFmpeg / audio helpers
# ═══════════════════════════════════════════════════════════════════

def run_cmd(cmd: list[str]) -> bytes:
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL)


def ffprobe_info(path: Path) -> tuple[float, int]:
    cmd = [
        FFPROBE, "-v", "error",
        "-show_entries", "format=duration,size",
        "-of", "json", str(path),
    ]
    raw = run_cmd(cmd).decode("utf-8", errors="ignore")
    data = json.loads(raw)
    fmt = data.get("format", {})
    duration = float(fmt.get("duration", 0.0))
    size = int(fmt.get("size", path.stat().st_size))
    return duration, size


def make_envelope_from_pcm(raw_bytes: bytes, sr: int = AUDIO_SR, hop_ms: int = HOP_MS):
    if not raw_bytes:
        return None
    audio = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
    if audio.size < sr:
        return None
    audio /= 32768.0
    audio = np.abs(audio)
    hop = max(1, int(sr * hop_ms / 1000))
    usable = (audio.size // hop) * hop
    if usable <= 0:
        return None
    env = audio[:usable].reshape(-1, hop).mean(axis=1)
    k = min(21, len(env))
    if k >= 3:
        smooth = np.convolve(env, np.ones(k) / k, mode="same")
        env = env - smooth
    std = env.std()
    if std < 1e-8:
        return None
    env = (env - env.mean()) / std
    return env


@lru_cache(maxsize=10000)
def extract_env(path_str: str, start_sec: int):
    cmd = [
        FFMPEG, "-v", "error",
        "-ss", str(start_sec), "-i", path_str,
        "-vn", "-ac", "1", "-ar", str(AUDIO_SR),
        "-t", str(SAMPLE_SECONDS), "-f", "s16le", "-",
    ]
    try:
        raw = run_cmd(cmd)
    except Exception:
        return None
    return make_envelope_from_pcm(raw)


def corr_score(a, b, hop_ms: int = HOP_MS, max_shift_sec: int = MAX_SHIFT_SEC):
    if a is None or b is None:
        return None, None
    corr = np.correlate(a, b, mode="full")
    lags = np.arange(-len(b) + 1, len(a))
    max_bins = int(max_shift_sec * 1000 / hop_ms)
    mask = (lags >= -max_bins) & (lags <= max_bins)
    corr = corr[mask]
    lags = lags[mask]
    if corr.size == 0:
        return None, None
    idx = int(np.argmax(corr))
    best = float(corr[idx] / min(len(a), len(b)))
    lag_bins = int(lags[idx])
    offset_sec = lag_bins * hop_ms / 1000.0
    return best, offset_sec


def duration_sim(d1: float, d2: float) -> float:
    diff = abs(d1 - d2)
    return max(0.0, 1.0 - diff / DURATION_TOL_SEC)


def size_sim(s1: int, s2: int) -> float:
    small, big = min(s1, s2), max(s1, s2)
    if small <= 0:
        return 0.0
    ratio = big / small
    if ratio > MAX_SIZE_RATIO:
        return 0.0
    return max(0.0, 1.0 - (ratio - 1.0) / (MAX_SIZE_RATIO - 1.0))


def candidate_ok(a: dict, b: dict) -> bool:
    if abs(a["duration"] - b["duration"]) > DURATION_TOL_SEC:
        return False
    small, big = min(a["size"], b["size"]), max(a["size"], b["size"])
    if small <= 0:
        return False
    return big / small <= MAX_SIZE_RATIO


def choose_sample_starts(d1: float, d2: float) -> list[int]:
    m = min(d1, d2)
    starts = [0]
    if m > SAMPLE_SECONDS * 3:
        starts.append(int(max(0, (m / 2) - (SAMPLE_SECONDS / 2))))
    if m > SAMPLE_SECONDS * 5:
        starts.append(int(max(0, m - SAMPLE_SECONDS - 10)))
    seen: set[int] = set()
    return [s for s in starts if s not in seen and not seen.add(s)]  # type: ignore[func-returns-value]


def audio_match_score(a: dict, b: dict):
    starts = choose_sample_starts(a["duration"], b["duration"])
    best_score = best_offset = None
    for start_sec in starts:
        env_a = extract_env(str(a["path"]), start_sec)
        env_b = extract_env(str(b["path"]), start_sec)
        score, offset = corr_score(env_a, env_b)
        if score is not None and (best_score is None or score > best_score):
            best_score, best_offset = score, offset
    return best_score, best_offset


def combined_score(a: dict, b: dict):
    ds = duration_sim(a["duration"], b["duration"])
    ss = size_sim(a["size"], b["size"])
    audio_score, offset = audio_match_score(a, b)
    if audio_score is None:
        return None, None, ds, ss, None
    total = (audio_score * 0.75) + (ds * 0.15) + (ss * 0.10)
    return total, offset, ds, ss, audio_score


def confidence_label(total: float, audio_score: float) -> str:
    if audio_score is None:
        return "NO_AUDIO"
    if total >= 0.60 and audio_score >= 0.45:
        return "HIGH"
    if total >= 0.40 and audio_score >= 0.28:
        return "MEDIUM"
    if total >= 0.25 and audio_score >= MIN_AUDIO_SCORE:
        return "LOW"
    return "REVIEW"


# ═══════════════════════════════════════════════════════════════════
#  Scanning  (with progress bar)
# ═══════════════════════════════════════════════════════════════════

def _discover_media(folder: Path) -> list[Path]:
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    )


def scan_folder(folder: Path, label: str) -> list[dict]:
    media = _discover_media(folder)
    total = len(media)
    files: list[dict] = []
    t0 = time.time()

    for i, p in enumerate(media):
        elapsed = time.time() - t0
        extra = f"{i+1}/{total}  {elapsed_str(elapsed)}"
        progress_bar(i, total, f"Scanning {label}", extra)

        try:
            duration, size = ffprobe_info(p)
        except Exception:
            continue

        files.append({
            "camera": label,
            "path": p,
            "name": p.name,
            "relpath": str(p.relative_to(folder)),
            "duration": duration,
            "size": size,
        })

    progress_done(f"Scanning {label} — {len(files)} files found ({elapsed_str(time.time() - t0)})")
    return files


# ═══════════════════════════════════════════════════════════════════
#  Matching  (with progress bar)
# ═══════════════════════════════════════════════════════════════════

def greedy_match(anchor_files: list[dict], other_files: list[dict],
                 label: str = "") -> dict[int, dict]:
    total_pairs = len(anchor_files) * len(other_files)
    pair_idx = 0
    t0 = time.time()

    candidates = []
    for i, a in enumerate(anchor_files):
        for j, b in enumerate(other_files):
            pair_idx += 1
            if pair_idx % max(1, total_pairs // 200) == 0 or pair_idx == total_pairs:
                extra = f"{pair_idx}/{total_pairs}  {elapsed_str(time.time() - t0)}"
                progress_bar(pair_idx, total_pairs, label, extra)

            if not candidate_ok(a, b):
                continue
            total, offset, ds, ss, audio_score = combined_score(a, b)
            if total is None or audio_score is None or audio_score < MIN_AUDIO_SCORE:
                continue
            candidates.append({
                "anchor_idx": i, "other_idx": j,
                "total": total, "audio_score": audio_score,
                "offset": offset, "duration_sim": ds, "size_sim": ss,
            })

    progress_done(f"{label} — {len(candidates)} candidates ({elapsed_str(time.time() - t0)})")

    candidates.sort(key=lambda x: x["total"], reverse=True)
    used_anchor: set[int] = set()
    used_other: set[int] = set()
    matches: dict[int, dict] = {}
    for c in candidates:
        i, j = c["anchor_idx"], c["other_idx"]
        if i in used_anchor or j in used_other:
            continue
        matches[i] = c
        used_anchor.add(i)
        used_other.add(j)
    return matches


# ═══════════════════════════════════════════════════════════════════
#  run_match
# ═══════════════════════════════════════════════════════════════════

CSV_FIELDS = [
    "set_id", "confidence",
    "head_file", "left_file", "right_file",
    "head_duration_sec", "left_duration_sec", "right_duration_sec",
    "head_size_mb", "left_size_mb", "right_size_mb",
    "head_left_audio_score", "head_right_audio_score", "left_right_audio_score",
    "left_offset_vs_head_sec", "right_offset_vs_head_sec", "right_offset_vs_left_sec",
    "head_left_total", "head_right_total", "left_right_total",
    "avg_total_score", "avg_audio_score",
]


def run_match(root: Path) -> Path:
    camera_dirs = _find_camera_dirs(root)
    if not camera_dirs:
        raise FileNotFoundError(
            "Missing HEAD/LEFT/RIGHT under root. "
            f"Resolved root: {root}"
        )

    print()
    print("  ── STEP 1/3 : Scanning camera folders ─────────────────")
    print()

    head_files = scan_folder(camera_dirs["HEAD"], "HEAD ")
    left_files = scan_folder(camera_dirs["LEFT"], "LEFT ")
    right_files = scan_folder(camera_dirs["RIGHT"], "RIGHT")

    total_size = sum(f["size"] for grp in (head_files, left_files, right_files) for f in grp)
    print(f"\n    Total: {len(head_files) + len(left_files) + len(right_files)} "
          f"files  ({format_size(total_size)})")

    print()
    print("  ── STEP 2/3 : Audio fingerprint matching ──────────────")
    print()

    head_left = greedy_match(head_files, left_files, "HEAD → LEFT ")
    head_right = greedy_match(head_files, right_files, "HEAD → RIGHT")

    print()
    print("  ── STEP 3/3 : Building triplets ───────────────────────")
    print()

    rows: list[dict] = []
    used_left: set[int] = set()
    used_right: set[int] = set()
    triplet_total = len(head_files)

    for head_idx, head in enumerate(head_files):
        progress_bar(head_idx, triplet_total, "Assembling sets",
                     f"{len(rows)} sets so far")

        if head_idx not in head_left or head_idx not in head_right:
            continue
        left_idx = head_left[head_idx]["other_idx"]
        right_idx = head_right[head_idx]["other_idx"]
        if left_idx in used_left or right_idx in used_right:
            continue

        left = left_files[left_idx]
        right = right_files[right_idx]
        lr_total, lr_offset, _, _, lr_audio = combined_score(left, right)
        hl = head_left[head_idx]
        hr = head_right[head_idx]

        avg_total = float(np.mean([
            hl["total"], hr["total"],
            lr_total if lr_total is not None else 0.0,
        ]))
        avg_audio = float(np.mean([
            hl["audio_score"], hr["audio_score"],
            lr_audio if lr_audio is not None else 0.0,
        ]))

        rows.append({
            "set_id": f"SET_{len(rows)+1:03d}",
            "confidence": confidence_label(avg_total, avg_audio),
            "head_file": head["relpath"],
            "left_file": left["relpath"],
            "right_file": right["relpath"],
            "head_duration_sec": round(head["duration"], 2),
            "left_duration_sec": round(left["duration"], 2),
            "right_duration_sec": round(right["duration"], 2),
            "head_size_mb": round(head["size"] / (1024**2), 2),
            "left_size_mb": round(left["size"] / (1024**2), 2),
            "right_size_mb": round(right["size"] / (1024**2), 2),
            "head_left_audio_score": round(hl["audio_score"], 4),
            "head_right_audio_score": round(hr["audio_score"], 4),
            "left_right_audio_score": round(lr_audio, 4) if lr_audio is not None else "",
            "left_offset_vs_head_sec": round(hl["offset"], 2) if hl["offset"] is not None else "",
            "right_offset_vs_head_sec": round(hr["offset"], 2) if hr["offset"] is not None else "",
            "right_offset_vs_left_sec": round(lr_offset, 2) if lr_offset is not None else "",
            "head_left_total": round(hl["total"], 4),
            "head_right_total": round(hr["total"], 4),
            "left_right_total": round(lr_total, 4) if lr_total is not None else "",
            "avg_total_score": round(avg_total, 4),
            "avg_audio_score": round(avg_audio, 4),
        })
        used_left.add(left_idx)
        used_right.add(right_idx)

    progress_done(f"Assembled {len(rows)} matched triplet(s)")

    rows.sort(key=lambda x: x["avg_total_score"], reverse=True)

    out_csv = root / "matched_triplets.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print(f"  │  ✓  Matched sets : {len(rows):<31}│")
    print(f"  │     CSV written  : {str(out_csv):<31}│")
    print("  └─────────────────────────────────────────────────┘")
    print()
    return out_csv


# ═══════════════════════════════════════════════════════════════════
#  run_package  —  3 modes: copy, move, transfer
# ═══════════════════════════════════════════════════════════════════

def _package_menu() -> str:
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
    print("  │     Copies files + CSV to another SSD/drive     │")
    print("  │     and creates the folder structure there      │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    return ask_choice("    Choose [1/2/3]: ", ["1", "2", "3"])


def run_package(root: Path, csv_path: Path | None = None,
                mode: str | None = None,
                dest_path: Path | None = None) -> Path:
    camera_dirs = _find_camera_dirs(root)
    if not camera_dirs:
        raise FileNotFoundError(
            "Missing HEAD/LEFT/RIGHT under root. "
            f"Resolved root: {root}"
        )

    csv_file = csv_path if csv_path else root / "matched_triplets.csv"
    if not csv_file.exists():
        raise FileNotFoundError(f"Missing CSV: {csv_file}. Run a full scan first.")

    if mode is None:
        mode = _package_menu()

    if mode == "3" and dest_path is None:
        dest_path = _prompt_for_destination_volume()

    if mode == "3":
        upload_dir = dest_path  # type: ignore[assignment]
    else:
        upload_dir = root / "UPLOAD_READY"

    upload_dir.mkdir(parents=True, exist_ok=True)

    with csv_file.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    file_ops: list[tuple[Path, Path]] = []
    for row in rows:
        set_id = row["set_id"]
        for src_rel, cam in [
            (row["head_file"], "HEAD"),
            (row["left_file"], "LEFT"),
            (row["right_file"], "RIGHT"),
        ]:
            src = camera_dirs[cam] / src_rel
            if src.exists():
                dst = upload_dir / f"{set_id}_{cam}{src.suffix.lower()}"
                file_ops.append((src, dst))

    total = len(file_ops)
    total_bytes = sum(s.stat().st_size for s, _ in file_ops if s.exists())
    verb = "Moving" if mode == "2" else "Copying" if mode == "1" else "Transferring"
    t0 = time.time()

    for i, (src, dst) in enumerate(file_ops):
        extra = f"{i+1}/{total}  {format_size(src.stat().st_size)}"
        progress_bar(i, total, f"{verb} files", extra)

        if mode == "2":
            shutil.move(str(src), str(dst))
        else:
            shutil.copy2(src, dst)

    progress_done(f"{verb} complete — {total} files ({format_size(total_bytes)}, {elapsed_str(time.time() - t0)})")

    if mode == "3":
        dest_csv = upload_dir / "matched_triplets.csv"
        shutil.copy2(csv_file, dest_csv)
        print(f"    CSV copied to: {dest_csv}")

    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print(f"  │  ✓  {total} files packaged                        │")
    print(f"  │     Output: {str(upload_dir):<36}│")
    print("  └─────────────────────────────────────────────────┘")
    print()
    return upload_dir


# ═══════════════════════════════════════════════════════════════════
#  Interactive launcher
# ═══════════════════════════════════════════════════════════════════

def interactive_launcher():
    clear_screen()
    banner()

    _, tier = check_or_prompt()
    print(f"    License: {tier}")
    print()

    root = resolve_root()
    print(f"    Source SSD: {root}")
    print()

    csv_exists = (root / "matched_triplets.csv").exists()

    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  What would you like to do?                     │")
    print("  │                                                 │")
    print("  │  1) Full scan + match + package                 │")
    print("  │     Scans HEAD/LEFT/RIGHT, matches audio,       │")
    print("  │     writes CSV, then packages files             │")
    print("  │                                                 │")
    if csv_exists:
        print("  │  2) Package only (CSV already exists)           │")
        print("  │     Skip scanning — use existing CSV to         │")
        print("  │     copy / move / transfer matched files        │")
        print("  │                                                 │")
        print("  │  3) Re-scan only (regenerate CSV)               │")
        print("  │     Run the audio scan again without packaging  │")
        print("  │                                                 │")
    else:
        print("  │  2) Scan only (generate CSV, package later)     │")
        print("  │     Run the audio scan without packaging        │")
        print("  │                                                 │")
    print("  │  0) Exit                                        │")
    print("  └─────────────────────────────────────────────────┘")
    print()

    if csv_exists:
        choice = ask_choice("    Choose [0/1/2/3]: ", ["0", "1", "2", "3"])
    else:
        choice = ask_choice("    Choose [0/1/2]: ", ["0", "1", "2"])

    if choice == "0":
        print("    Goodbye!")
        return

    t_global = time.time()

    if choice == "1":
        csv_out = run_match(root)
        run_package(root, csv_out)
    elif choice == "2" and csv_exists:
        run_package(root)
    elif choice == "2" and not csv_exists:
        run_match(root)
    elif choice == "3":
        run_match(root)

    print(f"    Total time: {elapsed_str(time.time() - t_global)}")
    print()


# ═══════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{VERSION} — Tri-Cam Sync Pipeline (macOS)")

    subparsers = parser.add_subparsers(dest="command")

    launch_p = subparsers.add_parser("launch", help="Interactive menu (default)")
    launch_p.add_argument("--root", default=None)

    match_p = subparsers.add_parser("match", help="Generate matched_triplets.csv")
    match_p.add_argument("--root", default=None)

    pkg_p = subparsers.add_parser("package", help="Package matched clips")
    pkg_p.add_argument("--root", default=None)
    pkg_p.add_argument("--csv", default=None)
    pkg_p.add_argument("--mode", choices=["1", "2", "3"], default=None,
                       help="1=copy, 2=move, 3=transfer")
    pkg_p.add_argument("--dest", default=None, help="Destination path (mode 3)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None or args.command == "launch":
        interactive_launcher()
        return 0

    check_or_prompt()

    root = resolve_root(getattr(args, "root", None))
    print(f"    Source SSD: {root}")

    if args.command == "match":
        run_match(root)
        return 0

    if args.command == "package":
        csv_path = Path(args.csv) if args.csv else None
        dest = Path(args.dest) if args.dest else None
        run_package(root, csv_path, mode=args.mode, dest_path=dest)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
