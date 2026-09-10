#!/usr/bin/env python3
"""Automated checks on a rendered cut → work/qa_checks.json.

usage: qa_checks.py <project> <video> [--black 0.3] [--silence 2.5] [--tolerance 1.0]

Checks: duration vs voiceover + cards, black intervals, silence in the mix, integrated
loudness and true peak, resolution/fps/pixel format vs the EDL canvas, faststart, and segment
start times vs the shot list.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
from pathlib import Path

from common import dump_json, ffmpeg_bin, load_json, probe, project_paths


def ff_stderr(ff: str, args: list[str]) -> str:
    return subprocess.run([ff, "-hide_banner", "-nostats"] + args, capture_output=True, text=True).stderr


def faststart(path: Path) -> bool:
    with open(path, "rb") as fh:
        pos, size = 0, path.stat().st_size
        while pos + 8 <= size:
            fh.seek(pos)
            head = fh.read(8)
            atom_size, atom = struct.unpack(">I4s", head)
            if atom_size == 1:
                atom_size = struct.unpack(">Q", fh.read(8))[0]
            if atom == b"moov":
                return True
            if atom == b"mdat":
                return False
            if atom_size < 8:
                return False
            pos += atom_size
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("video")
    ap.add_argument("--black", type=float, default=0.3)
    ap.add_argument("--silence", type=float, default=2.5)
    ap.add_argument("--tolerance", type=float, default=1.0)
    args = ap.parse_args()

    p = project_paths(args.project)
    ff = ffmpeg_bin()
    video = Path(args.video) if Path(args.video).is_absolute() else p["root"] / args.video
    info = probe(video)
    checks = []

    def add(name, ok, value, expected="", detail=""):
        checks.append({"name": name, "pass": bool(ok), "value": value, "expected": expected, "detail": detail})

    # duration
    vo_dur, cards = None, 0.0
    tr = p["work"] / "transcript.json"
    if tr.exists():
        vo_dur = load_json(tr).get("duration")
    edl_path = p["work"] / "edl.json"
    edl = load_json(edl_path) if edl_path.exists() else {}
    for it in edl.get("timeline", []):
        if it.get("type") == "card":
            cards += float(it.get("duration", 0))
    vo_start = float(((edl.get("audio") or {}).get("voiceover") or {}).get("start", 0) or 0)
    if vo_dur:
        expected = vo_dur + vo_start + cards
        add("duration", abs((info.get("duration") or 0) - expected) <= args.tolerance,
            info.get("duration"), round(expected, 2), f"voiceover {vo_dur}s + start {vo_start}s + cards {cards}s")
    else:
        add("duration", True, info.get("duration"), "unknown (no transcript.json)", "")

    # canvas
    canvas = edl.get("canvas", {})
    if canvas:
        ok = info.get("width") == canvas.get("width") and info.get("height") == canvas.get("height")
        add("resolution", ok, f"{info.get('width')}x{info.get('height')}", f"{canvas.get('width')}x{canvas.get('height')}")
        add("fps", abs((info.get("fps") or 0) - float(canvas.get("fps", 30))) < 0.05, info.get("fps"), canvas.get("fps"))
    banner = ff_stderr(ff, ["-i", str(video)])
    add("pixel_format", "yuv420p" in banner, "yuv420p" if "yuv420p" in banner else "other", "yuv420p")
    add("faststart", faststart(video), faststart(video), True)
    add("has_audio", info.get("has_audio"), info.get("has_audio"), True)

    # black frames
    err = ff_stderr(ff, ["-i", str(video), "-vf", f"blackdetect=d={args.black}:pix_th=0.10", "-an", "-f", "null", "-"])
    blacks = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]
    fade_in = float(edl.get("fade_in") or 0)
    fade_out = float(edl.get("fade_out") or 0)
    total = info.get("duration") or 0
    bad = [b for b in blacks if not (b[1] <= fade_in + 0.2 or b[0] >= total - fade_out - 0.2)]
    add("black_intervals", not bad, [[round(a, 2), round(b, 2)] for a, b in blacks], "none outside fades",
        f"{len(bad)} outside the opening/closing fades")

    # silence + loudness
    if info.get("has_audio"):
        err = ff_stderr(ff, ["-i", str(video), "-af", f"silencedetect=n=-35dB:d={args.silence}", "-vn", "-f", "null", "-"])
        starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
        ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
        sil = list(zip(starts, ends + [total] * (len(starts) - len(ends))))
        bad = [s for s in sil if s[0] < total - cards - 0.5]
        add("silence", not bad, [[round(a, 2), round(b, 2)] for a, b in sil], "none before the end card", f"{len(bad)} gaps ≥ {args.silence}s")
        err = ff_stderr(ff, ["-i", str(video), "-af", "loudnorm=print_format=json", "-vn", "-f", "null", "-"])
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
        if m:
            d = json.loads(m.group(0))
            lufs, tp = float(d["input_i"]), float(d["input_tp"])
            add("loudness_lufs", -18.5 <= lufs <= -13.5, lufs, "-16 ± 2.5", "integrated")
            add("true_peak_dbtp", tp <= -1.0, tp, "≤ -1.0", "")
    # segment starts vs shot list
    rep = p["work"] / "render" / "timeline_report.json"
    sl = p["work"] / "shotlist.json"
    if rep.exists() and sl.exists():
        shots = {s["id"]: s for s in load_json(sl).get("shots", [])}
        drift = []
        for it in load_json(rep).get("items", []):
            s = shots.get(it["id"])
            if s and abs(float(s["start"]) - float(it["start"])) > 0.25:
                drift.append(f"{it['id']}: edl {it['start']} vs shotlist {s['start']}")
        add("segment_starts", not drift, drift, "within 0.25s of shotlist", "")

    out = {"video": str(video), "all_pass": all(c["pass"] for c in checks), "checks": checks}
    dump_json(p["work"] / "qa_checks.json", out)
    for c in checks:
        mark = "PASS" if c["pass"] else "FAIL"
        print(f"  {mark} {c['name']:18} {c['value']!s:40.40} expected {c['expected']}  {c['detail']}")
    print("all_pass:", out["all_pass"])


if __name__ == "__main__":
    main()
