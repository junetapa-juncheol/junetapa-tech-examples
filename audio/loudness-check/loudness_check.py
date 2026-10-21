"""Measure loudness, true peak, clipping and leading silence for every track in a folder.

Uses ffmpeg / ffprobe only. Audio files are read, never modified.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

AUDIO_EXT = {".wav", ".flac", ".mp3", ".m4a", ".aif", ".aiff", ".ogg"}

# Spotify for Artists, "Loudness normalization"
TARGET_LUFS = -14.0
TP_LIMIT = -1.0         # keep true peak below -1 dBTP
TP_LIMIT_LOUD = -2.0    # ... or below -2 dBTP if the master is louder than -14 LUFS

SILENCE_DB = -50
MAX_HEAD_SILENCE = 2.0


def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out) if out else 0.0


def number(pattern, text):
    m = re.search(pattern, text, re.S)
    if not m or m.group(1) in ("-inf", "inf", "nan"):
        return None
    return float(m.group(1))


def analyze(path):
    # one pass: ebur128 for loudness, astats for peaks, silencedetect for the intro
    filters = (
        "ebur128=peak=true:framelog=verbose,"
        "astats=measure_perchannel=none,"
        f"silencedetect=noise={SILENCE_DB}dB:d=0.1"
    )
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", filters, "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr

    summary = log[log.rfind("Summary:"):]
    overall = log[log.rfind("Overall"):] if "Overall" in log else ""

    head = 0.0
    m = re.search(r"silence_start: (-?[\d.e-]+)", log)
    if m and float(m.group(1)) <= 0.01:
        end = re.search(r"silence_end: ([\d.]+)", log)
        head = float(end.group(1)) if end else ffprobe_duration(path)

    peak_db = number(r"Peak level dB:\s*(-?[\d.]+|-?inf)", overall)
    peak_count = number(r"Peak count:\s*([\d.]+)", overall)
    # astats "Peak count" only means clipping when the peak sits at 0 dBFS
    clipped = int(peak_count) if peak_db is not None and peak_db >= -0.01 and peak_count else 0

    return {
        "file": path.name,
        "duration": round(ffprobe_duration(path), 2),
        "lufs": number(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", summary),
        "lra": number(r"LRA:\s*(-?[\d.]+)\s*LU\b", summary),
        "true_peak": number(r"Peak:\s*(-?[\d.]+|-inf)\s*dBFS", summary),
        "sample_peak": peak_db,
        "clipped": clipped,
        "head_silence": round(head, 2),
    }


def check(row):
    notes = []
    lufs, tp = row["lufs"], row["true_peak"]
    if tp is not None:
        limit = TP_LIMIT_LOUD if lufs is not None and lufs > TARGET_LUFS else TP_LIMIT
        if tp > limit:
            notes.append(f"true peak {tp:+.1f} dBTP > {limit:+.0f}")
    if lufs is not None and lufs > TARGET_LUFS + 3:
        notes.append(f"{lufs:.1f} LUFS, will be turned down")
    if row["clipped"]:
        notes.append(f"{row['clipped']} samples at full scale")
    if row["head_silence"] > MAX_HEAD_SILENCE:
        notes.append(f"{row['head_silence']}s silence at start")
    return notes


def mmss(seconds):
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def to_markdown(rows):
    lines = [
        "| file | length | LUFS | LRA | true peak | clipped | intro silence | notes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        notes = "; ".join(r["notes"]) or "ok"
        lines.append(
            f"| {r['file']} | {mmss(r['duration'])} | {r['lufs']} | {r['lra']} | "
            f"{r['true_peak']} | {r['clipped']} | {r['head_silence']}s | {notes} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Loudness report for a folder of audio files")
    parser.add_argument("folder")
    parser.add_argument("--out", help="also write report.md and report.json here")
    args = parser.parse_args()

    files = sorted(p for p in Path(args.folder).rglob("*") if p.suffix.lower() in AUDIO_EXT)
    if not files:
        print("no audio files found")
        return 1

    rows = []
    for path in files:
        print(f"measuring {path.name}", file=sys.stderr)
        row = analyze(path)
        row["notes"] = check(row)
        rows.append(row)

    table = to_markdown(rows)
    print(table)

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.md").write_text(table + "\n", encoding="utf-8")
        (out / "report.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"\nsaved {out / 'report.md'} and report.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
