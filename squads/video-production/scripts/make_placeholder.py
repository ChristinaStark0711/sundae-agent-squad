#!/usr/bin/env python3
"""Dry-run stand-ins for generated b-roll: one labeled clip per shot in a b-roll plan, zero credits.

usage: make_placeholder.py <project> --plan work/broll_plan.json --out-dir work/broll [--results work/broll_results.json]

Lets the whole pipeline (edit, captions, QA, batch report) run before any money is spent.
Each clip shows the shot id and the start of its prompt on a colored background with a slow
zoom, at the plan's duration and aspect ratio. Writes a broll_results.json with
status "placeholder" and credits 0 so the editor and QA can proceed.
"""
from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path

from common import dump_json, ffmpeg_bin, load_json, project_paths, run

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def size_for(aspect: str) -> tuple[int, int]:
    return {"9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350), "21:9": (2520, 1080)}.get(aspect, (1920, 1080))


def label_png(text: str, w: int, h: int, out: Path) -> Path | None:
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception:
        return None
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = int(h * 0.035)
    font = next((ImageFont.truetype(f, size) for f in FONT_CANDIDATES if Path(f).exists()), ImageFont.load_default())
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=font) > w * 0.8:
            lines.append(cur); cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    y = h * 0.4
    for ln in lines[:8]:
        tw = d.textlength(ln, font=font)
        d.text(((w - tw) / 2, y), ln, font=font, fill=(255, 255, 255, 230))
        y += size * 1.35
    img.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--plan", default="work/broll_plan.json")
    ap.add_argument("--out-dir", default="work/broll")
    ap.add_argument("--results", default=None, help="default: <plan dir>/broll_results.json")
    args = ap.parse_args()
    p = project_paths(args.project)
    ff = ffmpeg_bin()
    plan = load_json(p["root"] / args.plan)
    out_dir = p["root"] / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for shot in plan.get("shots", []):
        params = shot.get("params", {})
        dur = float(params.get("duration") or shot.get("duration") or 5)
        aspect = params.get("aspectRatio") or params.get("aspect_ratio") or "16:9"
        w, h = size_for(aspect)
        color = "0x" + hashlib.md5(shot["id"].encode()).hexdigest()[:6]
        out = out_dir / f"{shot['id']}_v1.mp4"
        label = label_png(f"PLACEHOLDER {shot['id']}\n{(params.get('prompt') or '')[:140]}", w, h, out_dir / f"{shot['id']}_label.png")
        frames = int(dur * 30)
        inputs = ["-f", "lavfi", "-i", f"color=c={color}:s={w}x{h}:r=30:d={dur:.3f}"]
        chain = f"[0:v]zoompan=z='1+0.08*on/{max(frames-1,1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps=30[bg]"
        if label:
            inputs += ["-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", str(label)]
            chain += f";[bg][1:v]overlay=0:0:shortest=1[v]"
        else:
            chain += ";[bg]null[v]"
        run([ff, "-hide_banner", "-loglevel", "error", "-y"] + inputs + ["-filter_complex", chain, "-map", "[v]", "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(out)])
        results.append({"id": shot["id"], "platform": shot.get("platform"), "model": shot.get("model"), "mode": shot.get("mode"),
                        "job_id": None, "status": "placeholder", "file": str(out.relative_to(p["root"])), "duration": dur,
                        "width": w, "height": h, "credits": 0, "credits_source": "dry-run", "retries": 0, "rejections": [], "result_url": None})
        print(f"  {shot['id']}: {dur}s {w}x{h} → {out.relative_to(p['root'])}")
    res_path = p["root"] / (args.results or str(Path(args.plan).parent / "broll_results.json"))
    dump_json(res_path, {"meta": {"slug": p["root"].name, "dry_run": True, "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                         "shots": results, "totals": {"openart": 0, "higgsfield": 0, "all": 0, "plan": plan.get("totals", {}).get("all", 0)}})
    print(f"{len(results)} placeholder clips; results → {res_path.relative_to(p['root'])} (credits 0)")


if __name__ == "__main__":
    main()
