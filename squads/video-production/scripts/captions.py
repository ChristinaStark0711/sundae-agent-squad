#!/usr/bin/env python3
"""Build burned-in caption subtitles (ASS) from work/transcript.json.

usage: captions.py <project> [--transcript work/transcript.json] [--out work/captions.ass] [--style reels|clean|minimal]
                   [--max-words 4] [--max-chars 24] [--position 0.70] [--font "Liberation Sans"]
                   [--size 0.042] [--uppercase] [--highlight] [--color #FFFFFF] [--accent #FFD400]
                   [--width 1080 --height 1920]

Chunks the word timestamps into short phrases (breaks on sentence ends, pauses > 0.6 s,
max words / chars), positions them at `--position` (fraction of height from the top, 0.70
sits in the safe zone above TikTok/Reels UI), and writes an ASS file the assembler burns in
with the `ass` filter (`"captions": {"ass": "work/captions.ass"}` in the EDL).

--highlight emits one event per word so the spoken word is shown in the accent color.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import load_json, project_paths

STYLES = {
    # font size as fraction of height, outline px @1080 wide, shadow, bold, uppercase default
    "reels":   {"size": 0.042, "outline": 5, "shadow": 2, "bold": -1, "upper": True,  "back": False},
    "clean":   {"size": 0.036, "outline": 3, "shadow": 0, "bold": -1, "upper": False, "back": False},
    "minimal": {"size": 0.032, "outline": 0, "shadow": 0, "bold": 0,  "upper": False, "back": True},
}


def ass_color(hex_color: str, alpha: int = 0) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


def ts(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def chunk_words(segments: list[dict], max_words: int, max_chars: int, pause: float = 0.6) -> list[dict]:
    chunks: list[dict] = []
    for seg in segments:
        words = seg.get("words") or []
        if not words:
            # no word timing: split the segment text evenly
            text_words = seg["text"].split()
            n = len(text_words)
            if not n:
                continue
            span = (seg["end"] - seg["start"]) / n
            words = [{"w": w, "start": seg["start"] + i * span, "end": seg["start"] + (i + 1) * span} for i, w in enumerate(text_words)]
        cur: list[dict] = []
        for w in words:
            token = w["w"].strip()
            if not token:
                continue
            if cur:
                gap = w["start"] - cur[-1]["end"]
                text_len = len(" ".join(x["w"] for x in cur)) + 1 + len(token)
                ends_sentence = bool(re.search(r"[.!?]$", cur[-1]["w"]))
                if len(cur) >= max_words or text_len > max_chars or gap > pause or ends_sentence:
                    chunks.append({"words": cur})
                    cur = []
            cur.append({"w": token, "start": float(w["start"]), "end": float(w["end"])})
        if cur:
            chunks.append({"words": cur})
    for c in chunks:
        c["start"] = c["words"][0]["start"]
        c["end"] = c["words"][-1]["end"]
        c["text"] = " ".join(x["w"] for x in c["words"])
    # close small gaps so captions don't flicker; keep a minimum on-screen time
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1]["start"] if i + 1 < len(chunks) else None
        min_end = c["start"] + 0.7
        c["end"] = max(c["end"], min(min_end, nxt) if nxt else min_end)
        if nxt is not None and nxt - c["end"] < 0.25:
            c["end"] = nxt
    return chunks


def build_ass(chunks: list[dict], a) -> str:
    st = STYLES[a.style]
    size = int(a.height * (a.size or st["size"]))
    outline = round(st["outline"] * a.width / 1080, 1)
    shadow = round(st["shadow"] * a.width / 1080, 1)
    margin_v = int(a.height * (1 - a.position))  # distance from bottom for alignment 2
    margin_lr = int(a.width * 0.08)
    primary = ass_color(a.color)
    accent = ass_color(a.accent)
    back = ass_color("#000000", 0x60) if st["back"] else ass_color("#000000", 0x00)
    border_style = 3 if st["back"] else 1
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {a.width}
PlayResY: {a.height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{a.font},{size},{primary},{accent},&H00000000,{back},{st['bold']},0,0,0,100,100,0.5,0,{border_style},{outline},{shadow},2,{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    upper = a.uppercase or (st["upper"] and not a.no_uppercase)
    lines = []
    for c in chunks:
        if a.highlight:
            words = c["words"]
            for i, w in enumerate(words):
                start = w["start"] if i > 0 else c["start"]
                end = words[i + 1]["start"] if i + 1 < len(words) else c["end"]
                if end <= start:
                    continue
                parts = []
                for j, x in enumerate(words):
                    t = x["w"].upper() if upper else x["w"]
                    parts.append(f"{{\\c{accent}}}{t}{{\\c{primary}}}" if j == i else t)
                lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{' '.join(parts)}")
        else:
            t = c["text"].upper() if upper else c["text"]
            lines.append(f"Dialogue: 0,{ts(c['start'])},{ts(c['end'])},Cap,,0,0,0,,{t}")
    return header + "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out", default="work/captions.ass")
    ap.add_argument("--style", default="reels", choices=list(STYLES))
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--max-chars", type=int, default=24)
    ap.add_argument("--position", type=float, default=0.70, help="caption baseline as a fraction of height from the top")
    ap.add_argument("--font", default="Liberation Sans")
    ap.add_argument("--size", type=float, default=None, help="font size as a fraction of height (default per style)")
    ap.add_argument("--uppercase", action="store_true")
    ap.add_argument("--no-uppercase", action="store_true")
    ap.add_argument("--highlight", action="store_true", help="color the spoken word")
    ap.add_argument("--color", default="#FFFFFF")
    ap.add_argument("--accent", default="#FFD400")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--offset", type=float, default=0.0, help="seconds to add to every timestamp (voiceover start in the EDL)")
    ap.add_argument("--transcript", default="work/transcript.json", help="transcript path relative to the project")
    a = ap.parse_args()

    p = project_paths(a.project)
    tr = load_json(p["root"] / a.transcript)
    if tr.get("engine") in (None, "none") or not tr.get("segments"):
        sys.exit("transcript.json has no segments; run transcribe.py first")
    if tr.get("engine") == "estimated":
        print("! transcript timings are estimated from the script; captions will be roughly aligned", file=sys.stderr)
    segs = tr["segments"]
    if a.offset:
        for s in segs:
            s["start"] += a.offset; s["end"] += a.offset
            for w in s.get("words") or []:
                w["start"] += a.offset; w["end"] += a.offset
    chunks = chunk_words(segs, a.max_words, a.max_chars)
    out = p["root"] / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_ass(chunks, a), encoding="utf-8")
    print(f"{out.relative_to(p['root'])}: {len(chunks)} captions, style={a.style}, highlight={a.highlight}, position={a.position}")
    for c in chunks[:6]:
        print(f"  {c['start']:6.2f}-{c['end']:6.2f}  {c['text']}")
    if len(chunks) > 6:
        print("  ...")


if __name__ == "__main__":
    main()
