"""Shared helpers: ffmpeg discovery, media probing (works without ffprobe), paths, JSON."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi", ".mts", ".m2ts"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".aiff", ".aif"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
VECTOR_EXT = {".svg"}


def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    sys.exit(
        "ffmpeg not found. Install it (apt/brew) or run: pip install imageio-ffmpeg"
    )


def ffprobe_bin() -> str | None:
    return shutil.which("ffprobe")


def run(cmd: list[str], check: bool = True, quiet: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        sys.stderr.write(proc.stderr[-4000:])
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd[:6])} ...")
    if not quiet and proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc


def kind_of(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in VIDEO_EXT:
        return "video"
    if ext in AUDIO_EXT:
        return "audio"
    if ext in IMAGE_EXT:
        return "image"
    if ext in VECTOR_EXT:
        return "vector"
    return "other"


_DUR = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_VID = re.compile(r"Stream #\d+:\d+.*?Video:\s*([A-Za-z0-9_]+).*?,\s*(\d{2,5})x(\d{2,5})")
_FPS = re.compile(r"(\d+(?:\.\d+)?)\s*fps")
_AUD = re.compile(r"Stream #\d+:\d+.*?Audio:\s*([A-Za-z0-9_]+)(?:.*?,\s*(\d+)\s*Hz)?")
_ROT = re.compile(r"rotation of (-?\d+(?:\.\d+)?) degrees|rotate\s*:\s*(-?\d+)")


def probe(path: str | Path) -> dict:
    """Return {duration, width, height, fps, has_video, has_audio, vcodec, acodec, sample_rate, rotation}."""
    path = str(path)
    info = {
        "path": path,
        "duration": None,
        "width": None,
        "height": None,
        "fps": None,
        "has_video": False,
        "has_audio": False,
        "vcodec": None,
        "acodec": None,
        "sample_rate": None,
        "rotation": 0,
    }
    fp = ffprobe_bin()
    if fp:
        proc = subprocess.run(
            [fp, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout or "{}")
            fmt = data.get("format", {})
            if fmt.get("duration"):
                info["duration"] = float(fmt["duration"])
            for s in data.get("streams", []):
                if s.get("codec_type") == "video" and not info["has_video"]:
                    info["has_video"] = True
                    info["vcodec"] = s.get("codec_name")
                    info["width"], info["height"] = s.get("width"), s.get("height")
                    r = s.get("avg_frame_rate") or s.get("r_frame_rate") or "0/1"
                    num, _, den = r.partition("/")
                    try:
                        info["fps"] = round(float(num) / float(den or 1), 3) if float(den or 1) else None
                    except ValueError:
                        info["fps"] = None
                    rot = (s.get("tags") or {}).get("rotate")
                    if rot:
                        info["rotation"] = int(float(rot))
                    for sd in s.get("side_data_list") or []:
                        if "rotation" in sd:
                            info["rotation"] = int(float(sd["rotation"]))
                elif s.get("codec_type") == "audio" and not info["has_audio"]:
                    info["has_audio"] = True
                    info["acodec"] = s.get("codec_name")
                    if s.get("sample_rate"):
                        info["sample_rate"] = int(s["sample_rate"])
            _apply_rotation(info)
            return info
    # Fallback: parse `ffmpeg -i` banner (imageio-ffmpeg ships no ffprobe).
    proc = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", path], capture_output=True, text=True)
    text = proc.stderr
    m = _DUR.search(text)
    if m:
        h, mnt, s = m.groups()
        info["duration"] = round(int(h) * 3600 + int(mnt) * 60 + float(s), 3)
    m = _VID.search(text)
    if m:
        info["has_video"] = True
        info["vcodec"] = m.group(1)
        info["width"], info["height"] = int(m.group(2)), int(m.group(3))
        line = text[m.start(): text.find("\n", m.start())]
        f = _FPS.search(line)
        if f:
            info["fps"] = float(f.group(1))
    m = _AUD.search(text)
    if m:
        info["has_audio"] = True
        info["acodec"] = m.group(1)
        if m.group(2):
            info["sample_rate"] = int(m.group(2))
    m = _ROT.search(text)
    if m:
        info["rotation"] = int(float(m.group(1) or m.group(2)))
    _apply_rotation(info)
    return info


def _apply_rotation(info: dict) -> None:
    """Report display dimensions for phone footage stored with a rotation tag."""
    if info.get("rotation") in (90, -90, 270, -270) and info.get("width") and info.get("height"):
        info["display_width"], info["display_height"] = info["height"], info["width"]
    else:
        info["display_width"], info["display_height"] = info.get("width"), info.get("height")


def project_paths(project: str | Path) -> dict[str, Path]:
    root = Path(project).resolve()
    if not (root / "brief.md").exists():
        sys.exit(f"{root} has no brief.md; is this a project folder?")
    p = {
        "root": root,
        "assets": root / "assets",
        "work": root / "work",
        "output": root / "output",
        "stills": root / "work" / "stills",
        "refs": root / "work" / "refs",
        "broll": root / "work" / "broll",
        "render": root / "work" / "render",
        "videos": root / "work" / "videos",
    }
    for key in ("work", "output", "stills", "refs", "broll", "render", "videos"):
        p[key].mkdir(parents=True, exist_ok=True)
    return p


def read_brief_frontmatter(project_root: Path) -> dict:
    """Tiny YAML-subset reader for brief.md front matter (scalars, lists of scalars, inline maps, block scalars)."""
    text = (project_root / "brief.md").read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip("\n")
    data: dict = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith(" "):
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.split(" #")[0].strip() if not rest.strip().startswith('"') else rest.strip()
        if rest == "|" or rest == ">":
            buf = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                buf.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            data[key] = "\n".join(buf).strip()
            continue
        if rest == "":
            items = []
            i += 1
            while i < len(lines) and lines[i].startswith("  -"):
                items.append(_scalar(lines[i].split("-", 1)[1].strip()))
                i += 1
            data[key] = items
            continue
        data[key] = _scalar(rest)
        i += 1
    return data


def _scalar(v: str):
    v = v.strip()
    if v.startswith("{") and v.endswith("}"):
        out = {}
        for part in v[1:-1].split(","):
            if ":" in part:
                k, _, val = part.partition(":")
                out[k.strip()] = _scalar(val)
        return out
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_scalar(x) for x in inner.split(",")] if inner else []
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v.lower() in ("null", "none", "~", ""):
        return None
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def hex_to_ffmpeg(color: str) -> str:
    color = (color or "#000000").strip()
    return "0x" + color[1:] if color.startswith("#") else color
