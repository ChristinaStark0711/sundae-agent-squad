#!/usr/bin/env python3
"""Voiceover → work/transcript.json with segment and word timestamps.

usage: transcribe.py <project> [--model small] [--script file] [--language en]

Engine order:
  1. faster-whisper (pip install faster-whisper); word_timestamps=True
  2. estimate: the script text (--script file, or `script:` in brief.md) spread over the
     voiceover duration proportionally to word length; engine = "estimated"
  3. none: writes a stub and exits 2 so the producer stops.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import dump_json, load_json, probe, project_paths, read_brief_frontmatter


def find_voiceover(p) -> Path | None:
    assets_json = p["work"] / "assets.json"
    if assets_json.exists():
        for i in load_json(assets_json)["items"]:
            if i["kind"] == "voiceover" and i["media"] in ("audio", "video"):
                return p["root"] / i["path"]
    for f in sorted((p["assets"] / "voiceover").glob("*")):
        if f.is_file() and not f.name.startswith("."):
            return f
    return None


def whisper(path: Path, model_size: str, language: str | None):
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception:
        return None, "faster-whisper not installed"
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(path), word_timestamps=True, language=language, vad_filter=True)
    except Exception as e:  # model download blocked, bad audio, ...
        return None, f"faster-whisper failed: {e}"
    out = []
    for i, s in enumerate(segments):
        words = [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for w in (s.words or [])]
        out.append({"id": f"t{i+1:03}", "start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": words})
    return {"engine": f"faster-whisper/{model_size}", "language": getattr(info, "language", language), "segments": out}, None


def estimate(script: str, duration: float):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", script) if s.strip()]
    if not sentences or not duration:
        return None
    lead, tail = 0.4, 0.6  # breath at start, room at end
    usable = max(duration - lead - tail, 1.0)
    weights = [sum(len(w) + 1 for w in s.split()) for s in sentences]
    total_w = sum(weights)
    t = lead
    segs = []
    for i, (s, w) in enumerate(zip(sentences, weights)):
        d = usable * w / total_w
        words = s.split()
        ww = [len(x) + 1 for x in words]
        wt = t
        wlist = []
        for x, wl in zip(words, ww):
            wd = d * wl / sum(ww)
            wlist.append({"w": x, "start": round(wt, 3), "end": round(wt + wd, 3)})
            wt += wd
        segs.append({"id": f"t{i+1:03}", "start": round(t, 3), "end": round(t + d, 3), "text": s, "words": wlist})
        t += d
    return {"engine": "estimated", "language": None, "segments": segs}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--model", default="small", help="faster-whisper size: tiny, base, small, medium, large-v3")
    ap.add_argument("--script", help="text file with the voiceover script (fallback timing)")
    ap.add_argument("--language", default=None)
    ap.add_argument("--force-estimate", action="store_true")
    args = ap.parse_args()

    p = project_paths(args.project)
    vo = find_voiceover(p)
    if not vo:
        dump_json(p["work"] / "transcript.json", {"engine": "none", "duration": None, "segments": [], "error": "no voiceover file"})
        sys.exit("no voiceover found in assets/voiceover/")
    duration = probe(vo).get("duration")

    result, why = (None, "forced estimate") if args.force_estimate else whisper(vo, args.model, args.language)
    if result is None:
        script = Path(args.script).read_text(encoding="utf-8") if args.script else (read_brief_frontmatter(p["root"]).get("script") or "")
        script = script.strip()
        if script and not script.startswith("(") and duration:
            result = estimate(script, duration)
            result["note"] = f"{why}; timings estimated from script text"
        else:
            dump_json(p["work"] / "transcript.json", {"engine": "none", "duration": duration, "segments": [], "error": why})
            print(f"transcript.json: engine none ({why}); add `script:` to brief.md or install faster-whisper", file=sys.stderr)
            sys.exit(2)

    result["voiceover"] = str(vo.relative_to(p["root"]))
    result["duration"] = duration
    result["word_count"] = sum(len(s["words"]) for s in result["segments"])
    dump_json(p["work"] / "transcript.json", result)
    print(f"transcript.json: engine={result['engine']} duration={duration}s segments={len(result['segments'])} words={result['word_count']}")
    for s in result["segments"][:8]:
        print(f"  {s['start']:6.2f}-{s['end']:6.2f}  {s['text'][:80]}")
    if len(result["segments"]) > 8:
        print("  ...")


if __name__ == "__main__":
    main()
