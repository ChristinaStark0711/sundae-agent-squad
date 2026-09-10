#!/usr/bin/env python3
"""Extract viewing stills and full-res reference frames.

usage: extract_frames.py <project> [--interval 2] [--width 640] [--max 12]
       extract_frames.py --file <clip> [--out dir] [--interval 2]

Project mode: for every footage clip in work/assets.json → work/stills/<stem>/t<sec>.jpg
(small, for viewing) and work/refs/<stem>_mid.png (full res, first/mid/last frames for
image2video references).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import ffmpeg_bin, load_json, probe, project_paths, run


def stills(ff: str, src: Path, out_dir: Path, interval: float, width: int, max_frames: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    info = probe(src)
    dur = info.get("duration") or 0
    times = [round(t, 2) for t in frange(0.0, dur, interval)]
    if len(times) > max_frames:
        step = len(times) / max_frames
        times = [times[int(i * step)] for i in range(max_frames)]
    outs = []
    for t in times:
        out = out_dir / f"t{t:06.1f}.jpg"
        run([ff, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src),
             "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "4", str(out)])
        outs.append(out)
    return outs


def refs(ff: str, src: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    dur = probe(src).get("duration") or 0
    points = {"first": min(0.3, dur), "mid": dur / 2, "last": max(dur - 0.3, 0)}
    outs = []
    for name, t in points.items():
        out = out_dir / f"{src.stem}_{name}.png"
        run([ff, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src),
             "-frames:v", "1", str(out)])
        outs.append(out)
    return outs


def frange(start: float, stop: float, step: float):
    t = start
    while t < stop:
        yield t
        t += step


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--out")
    ap.add_argument("--interval", type=float, default=2.0)
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--max", type=int, default=12)
    args = ap.parse_args()
    ff = ffmpeg_bin()

    if args.file:
        src = Path(args.file)
        out_dir = Path(args.out) if args.out else src.parent / f"{src.stem}_stills"
        outs = stills(ff, src, out_dir, args.interval, args.width, args.max)
        print(f"{len(outs)} stills → {out_dir}")
        return
    if not args.project:
        ap.error("project path or --file required")

    p = project_paths(args.project)
    assets = load_json(p["work"] / "assets.json")
    clips = [i for i in assets["items"] if i["kind"] == "footage" and i["media"] == "video"]
    if not clips:
        print("no footage clips in assets.json")
        return
    for c in clips:
        src = p["root"] / c["path"]
        s = stills(ff, src, p["stills"] / src.stem, args.interval, args.width, args.max)
        r = refs(ff, src, p["refs"])
        print(f"{src.name}: {len(s)} stills → work/stills/{src.stem}/, refs → {', '.join(x.name for x in r)}")


if __name__ == "__main__":
    main()
