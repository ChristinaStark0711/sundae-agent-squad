#!/usr/bin/env python3
"""Pull assets from link-shared Google Drive folders into the project's assets/ (fallback path).

usage: drive_pull.py <project> --from-brief
       drive_pull.py <project> --folder <url-or-id> --kind footage|images|voiceover|music|brand
       drive_pull.py <project> --file-id <id> --kind <kind> [--name <filename>]
       drive_pull.py <project> --list <url-or-id>
       drive_pull.py <project> --b64 <path>      (decode base64 from stdin into <path>, for small
                                                  files the Drive connector returns inline)

Uses `gdown` (pip install gdown). Folders must be shared as "Anyone with the link"; gdown
downloads at most 50 files per folder. For private folders or larger sets, use the Google
Drive connector through the drive-librarian agent instead. Writes work/drive_manifest.json.

brief.md front matter:
  drive_folders:
    - {kind: footage, url: "https://drive.google.com/drive/folders/..."}
    - {kind: voiceover, url: "..."}
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from common import dump_json, load_json, project_paths, read_brief_frontmatter

KINDS = ("footage", "images", "voiceover", "music", "brand")


def pull(folder: str, dest: Path) -> list[str]:
    try:
        import gdown  # type: ignore
    except Exception:
        sys.exit("gdown not installed: pip install gdown")
    dest.mkdir(parents=True, exist_ok=True)
    url = folder if folder.startswith("http") else f"https://drive.google.com/drive/folders/{folder}"
    files = gdown.download_folder(url=url, output=str(dest), quiet=False, use_cookies=False, remaining_ok=True)
    if not files:
        sys.exit(f"nothing downloaded from {url}. Is the folder shared as 'Anyone with the link'? "
                 "Private folders need the Google Drive connector (drive-librarian agent).")
    return [str(Path(f)) for f in files]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--from-brief", action="store_true")
    ap.add_argument("--folder")
    ap.add_argument("--kind", choices=KINDS)
    ap.add_argument("--list", help="list a folder's contents (JSON) without downloading")
    ap.add_argument("--file-id", help="download one file by Drive id (link-shared)")
    ap.add_argument("--name", help="filename for --file-id (default: Drive's name)")
    ap.add_argument("--b64", help="write base64 from stdin to this path (relative to the project)")
    args = ap.parse_args()
    p = project_paths(args.project)

    if args.b64:
        import base64
        dest = p["root"] / args.b64
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = sys.stdin.read().strip()
        if data.startswith("data:"):
            data = data.split(",", 1)[1]
        dest.write_bytes(base64.b64decode(data))
        print(f"{args.b64} ({dest.stat().st_size/1e6:.2f} MB)")
        return

    if args.file_id:
        if not args.kind:
            ap.error("--kind is required with --file-id")
        try:
            import gdown  # type: ignore
        except Exception:
            sys.exit("gdown not installed: pip install gdown")
        dest_dir = p["assets"] / args.kind
        dest_dir.mkdir(parents=True, exist_ok=True)
        out = str(dest_dir / args.name) if args.name else str(dest_dir) + "/"
        got = gdown.download(id=args.file_id, output=out, quiet=False, fuzzy=True)
        if not got:
            sys.exit(f"could not download {args.file_id}; the file (or its folder) must be shared as 'Anyone with the link'")
        manifest_path = p["work"] / "drive_manifest.json"
        manifest = load_json(manifest_path) if manifest_path.exists() else {"pulls": []}
        rel = str(Path(got).resolve().relative_to(p["root"]))
        manifest["pulls"].append({"kind": args.kind, "file_id": args.file_id, "files": [rel], "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        dump_json(manifest_path, manifest)
        print(f"{rel}")
        return

    if args.list:
        import subprocess
        url = args.list if args.list.startswith("http") else f"https://drive.google.com/drive/folders/{args.list}"
        proc = subprocess.run([sys.executable, "-m", "gdown", "--folder", "--json", url], capture_output=True, text=True)
        print(proc.stdout or proc.stderr)
        return

    jobs: list[tuple[str, str]] = []
    if args.from_brief:
        fm = read_brief_frontmatter(p["root"])
        for entry in fm.get("drive_folders") or []:
            if isinstance(entry, dict) and entry.get("kind") in KINDS and entry.get("url"):
                jobs.append((entry["kind"], entry["url"]))
        if not jobs:
            sys.exit("brief.md has no drive_folders entries")
    elif args.folder and args.kind:
        jobs.append((args.kind, args.folder))
    else:
        ap.error("--from-brief, or --folder with --kind, or --list")

    manifest_path = p["work"] / "drive_manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {"pulls": []}
    for kind, folder in jobs:
        dest = p["assets"] / kind
        print(f"== {kind} ← {folder}")
        files = pull(folder, dest)
        rel = [str(Path(f).resolve().relative_to(p["root"])) if Path(f).resolve().is_relative_to(p["root"]) else f for f in files]
        manifest["pulls"].append({"kind": kind, "folder": folder, "files": rel, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        print(f"   {len(files)} files → assets/{kind}/")
    dump_json(manifest_path, manifest)
    print(f"work/drive_manifest.json updated; now run probe_assets.py")


if __name__ == "__main__":
    main()
