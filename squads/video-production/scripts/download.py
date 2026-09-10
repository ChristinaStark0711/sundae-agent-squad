#!/usr/bin/env python3
"""Download a URL to a file (remote asset or a generated clip).

usage: download.py <url> <dest>
Google Drive share links are rewritten to direct-download form.
"""
from __future__ import annotations

import re
import shutil
import sys
import urllib.request
from pathlib import Path


def normalize(url: str) -> str:
    m = re.search(r"drive\.google\.com/file/d/([^/]+)", url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    m = re.search(r"dropbox\.com/(.+)\?dl=0", url)
    if m:
        return url.replace("?dl=0", "?dl=1")
    return url


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    url, dest = normalize(sys.argv[1]), Path(sys.argv[2])
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "sundae-agent-squad/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as fh:
        shutil.copyfileobj(resp, fh, length=1 << 20)
    size = dest.stat().st_size
    if size < 1024:
        sys.exit(f"downloaded only {size} bytes to {dest}; check the URL (HTML page instead of media?)")
    print(f"{dest} ({size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
