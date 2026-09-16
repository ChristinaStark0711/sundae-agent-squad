#!/usr/bin/env python3
"""Assemble a cut from an EDL with ffmpeg.

usage: assemble.py <project> [--edl work/edl.json] [--out output/<slug>_v1.mp4] [--draft] [--validate] [--render-dir work/render]

EDL schema: see squads/video-production/templates/edl.json.

Item types: clip (default; src/in/duration/fit/focus_x/focus_y/speed), image (src/duration/motion/zoom),
card (background/image/text). Top-level "captions": {"ass": "work/captions.ass"} burns subtitles in.

Timeline semantics
- items play back to back in order; `transition` on an item overlaps the previous item, so
  total = sum(duration) - sum(transition.duration)
- `--validate` prints the computed start time of every item and exits without rendering
- overlays and fades use final-timeline seconds; overlay end "card" = start of the first card

Pipeline
1. every item → normalized intermediate (canvas size, fps, yuv420p, silent)
2. one filter graph: concat filter for hard cuts, xfade for transitions, fades, overlays
   → work/render/video_post.mp4 (the master video encode; the graph is saved next to it)
4. voiceover (+ music with ducking) → work/render/mix.wav, two-pass loudnorm
5. mux → out.mp4 (faststart)
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

from common import dump_json, ffmpeg_bin, hex_to_ffmpeg, load_json, probe, project_paths

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


class Job:
    def __init__(self, project: str, edl_path: str, out: str | None, draft: bool, render_dir: str | None = None):
        self.p = project_paths(project)
        self.root = self.p["root"]
        self.ff = ffmpeg_bin()
        self.edl = load_json(self.root / edl_path)
        self.draft = draft
        canvas = self.edl.get("canvas", {})
        self.W = int(canvas.get("width", 1920))
        self.H = int(canvas.get("height", 1080))
        self.fps = float(canvas.get("fps", 30))
        if draft:
            self.W, self.H = (self.W // 2) // 2 * 2, (self.H // 2) // 2 * 2
        self.bg = canvas.get("background") or "#000000"
        self.render = (self.root / render_dir) if render_dir else self.p["render"]
        self.render.mkdir(parents=True, exist_ok=True)
        slug = self.root.name
        default_out = f"output/{slug}_v1{'_draft' if draft else ''}.mp4"
        self.out = self.root / (out or default_out)
        if draft and out and not self.out.stem.endswith("_draft"):
            self.out = self.out.with_name(self.out.stem + "_draft" + self.out.suffix)
        self.warnings: list[str] = []
        self.notes: list[str] = []
        self.items = self.edl.get("timeline", [])
        if not self.items:
            sys.exit("EDL timeline is empty")

    # ---------- planning ----------
    def plan(self) -> dict:
        t = 0.0
        planned = []
        for i, it in enumerate(self.items):
            dur = float(it.get("duration") or 0)
            if dur <= 0:
                sys.exit(f"item {it.get('id', i)} has no positive duration")
            trans = it.get("transition") if i > 0 else None
            if i == 0 and it.get("transition"):
                self.warnings.append(f"{it.get('id')}: transition on the first item ignored")
            td = float(trans.get("duration", 0)) if trans else 0.0
            if trans and (td >= dur or td >= float(self.items[i - 1].get("duration", 0))):
                sys.exit(f"item {it.get('id')}: transition {td}s is not shorter than both neighbours")
            start = t - td
            planned.append({
                "index": i,
                "id": it.get("id", f"item{i:02}"),
                "type": it.get("type", "clip"),
                "src": it.get("src") or (it.get("image") or {}).get("src"),
                "start": round(start, 3),
                "end": round(start + dur, 3),
                "duration": dur,
                "transition_in": td or None,
            })
            t = start + dur
            if it.get("type") != "card":
                if dur < 1.5:
                    self.notes.append(f"{it.get('id')}: {dur}s is under 1.5s")
                if dur > 7:
                    self.notes.append(f"{it.get('id')}: {dur}s is over 7s")
        self.total = round(t, 3)
        cards = [x for x in planned if x["type"] == "card"]
        self.card_start = cards[0]["start"] if cards else None
        self.card_total = round(sum(x["duration"] for x in cards), 3)
        vo = (self.edl.get("audio") or {}).get("voiceover")
        self.vo_duration = None
        if vo and vo.get("src"):
            vo_path = self.root / vo["src"]
            if not vo_path.exists():
                sys.exit(f"voiceover not found: {vo_path}")
            self.vo_duration = probe(vo_path).get("duration")
            expected = (self.vo_duration or 0) + float(vo.get("start", 0)) + self.card_total
            if abs(self.total - expected) > 1.0:
                self.warnings.append(
                    f"video {self.total}s vs voiceover {self.vo_duration}s + cards {self.card_total}s = {expected:.2f}s (diff {self.total-expected:+.2f}s)")
            if (self.vo_duration or 0) + float(vo.get("start", 0)) > self.total + 0.05:
                self.warnings.append("voiceover is longer than the video and will be cut")
        missing = []
        for it in self.items:
            for key in ("src",):
                if it.get(key) and not (self.root / it[key]).exists():
                    missing.append(it[key])
            img = (it.get("image") or {}).get("src")
            if img and not (self.root / img).exists():
                missing.append(img)
        for ov in self.edl.get("overlays", []):
            if ov.get("src") and not (self.root / ov["src"]).exists():
                missing.append(ov["src"])
        if missing:
            sys.exit("missing files:\n  " + "\n  ".join(missing))
        self.planned = planned
        report = {
            "canvas": {"width": self.W, "height": self.H, "fps": self.fps, "draft": self.draft},
            "total_duration": self.total,
            "voiceover_duration": self.vo_duration,
            "card_start": self.card_start,
            "card_total": self.card_total,
            "items": planned,
            "warnings": self.warnings,
            "notes": self.notes,
        }
        dump_json(self.render / "timeline_report.json", report)
        return report

    # ---------- intermediates ----------
    def _enc(self, final: bool = False) -> list[str]:
        if self.draft:
            return ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-pix_fmt", "yuv420p"]
        if final:
            return ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p"]
        return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p"]

    def _fit_filter(self, it: dict) -> str:
        W, H = self.W, self.H
        fit = it.get("fit", "cover")
        pad = hex_to_ffmpeg(it.get("pad_color") or self.bg)
        if fit == "contain":
            return f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={pad}"
        if fit == "blur":
            return (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:4[bg];"
                    f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
        fx = float(it.get("focus_x", 0.5))
        fy = float(it.get("focus_y", 0.5))
        return f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}:(iw-ow)*{fx}:(ih-oh)*{fy}"

    def render_item(self, i: int, it: dict) -> Path:
        out = self.render / f"seg_{i:02}.mp4"
        dur = float(it["duration"])
        if it.get("type") == "card":
            return self.render_card(i, it, out)
        if it.get("type") == "image":
            return self.render_image(i, it, out)
        src = self.root / it["src"]
        speed = float(it.get("speed") or 1.0)
        src_in = float(it.get("in") or 0.0)
        need = dur * speed + 0.25
        vf = [self._fit_filter(it)]
        if speed != 1.0:
            vf.append(f"setpts=PTS/{speed}")
        vf += [f"fps={self.fps}", f"tpad=stop_mode=clone:stop_duration={dur}", "setpts=PTS-STARTPTS", "format=yuv420p", "setsar=1"]
        cmd = [self.ff, "-hide_banner", "-loglevel", "error", "-y",
               "-ss", f"{src_in:.3f}", "-t", f"{need:.3f}", "-i", str(src),
               "-filter_complex", ",".join(vf) if ";" not in vf[0] else vf[0] + "," + ",".join(vf[1:]),
               "-t", f"{dur:.3f}", "-r", str(self.fps), "-an"] + self._enc() + [str(out)]
        self._run(cmd)
        got = probe(out).get("duration") or 0
        if abs(got - dur) > 0.15:
            self.warnings.append(f"{it.get('id')}: rendered {got:.2f}s, wanted {dur:.2f}s (source shorter than in+duration?)")
        return out

    def render_image(self, i: int, it: dict, out: Path) -> Path:
        """A still with a slow Ken Burns move: motion = push-in | push-out | pan-left | pan-right | static."""
        dur = float(it["duration"])
        W, H = self.W, self.H
        frames = int(round(dur * self.fps))
        motion = it.get("motion", "push-in")
        amount = float(it.get("zoom", 0.12))
        fx = float(it.get("focus_x", 0.5))
        fy = float(it.get("focus_y", 0.5))
        big_w, big_h = W * 2, H * 2  # oversample so the zoom stays sharp
        pre = f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase:flags=lanczos,crop={big_w}:{big_h}:(iw-ow)*{fx}:(ih-oh)*{fy}"
        n = max(frames - 1, 1)
        if motion == "push-out":
            z = f"{1 + amount}-{amount}*on/{n}"
            x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        elif motion == "pan-left":
            z = f"{1 + amount}"
            x, y = f"(iw-iw/zoom)*(1-on/{n})", "ih/2-(ih/zoom/2)"
        elif motion == "pan-right":
            z = f"{1 + amount}"
            x, y = f"(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"
        elif motion == "static":
            z, x, y = "1", "0", "0"
        else:  # push-in
            z = f"1+{amount}*on/{n}"
            x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        vf = f"{pre},zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={self.fps},format=yuv420p,setsar=1"
        cmd = [self.ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(self.root / it["src"]),
               "-filter_complex", vf, "-t", f"{dur:.3f}", "-r", str(self.fps), "-an"] + self._enc() + [str(out)]
        self._run(cmd)
        return out

    def render_card(self, i: int, it: dict, out: Path) -> Path:
        dur = float(it["duration"])
        W, H = self.W, self.H
        bg = hex_to_ffmpeg(it.get("background") or self.bg)
        inputs = ["-f", "lavfi", "-i", f"color=c={bg}:s={W}x{H}:r={self.fps}:d={dur:.3f}"]
        chains, last, n = [], "[0:v]", 1
        img = it.get("image")
        text = it.get("text")
        text_png = self.render_text(it, i) if text and text.get("value") else None
        if img and img.get("src"):
            lw = max(2, int(W * float(img.get("width_frac", 0.32))) // 2 * 2)
            y = "(H-h)/2" if not text_png else f"{H}*0.44-h/2"
            inputs += ["-loop", "1", "-framerate", str(self.fps), "-t", f"{dur:.3f}", "-i", str(self.root / img["src"])]
            chains.append(f"[{n}:v]scale={lw}:-1:flags=lanczos,format=rgba[lg{n}]")
            chains.append(f"{last}[lg{n}]overlay=(W-w)/2:{y}:format=auto:shortest=1[v{n}]")
            last, n = f"[v{n}]", n + 1
        if text_png:
            y = "(H-h)/2" if not (img and img.get("src")) else f"{H}*0.72-h/2"
            inputs += ["-loop", "1", "-framerate", str(self.fps), "-t", f"{dur:.3f}", "-i", str(text_png)]
            chains.append(f"{last}[{n}:v]overlay=(W-w)/2:{y}:format=auto:shortest=1[v{n}]")
            last, n = f"[v{n}]", n + 1
        chains.append(f"{last}format=yuv420p,setsar=1[vout]")
        cmd = [self.ff, "-hide_banner", "-loglevel", "error", "-y"] + inputs + [
            "-filter_complex", ";".join(chains), "-map", "[vout]", "-t", f"{dur:.3f}", "-r", str(self.fps), "-an"] + self._enc() + [str(out)]
        self._run(cmd)
        return out

    def render_text(self, it: dict, i: int) -> Path | None:
        text = it["text"]
        try:
            from PIL import Image, ImageDraw, ImageFont  # type: ignore
        except Exception:
            self.warnings.append(f"{it.get('id')}: text card needs Pillow (pip install Pillow); rendered without text")
            return None
        size = int(self.H * float(text.get("size_frac", 0.05)))
        font = None
        for cand in [text.get("font")] + FONT_CANDIDATES:
            if cand and Path(cand).exists():
                font = ImageFont.truetype(cand, size)
                break
        if font is None:
            font = ImageFont.load_default()
            self.warnings.append("no TrueType font found; title text uses the default bitmap font")
        lines = str(text["value"]).split("\n")
        dummy = Image.new("RGBA", (10, 10))
        d = ImageDraw.Draw(dummy)
        widths, heights = [], []
        for ln in lines:
            box = d.textbbox((0, 0), ln, font=font)
            widths.append(box[2] - box[0])
            heights.append(box[3] - box[1])
        pad = size // 2
        w = max(widths) + pad * 2
        lh = int(max(heights) * 1.3)
        h = lh * len(lines) + pad * 2
        img = Image.new("RGBA", (max(2, w // 2 * 2), max(2, h // 2 * 2)), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        color = text.get("color", "#FFFFFF")
        y = pad
        for ln, lw in zip(lines, widths):
            d.text(((img.width - lw) / 2, y), ln, font=font, fill=color)
            y += lh
        out = self.render / f"text_{i:02}.png"
        img.save(out)
        return out

    # ---------- concat + transitions + fades + overlays (one pass) ----------
    def build_video(self, segs: list[Path]) -> Path:
        """Join the intermediates with the concat filter (hard cuts) and xfade (transitions),
        then apply fades and overlays, encoding the master video track in one pass."""
        out = self.render / "video_post.mp4"
        T = self.total
        groups: list[list[int]] = []
        for i, it in enumerate(self.items):
            if i == 0 or not it.get("transition"):
                if groups:
                    groups[-1].append(i)
                else:
                    groups.append([i])
            else:
                groups.append([i])
        inputs: list[str] = []
        for s in segs:
            inputs += ["-i", str(s)]
        chains: list[str] = []
        labels: list[str] = []
        for g, idxs in enumerate(groups):
            if len(idxs) == 1:
                labels.append(f"[{idxs[0]}:v]")
            else:
                chains.append("".join(f"[{k}:v]" for k in idxs) + f"concat=n={len(idxs)}:v=1:a=0[g{g}]")
                labels.append(f"[g{g}]")
        last = labels[0]
        acc = sum(float(self.items[k]["duration"]) for k in groups[0])
        for g in range(1, len(groups)):
            tr = self.items[groups[g][0]]["transition"]
            td = float(tr.get("duration", 0.5))
            kind = tr.get("type", "fade")
            kind = "fade" if kind in ("fade", "dissolve", "crossfade") else kind
            chains.append(f"{last}{labels[g]}xfade=transition={kind}:duration={td:.3f}:offset={acc - td:.3f}[x{g}]")
            last = f"[x{g}]"
            acc = acc + sum(float(self.items[k]["duration"]) for k in groups[g]) - td
        fi = float(self.edl.get("fade_in") or 0)
        fo = float(self.edl.get("fade_out") or 0)
        vf = []
        if fi > 0:
            vf.append(f"fade=t=in:st=0:d={fi:.3f}")
        if fo > 0:
            vf.append(f"fade=t=out:st={max(T - fo, 0):.3f}:d={fo:.3f}")
        if vf:
            chains.append(f"{last}{','.join(vf)}[f0]")
            last = "[f0]"
        n = len(segs)
        for ov in self.edl.get("overlays", []):
            if ov.get("type", "image") != "image":
                self.warnings.append(f"overlay type {ov.get('type')} not supported; skipped")
                continue
            lw = max(2, int(self.W * float(ov.get("width_frac", 0.07))) // 2 * 2)
            m = int(self.W * float(ov.get("margin_frac", 0.03)))
            op = float(ov.get("opacity", 1.0))
            x, y = {
                "bottom-right": (f"W-w-{m}", f"H-h-{m}"),
                "bottom-left": (f"{m}", f"H-h-{m}"),
                "top-right": (f"W-w-{m}", f"{m}"),
                "top-left": (f"{m}", f"{m}"),
                "center": ("(W-w)/2", "(H-h)/2"),
            }.get(ov.get("position", "bottom-right"), (f"W-w-{m}", f"H-h-{m}"))
            s = float(ov.get("start") or 0)
            e = ov.get("end")
            if e == "card":
                e = self.card_start if self.card_start is not None else T
            e = float(e) if e is not None else T
            inputs += ["-loop", "1", "-framerate", str(self.fps), "-t", f"{T:.3f}", "-i", str(self.root / ov["src"])]
            chains.append(f"[{n}:v]scale={lw}:-1:flags=lanczos,format=rgba,colorchannelmixer=aa={op:.3f}[ov{n}]")
            chains.append(f"{last}[ov{n}]overlay={x}:{y}:format=auto:shortest=1:enable='between(t,{s:.3f},{e:.3f})'[o{n}]")
            last, n = f"[o{n}]", n + 1
        cap = self.edl.get("captions")
        if cap and cap.get("ass"):
            ass_path = self.root / cap["ass"]
            if not ass_path.exists():
                sys.exit(f"captions file not found: {ass_path}")
            esc = str(ass_path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            chains.append(f"{last}ass='{esc}'[cap]")
            last = "[cap]"
        if not chains:
            chains.append(f"{last}null[o0]")
            last = "[o0]"
        (self.render / "video_filter.txt").write_text(";\n".join(chains), encoding="utf-8")
        self._run([self.ff, "-hide_banner", "-loglevel", "error", "-y"] + inputs + [
            "-filter_complex", ";".join(chains), "-map", last, "-t", f"{T:.3f}", "-r", str(self.fps), "-an"]
                  + self._enc(final=True) + ["-movflags", "+faststart", str(out)])
        got = probe(out).get("duration") or 0
        if abs(got - T) > 0.15:
            self.warnings.append(f"video track rendered {got:.2f}s, planned {T:.2f}s")
        return out

    # ---------- audio ----------
    def mix(self) -> Path | None:
        a = self.edl.get("audio") or {}
        vo, mu = a.get("voiceover"), a.get("music")
        if not vo and not mu:
            self.warnings.append("no audio in EDL; output is silent")
            return None
        T = self.total
        inputs, chains, n = [], [], 0
        vo_lbl = mu_lbl = None
        if vo and vo.get("src"):
            inputs += ["-i", str(self.root / vo["src"])]
            delay = int(round(float(vo.get("start", 0)) * 1000))
            gain = float(vo.get("gain_db", 0))
            chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={delay}|{delay},volume={gain}dB[vo]")
            vo_lbl, n = "[vo]", n + 1
        if mu and mu.get("src"):
            mp = self.root / mu["src"]
            if not mp.exists():
                sys.exit(f"music not found: {mp}")
            inputs += ["-stream_loop", "-1", "-i", str(mp)]
            gain = float(mu.get("gain_db", -22))
            fo = float(mu.get("fade_out", 2.0))
            chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{T:.3f},asetpts=PTS-STARTPTS,volume={gain}dB,afade=t=out:st={max(T-fo,0):.3f}:d={fo:.3f}[mu0]")
            mu_lbl, n = "[mu0]", n + 1
            if vo_lbl and mu.get("duck", True):
                chains.append("[vo]asplit[vo1][vo2]")
                chains.append("[mu0][vo2]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=500:makeup=1[mu]")
                vo_lbl, mu_lbl = "[vo1]", "[mu]"
        if vo_lbl and mu_lbl:
            chains.append(f"{vo_lbl}{mu_lbl}amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix0]")
        else:
            chains.append(f"{vo_lbl or mu_lbl}anull[mix0]")
        chains.append(f"[mix0]apad,atrim=0:{T:.3f},asetpts=PTS-STARTPTS[aout]")
        out = self.render / "mix.wav"
        self._run([self.ff, "-hide_banner", "-loglevel", "error", "-y"] + inputs + [
            "-filter_complex", ";".join(chains), "-map", "[aout]", "-c:a", "pcm_s16le", str(out)])
        return out

    def loudnorm_args(self, mix: Path) -> str:
        audio = self.edl.get("audio") or {}
        lufs = float(audio.get("loudnorm_target", -16))
        tp_ceiling = float(audio.get("true_peak_dbtp", -1.0 if lufs >= -14.5 else -1.5))
        # Measured true peak on the final muxed file (what QA checks) runs ~0.15-0.3 dB hotter
        # than the PCM fed to the AAC encoder (inter-sample overs from the lossy encode/decode
        # round trip). Target a stricter internal ceiling so the encoded output still clears
        # the platform spec after that overshoot.
        tp = tp_ceiling - 0.3
        target = f"I={lufs}:TP={tp}:LRA=11"
        if not audio.get("loudnorm", True):
            return ""
        proc = self._run([self.ff, "-hide_banner", "-i", str(mix), "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"], check=False)
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, re.S)
        if not m:
            return f"loudnorm={target}"
        try:
            d = json.loads(m.group(0))
            return (f"loudnorm={target}:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
                    f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true:print_format=summary")
        except Exception:
            return f"loudnorm={target}"

    # ---------- mux ----------
    def mux(self, video: Path, mix: Path | None) -> Path:
        self.out.parent.mkdir(parents=True, exist_ok=True)
        if mix is None:
            self._run([self.ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-c", "copy", "-movflags", "+faststart", str(self.out)])
            return self.out
        ln = self.loudnorm_args(mix)
        af = (ln + "," if ln else "") + "aresample=48000"
        self._run([self.ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-i", str(mix),
                   "-map", "0:v:0", "-map", "1:a:0", "-af", af, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                   "-t", f"{self.total:.3f}", "-movflags", "+faststart", str(self.out)])
        return self.out

    def _run(self, cmd: list[str], check: bool = True):
        import subprocess
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if check and proc.returncode != 0:
            sys.stderr.write("\n".join(proc.stderr.splitlines()[-25:]) + "\n")
            raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:8])} ...")
        return proc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--edl", default="work/edl.json")
    ap.add_argument("--out")
    ap.add_argument("--draft", action="store_true", help="half-size, fast encode")
    ap.add_argument("--validate", action="store_true", help="print the computed timeline and exit")
    ap.add_argument("--render-dir", help="intermediates + timeline_report.json go here (default work/render)")
    args = ap.parse_args()

    job = Job(args.project, args.edl, args.out, args.draft, args.render_dir)
    report = job.plan()
    print(f"timeline: {len(report['items'])} items, total {report['total_duration']}s, voiceover {report['voiceover_duration']}s, cards {report['card_total']}s")
    for it in report["items"]:
        tr = f"  (xfade {it['transition_in']}s)" if it["transition_in"] else ""
        print(f"  {it['id']:>6} {it['start']:7.2f} → {it['end']:7.2f}  {it['duration']:5.2f}s  {it['type']:4} {it['src'] or ''}{tr}")
    for w in report["warnings"]:
        print("  ! " + w)
    for nte in report["notes"]:
        print("  · " + nte)
    if args.validate:
        return

    segs = [job.render_item(i, it) for i, it in enumerate(job.items)]
    video = job.build_video(segs)
    mix = job.mix()
    out = job.mux(video, mix)
    info = probe(out)
    report["output"] = {"path": str(out.relative_to(job.root)), "duration": info.get("duration"),
                        "width": info.get("width"), "height": info.get("height"), "fps": info.get("fps"), "has_audio": info.get("has_audio")}
    report["warnings"] = job.warnings
    dump_json(job.render / "timeline_report.json", report)
    print(f"\nwrote {report['output']['path']}: {info.get('duration')}s {info.get('width')}x{info.get('height')} @ {info.get('fps')} fps, audio={info.get('has_audio')}")
    for w in job.warnings:
        print("  ! " + w)


if __name__ == "__main__":
    main()
