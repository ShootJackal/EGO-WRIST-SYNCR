#!/usr/bin/env python3
"""Tri-cam matching + packaging pipeline.

Auto-detection looks for:
- <drive>:\\NOT UPLOADED\\HEAD
- <drive>:\\NOT UPLOADED\\LEFT
- <drive>:\\NOT UPLOADED\\RIGHT

Commands:
  match   -> create matched_triplets.csv
  package -> create UPLOAD_READY folder from matched_triplets.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import string
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

EXTENSIONS = {".mov", ".mp4", ".mxf", ".avi"}
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

DURATION_TOL_SEC = 75
MAX_SIZE_RATIO = 1.8
AUDIO_SR = 8000
SAMPLE_SECONDS = 20
HOP_MS = 100
MAX_SHIFT_SEC = 25
MIN_AUDIO_SCORE = 0.18


def _find_camera_dirs(root: Path) -> dict[str, Path] | None:
    """Return HEAD/LEFT/RIGHT directories under root (case-insensitive)."""
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


def resolve_root(root_arg: str | None = None) -> Path:
    """Resolve project root across any plugged-in SSD.

    Priority:
    1) explicit --root
    2) TRI_CAM_ROOT env var
    3) first existing <drive>:/NOT UPLOADED with HEAD/LEFT/RIGHT
    4) D:/NOT UPLOADED fallback
    """
    if root_arg:
        return Path(root_arg).expanduser()

    env_root = os.environ.get("TRI_CAM_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser()

    if os.name == "nt":
        candidates: list[Path] = []
        for drive in string.ascii_uppercase:
            drive_root = Path(f"{drive}:/")
            if not drive_root.exists():
                continue
            candidate = drive_root / "NOT UPLOADED"
            if _find_camera_dirs(candidate):
                candidates.append(candidate)
        if candidates:
            return sorted(candidates, key=lambda p: str(p).lower())[0]

    # Legacy fallback for older workflows.
    return Path(r"D:\NOT UPLOADED")


def run_cmd(cmd: list[str]) -> bytes:
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL)


def ffprobe_info(path: Path) -> tuple[float, int]:
    cmd = [
        FFPROBE,
        "-v",
        "error",
        "-show_entries",
        "format=duration,size",
        "-of",
        "json",
        str(path),
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
        FFMPEG,
        "-v",
        "error",
        "-ss",
        str(start_sec),
        "-i",
        path_str,
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(AUDIO_SR),
        "-t",
        str(SAMPLE_SECONDS),
        "-f",
        "s16le",
        "-",
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
    small = min(s1, s2)
    big = max(s1, s2)
    if small <= 0:
        return 0.0
    ratio = big / small
    if ratio > MAX_SIZE_RATIO:
        return 0.0
    return max(0.0, 1.0 - (ratio - 1.0) / (MAX_SIZE_RATIO - 1.0))


def candidate_ok(a: dict, b: dict) -> bool:
    if abs(a["duration"] - b["duration"]) > DURATION_TOL_SEC:
        return False

    small = min(a["size"], b["size"])
    big = max(a["size"], b["size"])
    if small <= 0:
        return False

    ratio = big / small
    return ratio <= MAX_SIZE_RATIO


def choose_sample_starts(d1: float, d2: float) -> list[int]:
    m = min(d1, d2)

    starts = [0]
    if m > SAMPLE_SECONDS * 3:
        starts.append(int(max(0, (m / 2) - (SAMPLE_SECONDS / 2))))
    if m > SAMPLE_SECONDS * 5:
        starts.append(int(max(0, m - SAMPLE_SECONDS - 10)))

    seen = set()
    final = []
    for s in starts:
        if s not in seen:
            final.append(s)
            seen.add(s)
    return final


def audio_match_score(a: dict, b: dict):
    starts = choose_sample_starts(a["duration"], b["duration"])
    best_score = None
    best_offset = None

    for start_sec in starts:
        env_a = extract_env(str(a["path"]), start_sec)
        env_b = extract_env(str(b["path"]), start_sec)
        score, offset = corr_score(env_a, env_b)

        if score is None:
            continue

        if (best_score is None) or (score > best_score):
            best_score = score
            best_offset = offset

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


def scan_folder(folder: Path, label: str) -> list[dict]:
    files = []
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.suffix.lower() in EXTENSIONS:
            try:
                duration, size = ffprobe_info(p)
            except Exception:
                continue

            files.append(
                {
                    "camera": label,
                    "path": p,
                    "name": p.name,
                    "relpath": str(p.relative_to(folder)),
                    "duration": duration,
                    "size": size,
                }
            )
    return files


def greedy_match(anchor_files: list[dict], other_files: list[dict]) -> dict[int, dict]:
    candidates = []
    for i, a in enumerate(anchor_files):
        for j, b in enumerate(other_files):
            if not candidate_ok(a, b):
                continue

            total, offset, ds, ss, audio_score = combined_score(a, b)
            if total is None or audio_score is None:
                continue

            if audio_score < MIN_AUDIO_SCORE:
                continue

            candidates.append(
                {
                    "anchor_idx": i,
                    "other_idx": j,
                    "total": total,
                    "audio_score": audio_score,
                    "offset": offset,
                    "duration_sim": ds,
                    "size_sim": ss,
                }
            )

    candidates.sort(key=lambda x: x["total"], reverse=True)

    used_anchor = set()
    used_other = set()
    matches = {}

    for c in candidates:
        i = c["anchor_idx"]
        j = c["other_idx"]
        if i in used_anchor or j in used_other:
            continue

        matches[i] = c
        used_anchor.add(i)
        used_other.add(j)

    return matches


def run_match(root: Path) -> Path:
    camera_dirs = _find_camera_dirs(root)
    if not camera_dirs:
        raise FileNotFoundError(
            "Missing required folders under root. Expected NOT UPLOADED/HEAD, LEFT, RIGHT. "
            f"Resolved root: {root}"
        )
    head_dir = camera_dirs["HEAD"]
    left_dir = camera_dirs["LEFT"]
    right_dir = camera_dirs["RIGHT"]

    print("Scanning folders...")
    head_files = scan_folder(head_dir, "HEAD")
    left_files = scan_folder(left_dir, "LEFT")
    right_files = scan_folder(right_dir, "RIGHT")

    print(f"HEAD files : {len(head_files)}")
    print(f"LEFT files : {len(left_files)}")
    print(f"RIGHT files: {len(right_files)}")

    print("Matching HEAD -> LEFT...")
    head_left = greedy_match(head_files, left_files)

    print("Matching HEAD -> RIGHT...")
    head_right = greedy_match(head_files, right_files)

    rows = []
    used_left = set()
    used_right = set()

    for head_idx, head in enumerate(head_files):
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

        avg_total = float(np.mean([hl["total"], hr["total"], lr_total if lr_total is not None else 0.0]))
        avg_audio = float(np.mean([hl["audio_score"], hr["audio_score"], lr_audio if lr_audio is not None else 0.0]))

        rows.append(
            {
                "set_id": f"SET_{len(rows)+1:03d}",
                "confidence": confidence_label(avg_total, avg_audio),
                "head_file": head["relpath"],
                "left_file": left["relpath"],
                "right_file": right["relpath"],
                "head_duration_sec": round(head["duration"], 2),
                "left_duration_sec": round(left["duration"], 2),
                "right_duration_sec": round(right["duration"], 2),
                "head_size_mb": round(head["size"] / (1024 * 1024), 2),
                "left_size_mb": round(left["size"] / (1024 * 1024), 2),
                "right_size_mb": round(right["size"] / (1024 * 1024), 2),
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
            }
        )

        used_left.add(left_idx)
        used_right.add(right_idx)

    rows.sort(key=lambda x: x["avg_total_score"], reverse=True)

    out_csv = root / "matched_triplets.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "set_id",
            "confidence",
            "head_file",
            "left_file",
            "right_file",
            "head_duration_sec",
            "left_duration_sec",
            "right_duration_sec",
            "head_size_mb",
            "left_size_mb",
            "right_size_mb",
            "head_left_audio_score",
            "head_right_audio_score",
            "left_right_audio_score",
            "left_offset_vs_head_sec",
            "right_offset_vs_head_sec",
            "right_offset_vs_left_sec",
            "head_left_total",
            "head_right_total",
            "left_right_total",
            "avg_total_score",
            "avg_audio_score",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\nDone.")
    print(f"Matched sets: {len(rows)}")
    print(f"CSV written to: {out_csv}")
    return out_csv


def run_package(root: Path, csv_path: Path | None = None) -> Path:
    camera_dirs = _find_camera_dirs(root)
    if not camera_dirs:
        raise FileNotFoundError(
            "Missing required folders under root. Expected NOT UPLOADED/HEAD, LEFT, RIGHT. "
            f"Resolved root: {root}"
        )

    csv_file = csv_path if csv_path else root / "matched_triplets.csv"
    if not csv_file.exists():
        raise FileNotFoundError(f"Missing CSV: {csv_file}. Run 'match' first.")

    upload_dir = root / "UPLOAD_READY"
    upload_dir.mkdir(parents=True, exist_ok=True)

    with csv_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    copied = 0
    for row in rows:
        set_id = row["set_id"]
        mappings = [
            (camera_dirs["HEAD"] / row["head_file"], "HEAD"),
            (camera_dirs["LEFT"] / row["left_file"], "LEFT"),
            (camera_dirs["RIGHT"] / row["right_file"], "RIGHT"),
        ]

        for src, cam in mappings:
            if not src.exists():
                continue
            dst = upload_dir / f"{set_id}_{cam}{src.suffix.lower()}"
            shutil.copy2(src, dst)
            copied += 1

    print(f"Copied files: {copied}")
    print(f"Output folder: {upload_dir}")
    return upload_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tri-cam sync pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    match_parser = subparsers.add_parser("match", help="Generate matched_triplets.csv")
    match_parser.add_argument("--root", default=None, help="Root folder containing HEAD/LEFT/RIGHT")

    package_parser = subparsers.add_parser("package", help="Copy matched clips into UPLOAD_READY")
    package_parser.add_argument("--root", default=None, help="Root folder containing HEAD/LEFT/RIGHT")
    package_parser.add_argument("--csv", default=None, help="Optional path to matched_triplets.csv")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    print(f"Using root: {root}")

    if args.command == "match":
        run_match(root)
        return 0

    if args.command == "package":
        csv_path = Path(args.csv) if args.csv else None
        run_package(root, csv_path)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
