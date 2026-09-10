#!/usr/bin/env python3
"""Preflight for the video-production scripts. usage: doctor.py [--install] [--network]

Checks python, ffmpeg (+ libass, zoompan, libx264), fonts, Pillow, faster-whisper, gdown, disk.
--install runs pip for the optional extras that are missing.
--network also probes the hosts the squad downloads from (Drive, Open Art, Higgsfield,
Hugging Face) and reports which ones this session's egress policy allows.
"""
from __future__ import annotations

import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

REQ = Path(__file__).resolve().parent / "requirements.txt"

# host → why the squad needs it
NETWORK_HOSTS = {
    "drive.google.com": "Google Drive downloads by file id (gdown)",
    "drive.usercontent.google.com": "Google Drive large-file download redirect",
    "openart.ai": "Open Art site / result pages",
    "cdn.openart.ai": "Open Art generated media downloads",
    "higgsfield.ai": "Higgsfield site / API",
    "huggingface.co": "faster-whisper model download (first use)",
    "github.com": "git push",
}


def probe_host(host: str) -> tuple[str, str]:
    import urllib.request, urllib.error, socket
    req = urllib.request.Request(f"https://{host}/", method="HEAD", headers={"User-Agent": "sundae-agent-squad/doctor"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return "ok", f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        # the egress proxy answers 403/405/407 for denied hosts; a real site answers 4xx too, but the tunnel was allowed
        if e.code in (403, 405, 407) and "proxy" in str(e.headers.get("Server", "")).lower():
            return "blocked", f"proxy {e.code}"
        return ("blocked" if e.code in (405, 407) else "ok"), f"HTTP {e.code}"
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "403" in reason or "Tunnel" in reason or "proxy" in reason.lower():
            return "blocked", reason[:70]
        return "error", reason[:70]
    except (socket.timeout, TimeoutError):
        return "error", "timeout"
    except Exception as e:  # noqa: BLE001
        return "error", f"{type(e).__name__}: {str(e)[:60]}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--network", action="store_true", help="probe the hosts the squad downloads from")
    args = ap.parse_args()
    rows, hard_fail = [], False

    rows.append(("python", sys.version_info >= (3, 10), sys.version.split()[0], ">= 3.10"))

    ff = shutil.which("ffmpeg")
    src = "PATH"
    if not ff:
        try:
            import imageio_ffmpeg  # type: ignore
            ff, src = imageio_ffmpeg.get_ffmpeg_exe(), "imageio-ffmpeg"
        except Exception:
            ff = None
    if not ff and args.install:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"], check=False)
        try:
            import imageio_ffmpeg  # type: ignore
            ff, src = imageio_ffmpeg.get_ffmpeg_exe(), "imageio-ffmpeg (installed)"
        except Exception:
            ff = None
    rows.append(("ffmpeg", bool(ff), f"{src}: {ff}" if ff else "missing", "apt/brew ffmpeg or pip install imageio-ffmpeg"))
    if ff:
        filters = subprocess.run([ff, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        for name, why in (("ass", "burned-in captions"), ("zoompan", "Ken Burns on images"), ("xfade", "crossfades"), ("loudnorm", "loudness"), ("sidechaincompress", "music ducking")):
            ok = f" {name} " in filters
            rows.append((f"ffmpeg filter {name}", ok, "yes" if ok else "no", why))
            if name == "ass" and not ok:
                hard_fail = True
        enc = subprocess.run([ff, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        rows.append(("libx264", "libx264" in enc, "yes" if "libx264" in enc else "no", "H.264 export"))
    else:
        hard_fail = True
    rows.append(("ffprobe", bool(shutil.which("ffprobe")), shutil.which("ffprobe") or "not on PATH (ok, scripts parse ffmpeg -i)", "optional"))

    fonts = [f for f in ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                         "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf") if Path(f).exists()]
    rows.append(("fonts", bool(fonts) or bool(shutil.which("fc-list")), fonts[0] if fonts else ("fontconfig present" if shutil.which("fc-list") else "none found"), "captions and title cards"))

    for mod, pkg, why in (("PIL", "Pillow", "title text, placeholders"), ("faster_whisper", "faster-whisper", "word-timed transcripts and captions"), ("gdown", "gdown", "link-shared Drive folders")):
        ok = importlib.util.find_spec(mod) is not None
        if not ok and args.install:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], check=False)
            ok = importlib.util.find_spec(mod) is not None
        rows.append((pkg, ok, "installed" if ok else "missing", why + " (pip install " + pkg + ")"))

    free_gb = shutil.disk_usage(os.getcwd()).free / 1e9
    rows.append(("disk free", free_gb > 5, f"{free_gb:.1f} GB", "> 5 GB for renders"))

    for name, ok, val, note in rows:
        print(f"  {'OK  ' if ok else 'WARN'} {name:24} {val[:60]:60} {note}")
    if args.network:
        print("network (this session's egress policy):")
        blocked = []
        for host, why in NETWORK_HOSTS.items():
            state, detail = probe_host(host)
            mark = {"ok": "OK  ", "blocked": "DENY", "error": "ERR "}[state]
            print(f"  {mark} {host:30} {detail[:34]:34} {why}")
            if state == "blocked":
                blocked.append(host)
        if blocked:
            print("  blocked hosts mean this session cannot download from them; in Claude Code on the web,")
            print("  change the environment's network policy (claude.ai → Code → environments), or run the squad locally.")
    print("hard failures:", "yes" if hard_fail else "none")
    sys.exit(1 if hard_fail else 0)


if __name__ == "__main__":
    main()
