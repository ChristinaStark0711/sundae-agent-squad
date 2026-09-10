#!/usr/bin/env python3
"""Thumbnail grid of a video for reviewing.

usage: contact_sheet.py <video> [--out path] [--interval 2] [--cols 6] [--width 320]

Cells are row-major; cell k (0-based) is at t = k * interval seconds. The script prints the
mapping so a reviewer can name timestamps from the grid.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from common import ffmpeg_bin, probe, run


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--interval", type=float, default=2.0)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--width", type=int, default=320)
    args = ap.parse_args()

    src = Path(args.video)
    info = probe(src)
    dur = info.get("duration") or 0
    n = max(1, math.ceil(dur / args.interval))
    rows = max(1, math.ceil(n / args.cols))
    out = Path(args.out) if args.out else src.with_name(src.stem + "_sheet.jpg")
    vf = f"fps=1/{args.interval},scale={args.width}:-2,tile={args.cols}x{rows}:padding=4:margin=4:color=0x202020"
    run([ffmpeg_bin(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-vf", vf, "-frames:v", "1", "-q:v", "3", str(out)])
    print(f"{out}: {n} frames, {args.cols}x{rows}, one every {args.interval}s, {dur:.1f}s total")
    print("cell → time: row r, col c → t = (r*%d + c) * %gs" % (args.cols, args.interval))
    for r in range(rows):
        t0 = r * args.cols * args.interval
        print(f"  row {r}: {t0:6.1f}s … {min(t0 + (args.cols - 1) * args.interval, dur):6.1f}s")


if __name__ == "__main__":
    main()
