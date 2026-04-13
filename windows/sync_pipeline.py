#!/usr/bin/env python3
"""EGO-WRIST-SYNCR  --  Tri-Cam Sync Pipeline  (Windows)

Unified launcher with license validation, progress bars, and flexible
packaging modes.  Run directly for the interactive menu, or use CLI
subcommands for scripted workflows.

Auto-detection scans external (non-system) drives for a folder named
``NOT UPLOADED`` containing ``HEAD``, ``LEFT``, and ``RIGHT``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import string
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from licensing import check_or_prompt

# ── media config ────────────────────────────────────────────────────
EXTENSIONS = {".mov", ".mp4", ".mxf", ".avi"}
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

# ── matching thresholds ─────────────────────────────────────────────
DURATION_TOL_SEC = 75
MAX_SIZE_RATIO = 1.8
AUDIO_SR = 8000
SAMPLE_SECONDS = 30
HOP_MS = 100
MAX_SHIFT_SEC = 25
MIN_PAIR_SCORE = 0.25
MIN_LR_SCORE = 0.20
MIN_TRIPLET_AVG = 0.30

# ── branding ────────────────────────────────────────────────────────
APP_NAME = "EGO-WRIST-SYNCR"
VERSION = "3.0.0"

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
BAR_FILL = "█"
BAR_EMPTY = "░"
BAR_WIDTH = 30

MATCH_FILE = "matched_sets.txt"
PROGRESS_FILE = ".package_progress"

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
#  Drive / root resolution  (external-only)
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


def _system_drive_letter() -> str:
    return os.environ.get("SystemDrive", "C:")[0].upper()


def _get_external_drives() -> list[str]:
    sys_letter = _system_drive_letter()
    drives: list[str] = []
    for letter in string.ascii_uppercase:
        if letter == sys_letter:
            continue
        if Path(f"{letter}:/").exists():
            drives.append(letter)
    return drives


def _prompt_for_root() -> Path:
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  No external drive with NOT UPLOADED found.     │")
    print("  │  Enter a drive letter or full folder path.      │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    print("    Examples:  E")
    print(r"               E:\NOT UPLOADED")
    print(r"               F:\MyProject\NOT UPLOADED")
    print()

    while True:
        try:
            response = input("    Drive letter or path: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(1)
        if not response:
            continue

        if len(response) == 1 and response.upper() in string.ascii_uppercase:
            candidate = Path(f"{response.upper()}:/NOT UPLOADED")
        elif len(response) == 2 and response.endswith(":") and response[0].upper() in string.ascii_uppercase:
            candidate = Path(f"{response[0].upper()}:/NOT UPLOADED")
        else:
            candidate = Path(response).expanduser()

        if candidate.exists():
            if _find_camera_dirs(candidate):
                print(f"    ✓ Found HEAD/LEFT/RIGHT in: {candidate}")
            else:
                print(f"    ⚠ '{candidate}' exists but is missing HEAD/LEFT/RIGHT sub-folders.")
            return candidate

        parent_drive = Path(candidate.anchor)
        if parent_drive.exists():
            print(f"    Path does not exist yet on drive {candidate.anchor}")
            yn = ask_choice("    Create and use it anyway? (y/n): ", ["y", "n", "Y", "N"])
            if yn.lower() == "y":
                return candidate
        else:
            print(f"    Drive '{candidate.anchor}' does not exist. Try again.")


def _prompt_for_destination_drive() -> Path:
    print()
    print("    Where should UPLOAD_READY be created?")
    print("    Enter a drive letter or full folder path.")
    print()
    print(r"    Examples:  F")
    print(r"               G:\Projects\UPLOAD_READY")
    print()

    while True:
        try:
            response = input("    Destination drive or path: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(1)
        if not response:
            continue

        if len(response) == 1 and response.upper() in string.ascii_uppercase:
            candidate = Path(f"{response.upper()}:/UPLOAD_READY")
        elif len(response) == 2 and response.endswith(":") and response[0].upper() in string.ascii_uppercase:
            candidate = Path(f"{response[0].upper()}:/UPLOAD_READY")
        else:
            candidate = Path(response).expanduser()

        parent_drive = Path(candidate.anchor)
        if parent_drive.exists():
            print(f"    ✓ Will use: {candidate}")
            return candidate
        print(f"    Drive '{candidate.anchor}' does not exist. Try again.")


def resolve_root(root_arg: str | None = None) -> Path:
    if root_arg:
        return Path(root_arg).expanduser()

    env_root = os.environ.get("TRI_CAM_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser()

    external_drives = _get_external_drives()
    candidates: list[Path] = []
    for drive in external_drives:
        candidate = Path(f"{drive}:/") / "NOT UPLOADED"
        if _find_camera_dirs(candidate):
            candidates.append(candidate)

    if candidates:
        if len(candidates) == 1:
            return candidates[0]
        print(f"\n    Found {len(candidates)} drives with 'NOT UPLOADED':")
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


def _extract_env_raw(path_str: str, start_sec: int):
    """Extract audio envelope from a file — no caching, safe for workers."""
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


_env_cache: dict[tuple[str, int], object] = {}


def extract_env(path_str: str, start_sec: int):
    key = (path_str, start_sec)
    if key in _env_cache:
        return _env_cache[key]
    result = _extract_env_raw(path_str, start_sec)
    _env_cache[key] = result
    return result


def _max_workers() -> int:
    cpus = os.cpu_count() or 4
    return max(4, cpus)


def preextract_audio(files: list[dict], label: str):
    """Pre-extract audio envelopes for all files at all sample points in parallel."""
    jobs: list[tuple[str, int]] = []
    for f in files:
        for start in choose_sample_starts(f["duration"], f["duration"]):
            key = (str(f["path"]), start)
            if key not in _env_cache:
                jobs.append(key)

    if not jobs:
        return

    total = len(jobs)
    done = 0
    t0 = time.time()
    workers = _max_workers()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_extract_env_raw, path_str, start): (path_str, start)
            for path_str, start in jobs
        }
        for future in as_completed(futures):
            path_str, start = futures[future]
            try:
                _env_cache[(path_str, start)] = future.result()
            except Exception:
                _env_cache[(path_str, start)] = None
            done += 1
            if done % max(1, total // 50) == 0 or done == total:
                extra = f"{done}/{total}  {_max_workers()}T  {elapsed_str(time.time() - t0)}"
                progress_bar(done, total, f"Extracting {label}", extra)

    progress_done(f"Extracting {label} — {total} samples ({_max_workers()} threads, {elapsed_str(time.time() - t0)})")


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
    """Pick up to 5 evenly-spaced sample points across the clip."""
    m = min(d1, d2)
    if m < SAMPLE_SECONDS:
        return [0]
    starts = [0]
    if m > SAMPLE_SECONDS * 2:
        starts.append(int(m * 0.25))
    if m > SAMPLE_SECONDS * 2.5:
        starts.append(int(max(0, (m / 2) - (SAMPLE_SECONDS / 2))))
    if m > SAMPLE_SECONDS * 3:
        starts.append(int(m * 0.75 - SAMPLE_SECONDS))
    if m > SAMPLE_SECONDS * 3.5:
        starts.append(int(max(0, m - SAMPLE_SECONDS - 5)))
    seen: set[int] = set()
    return [s for s in starts if s not in seen and not seen.add(s)]  # type: ignore[func-returns-value]


def audio_match_score(a: dict, b: dict):
    """Sample up to 5 points, return best score, median score, and hit count."""
    starts = choose_sample_starts(a["duration"], b["duration"])
    scores: list[float] = []
    offsets: list[float] = []
    for start_sec in starts:
        env_a = extract_env(str(a["path"]), start_sec)
        env_b = extract_env(str(b["path"]), start_sec)
        score, offset = corr_score(env_a, env_b)
        if score is not None and offset is not None:
            scores.append(score)
            offsets.append(offset)

    if not scores:
        return None, None, None, 0

    hits = sum(1 for s in scores if s >= MIN_PAIR_SCORE)
    best_idx = int(np.argmax(scores))
    median = float(np.median(scores))
    return scores[best_idx], offsets[best_idx], median, hits


def combined_score(a: dict, b: dict):
    ds = duration_sim(a["duration"], b["duration"])
    ss = size_sim(a["size"], b["size"])
    best_audio, offset, median_audio, hits = audio_match_score(a, b)
    if best_audio is None:
        return None, None, ds, ss, None, None, 0
    total = (best_audio * 0.60) + (median_audio * 0.15) + (ds * 0.15) + (ss * 0.10)
    return total, offset, ds, ss, best_audio, median_audio, hits


def confidence_label(avg_total: float, avg_audio: float,
                     min_hits: int) -> str:
    if avg_audio is None:
        return "NO_AUDIO"
    if avg_total >= 0.55 and avg_audio >= 0.45 and min_hits >= 2:
        return "HIGH"
    if avg_total >= 0.40 and avg_audio >= 0.30:
        return "MEDIUM"
    if avg_total >= MIN_TRIPLET_AVG:
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
#  Matching  (with progress bar + consensus)
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
            total, offset, ds, ss, best_audio, median_audio, hits = combined_score(a, b)
            if total is None or best_audio is None or best_audio < MIN_PAIR_SCORE:
                continue
            candidates.append({
                "anchor_idx": i, "other_idx": j,
                "total": total, "audio_score": best_audio,
                "median_audio": median_audio,
                "offset": offset, "duration_sim": ds, "size_sim": ss,
                "hits": hits,
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
#  run_match  —  full scan + human-readable TXT
# ═══════════════════════════════════════════════════════════════════

def _write_match_txt(rows: list[dict], unmatched: dict[str, list[str]],
                     out_path: Path, root: Path,
                     camera_dirs: dict[str, Path]):
    """Write a human-readable, copy-paste-friendly match file."""
    n_unmatched = sum(len(v) for v in unmatched.values())
    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"EGO-WRIST-SYNCR  Matched Sets\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source:    {root}\n")
        f.write(f"Matched:   {len(rows)} set(s)\n")
        if n_unmatched:
            f.write(f"Unmatched: {n_unmatched} file(s) had no confident match\n")
        f.write("=" * 70 + "\n\n")

        for row in rows:
            f.write(f"--- {row['set_id']}  [{row['confidence']}] ---\n")
            f.write(f"\n")
            f.write(f"  HEAD:   {camera_dirs['HEAD'] / row['head_file']}\n")
            f.write(f"  LEFT:   {camera_dirs['LEFT'] / row['left_file']}\n")
            f.write(f"  RIGHT:  {camera_dirs['RIGHT'] / row['right_file']}\n")
            f.write(f"\n")
            f.write(f"  Duration  HEAD {row['head_duration_sec']}s"
                    f"  LEFT {row['left_duration_sec']}s"
                    f"  RIGHT {row['right_duration_sec']}s\n")
            f.write(f"  Size      HEAD {row['head_size_mb']} MB"
                    f"  LEFT {row['left_size_mb']} MB"
                    f"  RIGHT {row['right_size_mb']} MB\n")
            f.write(f"  Audio     H-L {row['hl_audio']}"
                    f"  H-R {row['hr_audio']}"
                    f"  L-R {row['lr_audio']}\n")
            f.write(f"  Score     {row['avg_total_score']}"
                    f"  (hits: {row['min_hits']})\n")
            f.write("\n")

        if n_unmatched:
            f.write("\n")
            f.write("=" * 70 + "\n")
            f.write("UNMATCHED FILES  (no confident triplet found)\n")
            f.write("=" * 70 + "\n\n")
            for cam in ("HEAD", "LEFT", "RIGHT"):
                files = unmatched.get(cam, [])
                if files:
                    f.write(f"  {cam} ({len(files)} files):\n")
                    for fp in files:
                        f.write(f"    {fp}\n")
                    f.write("\n")

        f.write("=" * 70 + "\n")
        f.write("Copy any path above and paste into File Explorer to navigate there.\n")


def _parse_match_txt(txt_path: Path) -> list[dict]:
    """Parse the human-readable TXT back into structured rows for packaging."""
    rows: list[dict] = []
    current: dict = {}
    root_str = ""

    with txt_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            if line.startswith("Source:"):
                root_str = line.split(":", 1)[1].strip()

            if line.startswith("--- SET_"):
                if current:
                    rows.append(current)
                parts = line.strip("- ").split()
                current = {"set_id": parts[0]}
                if len(parts) > 1:
                    current["confidence"] = parts[1].strip("[]")

            elif line.strip().startswith("HEAD:") and "set_id" in current:
                current["head_full"] = line.split("HEAD:", 1)[1].strip()
            elif line.strip().startswith("LEFT:") and "set_id" in current:
                current["left_full"] = line.split("LEFT:", 1)[1].strip()
            elif line.strip().startswith("RIGHT:") and "set_id" in current:
                current["right_full"] = line.split("RIGHT:", 1)[1].strip()

    if current and "set_id" in current:
        rows.append(current)

    return rows


def run_match(root: Path) -> Path:
    camera_dirs = _find_camera_dirs(root)
    if not camera_dirs:
        raise FileNotFoundError(
            "Missing HEAD/LEFT/RIGHT under root. "
            f"Resolved root: {root}"
        )

    print()
    print("  ── STEP 1/4 : Scanning camera folders ─────────────────")
    print()

    head_files = scan_folder(camera_dirs["HEAD"], "HEAD ")
    left_files = scan_folder(camera_dirs["LEFT"], "LEFT ")
    right_files = scan_folder(camera_dirs["RIGHT"], "RIGHT")

    total_size = sum(f["size"] for grp in (head_files, left_files, right_files) for f in grp)
    print(f"\n    Total: {len(head_files) + len(left_files) + len(right_files)} "
          f"files  ({format_size(total_size)})")

    print()
    print(f"  ── STEP 2/4 : Extracting audio ({_max_workers()} threads) ────────")
    print()

    preextract_audio(head_files, "HEAD ")
    preextract_audio(left_files, "LEFT ")
    preextract_audio(right_files, "RIGHT")

    print()
    print("  ── STEP 3/4 : Audio fingerprint matching ──────────────")
    print()

    head_left = greedy_match(head_files, left_files, "HEAD → LEFT ")
    head_right = greedy_match(head_files, right_files, "HEAD → RIGHT")

    print()
    print("  ── STEP 4/4 : Building triplets (cross-validated) ─────")
    print()

    rows: list[dict] = []
    rejected_lr = 0
    rejected_weak = 0
    used_head: set[int] = set()
    used_left: set[int] = set()
    used_right: set[int] = set()
    triplet_total = len(head_files)

    for head_idx, head in enumerate(head_files):
        progress_bar(head_idx, triplet_total, "Assembling sets",
                     f"{len(rows)} matched")

        if head_idx not in head_left or head_idx not in head_right:
            continue
        left_idx = head_left[head_idx]["other_idx"]
        right_idx = head_right[head_idx]["other_idx"]
        if left_idx in used_left or right_idx in used_right:
            continue

        left = left_files[left_idx]
        right = right_files[right_idx]
        lr_total, lr_offset, _, _, lr_best, lr_median, lr_hits = combined_score(left, right)
        hl = head_left[head_idx]
        hr = head_right[head_idx]

        if lr_best is not None and lr_best < MIN_LR_SCORE:
            rejected_lr += 1
            continue

        pairwise_hits = [hl["hits"], hr["hits"]]
        if lr_hits > 0:
            pairwise_hits.append(lr_hits)
        min_hits = min(pairwise_hits) if pairwise_hits else 0

        avg_total = float(np.mean([
            hl["total"], hr["total"],
            lr_total if lr_total is not None else 0.0,
        ]))
        avg_audio = float(np.mean([
            hl["audio_score"], hr["audio_score"],
            lr_best if lr_best is not None else 0.0,
        ]))

        if avg_total < MIN_TRIPLET_AVG:
            rejected_weak += 1
            continue

        conf = confidence_label(avg_total, avg_audio, min_hits)
        used_head.add(head_idx)
        used_left.add(left_idx)
        used_right.add(right_idx)

        rows.append({
            "set_id": f"SET_{len(rows)+1:03d}",
            "confidence": conf,
            "head_file": head["relpath"],
            "left_file": left["relpath"],
            "right_file": right["relpath"],
            "head_duration_sec": round(head["duration"], 2),
            "left_duration_sec": round(left["duration"], 2),
            "right_duration_sec": round(right["duration"], 2),
            "head_size_mb": round(head["size"] / (1024**2), 2),
            "left_size_mb": round(left["size"] / (1024**2), 2),
            "right_size_mb": round(right["size"] / (1024**2), 2),
            "hl_audio": round(hl["audio_score"], 4),
            "hr_audio": round(hr["audio_score"], 4),
            "lr_audio": round(lr_best, 4) if lr_best is not None else "N/A",
            "avg_total_score": round(avg_total, 4),
            "avg_audio_score": round(avg_audio, 4),
            "min_hits": min_hits,
        })

    progress_done(f"Assembled {len(rows)} matched triplet(s)")

    if rejected_lr:
        print(f"    Rejected {rejected_lr} triplet(s): LEFT-RIGHT cross-validation failed")
    if rejected_weak:
        print(f"    Rejected {rejected_weak} triplet(s): score below minimum threshold")

    unmatched: dict[str, list[str]] = {"HEAD": [], "LEFT": [], "RIGHT": []}
    for idx, f in enumerate(head_files):
        if idx not in used_head:
            unmatched["HEAD"].append(str(f["path"]))
    for idx, f in enumerate(left_files):
        if idx not in used_left:
            unmatched["LEFT"].append(str(f["path"]))
    for idx, f in enumerate(right_files):
        if idx not in used_right:
            unmatched["RIGHT"].append(str(f["path"]))

    n_unmatched = sum(len(v) for v in unmatched.values())

    rows.sort(key=lambda x: x["avg_total_score"], reverse=True)

    out_txt = root / MATCH_FILE
    _write_match_txt(rows, unmatched, out_txt, root, camera_dirs)

    high = sum(1 for r in rows if r["confidence"] == "HIGH")
    med = sum(1 for r in rows if r["confidence"] == "MEDIUM")
    low = sum(1 for r in rows if r["confidence"] == "LOW")
    rev = sum(1 for r in rows if r["confidence"] == "REVIEW")

    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print(f"  │  ✓  Matched sets : {len(rows):<31}│")
    print(f"  │     HIGH: {high}   MEDIUM: {med}   LOW: {low}   REVIEW: {rev:<5}│")
    if n_unmatched:
        print(f"  │  ⚠  Unmatched   : {n_unmatched} file(s) had no match     │")
    print(f"  │     Written to  : {MATCH_FILE:<31}│")
    print("  └─────────────────────────────────────────────────┘")
    print()
    return out_txt


# ═══════════════════════════════════════════════════════════════════
#  Disk space checking
# ═══════════════════════════════════════════════════════════════════

def _check_disk_space(dest: Path, needed_bytes: int) -> bool:
    """Return True if there is enough space, False otherwise."""
    try:
        usage = shutil.disk_usage(str(dest) if dest.exists() else str(dest.anchor))
        return usage.free >= needed_bytes
    except OSError:
        return True


# ═══════════════════════════════════════════════════════════════════
#  Package progress tracking (crash/disconnect recovery)
# ═══════════════════════════════════════════════════════════════════

def _save_progress(progress_path: Path, completed: list[str]):
    progress_path.write_text("\n".join(completed) + "\n", encoding="utf-8")


def _load_progress(progress_path: Path) -> set[str]:
    if not progress_path.exists():
        return set()
    text = progress_path.read_text(encoding="utf-8").strip()
    if not text:
        return set()
    return set(text.splitlines())


# ═══════════════════════════════════════════════════════════════════
#  run_package  —  3 modes with space check + crash recovery
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
    print("  │     Copies files + match file to another SSD    │")
    print("  │     and creates the folder structure there      │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    return ask_choice("    Choose [1/2/3]: ", ["1", "2", "3"])


def run_package(root: Path, match_path: Path | None = None,
                mode: str | None = None,
                dest_path: Path | None = None) -> Path:
    camera_dirs = _find_camera_dirs(root)
    if not camera_dirs:
        raise FileNotFoundError(
            "Missing HEAD/LEFT/RIGHT under root. "
            f"Resolved root: {root}"
        )

    txt_file = match_path if match_path else root / MATCH_FILE
    if not txt_file.exists():
        raise FileNotFoundError(f"Missing match file: {txt_file}. Run a full scan first.")

    if mode is None:
        mode = _package_menu()

    if mode == "3" and dest_path is None:
        dest_path = _prompt_for_destination_drive()

    if mode == "3":
        upload_dir = dest_path  # type: ignore[assignment]
    else:
        upload_dir = root / "UPLOAD_READY"

    upload_dir.mkdir(parents=True, exist_ok=True)

    rows = _parse_match_txt(txt_file)

    file_ops: list[tuple[Path, Path, str]] = []
    for row in rows:
        set_id = row["set_id"]
        for key, cam in [("head_full", "HEAD"), ("left_full", "LEFT"), ("right_full", "RIGHT")]:
            full_path_str = row.get(key, "")
            if not full_path_str:
                continue
            src = Path(full_path_str)
            if src.exists():
                dst = upload_dir / f"{set_id}_{cam}{src.suffix.lower()}"
                tag = f"{set_id}_{cam}"
                file_ops.append((src, dst, tag))

    total = len(file_ops)
    if total == 0:
        print("    No files to package.")
        return upload_dir

    total_bytes = sum(s.stat().st_size for s, _, _ in file_ops if s.exists())

    if mode != "2":
        if not _check_disk_space(upload_dir, total_bytes):
            free = shutil.disk_usage(str(upload_dir) if upload_dir.exists()
                                     else str(upload_dir.anchor)).free
            print()
            print("  ┌─────────────────────────────────────────────────┐")
            print("  │  ⚠  NOT ENOUGH DISK SPACE                      │")
            print(f"  │     Need:      {format_size(total_bytes):<36}│")
            print(f"  │     Available:  {format_size(free):<36}│")
            print("  │                                                 │")
            print("  │  Options:                                       │")
            print("  │   - Free up space and re-run                    │")
            print("  │   - Use mode 2 (move) to avoid doubling         │")
            print("  │   - Use mode 3 (transfer) to a bigger drive     │")
            print("  └─────────────────────────────────────────────────┘")
            print()
            yn = ask_choice("    Continue anyway? (y/n): ", ["y", "n", "Y", "N"])
            if yn.lower() != "y":
                print("    Aborted. Re-run when ready.")
                return upload_dir

    progress_path = upload_dir / PROGRESS_FILE
    already_done = _load_progress(progress_path)
    skipped = 0

    verb = "Moving" if mode == "2" else "Copying" if mode == "1" else "Transferring"
    t0 = time.time()
    completed_tags: list[str] = list(already_done)

    for i, (src, dst, tag) in enumerate(file_ops):
        if tag in already_done:
            skipped += 1
            continue

        extra = f"{i+1}/{total}  {format_size(src.stat().st_size)}"
        progress_bar(i, total, f"{verb} files", extra)

        try:
            if mode == "2":
                shutil.move(str(src), str(dst))
            else:
                shutil.copy2(src, dst)
            completed_tags.append(tag)
            _save_progress(progress_path, completed_tags)
        except OSError as exc:
            print(f"\n\n    ⚠  Error on file: {src.name}")
            print(f"       {exc}")
            print()
            print("    The drive may have been disconnected or run out of space.")
            print(f"    Progress saved — {len(completed_tags)} of {total} files done.")
            print("    Re-run packaging to resume from where it stopped.")
            print()
            return upload_dir

    progress_done(f"{verb} complete — {total} files ({format_size(total_bytes)}, {elapsed_str(time.time() - t0)})")

    if skipped:
        print(f"    ({skipped} files already done from previous run)")

    if mode == "3":
        dest_txt = upload_dir / MATCH_FILE
        shutil.copy2(txt_file, dest_txt)
        print(f"    Match file copied to: {dest_txt}")

    if progress_path.exists():
        progress_path.unlink()

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

    txt_exists = (root / MATCH_FILE).exists()
    resume_exists = False
    if txt_exists:
        upload_dir = root / "UPLOAD_READY"
        resume_exists = (upload_dir / PROGRESS_FILE).exists()

    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  What would you like to do?                     │")
    print("  │                                                 │")
    print("  │  1) Full scan + match + package                 │")
    print("  │     Scans HEAD/LEFT/RIGHT, matches audio,       │")
    print("  │     then packages files                         │")
    print("  │                                                 │")
    if txt_exists:
        print("  │  2) Package only (match file exists)            │")
        print("  │     Skip scanning — use existing match file     │")
        print("  │     to copy / move / transfer matched files     │")
        print("  │                                                 │")
        print("  │  3) Re-scan only (regenerate match file)        │")
        print("  │     Run the audio scan again without packaging  │")
        print("  │                                                 │")
        if resume_exists:
            print("  │  4) Resume packaging                            │")
            print("  │     Continue a previous copy/transfer that      │")
            print("  │     was interrupted                             │")
            print("  │                                                 │")
    else:
        print("  │  2) Scan only (generate match file first)       │")
        print("  │     Run the audio scan without packaging        │")
        print("  │                                                 │")
    print("  │  0) Exit                                        │")
    print("  └─────────────────────────────────────────────────┘")
    print()

    valid = ["0", "1", "2"]
    if txt_exists:
        valid.append("3")
    if resume_exists:
        valid.append("4")
    choice = ask_choice(f"    Choose [{'/'.join(valid)}]: ", valid)

    if choice == "0":
        print("    Goodbye!")
        return

    t_global = time.time()

    if choice == "1":
        match_out = run_match(root)
        run_package(root, match_out)
    elif choice == "2" and txt_exists:
        run_package(root)
    elif choice == "2" and not txt_exists:
        run_match(root)
    elif choice == "3":
        run_match(root)
    elif choice == "4":
        run_package(root)

    print(f"    Total time: {elapsed_str(time.time() - t_global)}")
    print()


# ═══════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{VERSION} — Tri-Cam Sync Pipeline (Windows)")

    subparsers = parser.add_subparsers(dest="command")

    launch_p = subparsers.add_parser("launch", help="Interactive menu (default)")
    launch_p.add_argument("--root", default=None)

    match_p = subparsers.add_parser("match", help="Generate match file")
    match_p.add_argument("--root", default=None)

    pkg_p = subparsers.add_parser("package", help="Package matched clips")
    pkg_p.add_argument("--root", default=None)
    pkg_p.add_argument("--match-file", default=None)
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
        mf = Path(args.match_file) if args.match_file else None
        dest = Path(args.dest) if args.dest else None
        run_package(root, mf, mode=args.mode, dest_path=dest)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
