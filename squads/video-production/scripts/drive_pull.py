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
    - {kind: auto, url: "https://drive.google.com/drive/folders/..."}   # flat folder: sorted by file type
    - {kind: brand, url: "..."}                                            # or one folder per kind
    - {kind: auto, path: "~/Library/CloudStorage/GoogleDrive-you@co.com/My Drive/Folder"}
                                   # a Google Drive for Desktop mount (or any local folder): linked, no download
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from common import dump_json, load_json, project_paths, read_brief_frontmatter

KINDS = ("footage", "images", "voiceover", "music", "brand", "auto")
MUSIC_HINTS = ("music", "bed", "track", "song", "instrumental", "beat")
LOGO_HINTS = ("logo", "mark", "brand", "favicon")


HEIC_EXT = {".heic", ".heif"}


def convert_heic(path: Path) -> Path:
    """iPhone HEIC/HEIF -> PNG so ffmpeg (no libheif in the bundled static build) can use it.
    Returns the converted path, or the original path unchanged if conversion isn't available
    or isn't needed."""
    if path.suffix.lower() not in HEIC_EXT:
        return path
    try:
        import pillow_heif  # type: ignore
        pillow_heif.register_heif_opener()
        from PIL import Image  # type: ignore
    except Exception:
        print(f"   ! {path.name}: HEIC/HEIF image, no HEIC decoder available "
              f"(pip install pillow-heif) - kept as-is, ffmpeg in this build cannot read it")
        return path
    out = path.with_suffix(".png")
    try:
        Image.open(path).convert("RGB").save(out, "PNG")
    except Exception as e:  # noqa: BLE001
        print(f"   ! {path.name}: HEIC conversion failed ({e}) - kept as-is")
        return path
    print(f"   {path.name} -> {out.name} (HEIC converted to PNG)")
    return out


def classify(path: Path) -> str:
    """Kind for a file from a flat folder: by media type, with filename hints for music and logos."""
    from common import kind_of
    media = kind_of(path)
    name = path.name.lower()
    if media == "video":
        return "footage"
    if media == "audio":
        return "music" if any(h in name for h in MUSIC_HINTS) else "voiceover"
    if media in ("image", "vector"):
        return "brand" if any(h in name for h in LOGO_HINTS) else "images"
    return "other"


def sort_auto(files: list[str], assets: Path) -> dict[str, list[str]]:
    import shutil
    moved: dict[str, list[str]] = {}
    for f in files:
        src = Path(f)
        kind = classify(src)
        if kind == "other":
            continue
        dest = assets / kind / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.resolve() != dest.resolve():
            shutil.move(str(src), str(dest))
        dest = convert_heic(dest)
        moved.setdefault(kind, []).append(str(dest))
    return moved


def pull(folder: str, dest: Path) -> list[str]:
    try:
        import gdown  # type: ignore
    except Exception:
        sys.exit("gdown not installed: pip install gdown")
    dest.mkdir(parents=True, exist_ok=True)
    url = folder if folder.startswith("http") else f"https://drive.google.com/drive/folders/{folder}"
    kwargs = {"quiet": False}
    import inspect
    params = inspect.signature(gdown.download_folder).parameters
    if "use_cookies" in params:
        kwargs["use_cookies"] = False
    if "remaining_ok" in params:
        kwargs["remaining_ok"] = True
    files = gdown.download_folder(url=url, output=str(dest), **kwargs)
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
            ap.error("--kind is required with --file-id (use auto to sort by file type)")
        try:
            import gdown  # type: ignore
        except Exception:
            sys.exit("gdown not installed: pip install gdown")
        kind = args.kind
        if kind == "auto":
            kind = classify(Path(args.name)) if args.name else "footage"
        dest_dir = p["assets"] / kind
        dest_dir.mkdir(parents=True, exist_ok=True)
        out = str(dest_dir / args.name) if args.name else str(dest_dir) + "/"
        got = gdown.download(id=args.file_id, output=out, quiet=False)
        if not got:
            sys.exit(f"could not download {args.file_id}; the file (or its folder) must be shared as 'Anyone with the link'")
        args.kind = kind
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
    local_jobs: list[tuple[str, Path]] = []
    if args.from_brief:
        fm = read_brief_frontmatter(p["root"])
        for entry in fm.get("drive_folders") or []:
            if not isinstance(entry, dict) or entry.get("kind") not in KINDS:
                continue
            if entry.get("path"):
                local_jobs.append((entry["kind"], Path(str(entry["path"])).expanduser()))
            elif entry.get("url"):
                jobs.append((entry["kind"], entry["url"]))
        if not jobs and not local_jobs:
            sys.exit("brief.md has no drive_folders entries")
    elif args.folder and args.kind:
        jobs.append((args.kind, args.folder))
    else:
        ap.error("--from-brief, or --folder with --kind, or --list")

    manifest_path = p["work"] / "drive_manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {"pulls": []}
    for kind, folder in local_jobs:
        if not folder.is_dir():
            sys.exit(f"local folder not found: {folder} (is Google Drive for Desktop running and the folder available offline?)")
        print(f"== {kind} ← {folder} (local, linked)")
        linked: dict[str, list[str]] = {}
        for f in sorted(folder.rglob("*")):
            if not f.is_file() or f.name.startswith(".") or f.suffix.lower() in (".gdoc", ".gsheet", ".gslides"):
                continue
            k = classify(f) if kind == "auto" else kind
            if k == "other":
                continue
            dest = p["assets"] / k / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() or dest.is_symlink():
                dest.unlink()
            if f.suffix.lower() in HEIC_EXT:
                # convert from the source, don't symlink a format ffmpeg can't read
                converted = convert_heic(f)
                if converted != f:
                    import shutil
                    shutil.copy2(converted, dest.with_suffix(".png"))
                    dest = dest.with_suffix(".png")
                else:
                    dest.symlink_to(f.resolve())
            else:
                try:
                    dest.symlink_to(f.resolve())
                except OSError:
                    import shutil
                    shutil.copy2(f, dest)
            linked.setdefault(k, []).append(str(dest.relative_to(p["root"])))
        for k, lst in linked.items():
            print(f"   {len(lst)} → assets/{k}/")
        manifest["pulls"].append({"kind": kind, "path": str(folder), "files": [x for lst in linked.values() for x in lst],
                                  "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    for kind, folder in jobs:
        dest = p["assets"] / ("_incoming" if kind == "auto" else kind)
        print(f"== {kind} ← {folder}")
        files = pull(folder, dest)
        if kind == "auto":
            sorted_files = sort_auto(files, p["assets"])
            files = [f for lst in sorted_files.values() for f in lst]
            for k, lst in sorted_files.items():
                print(f"   {len(lst)} → assets/{k}/")
            if dest.exists() and not any(dest.iterdir()):
                dest.rmdir()
        rel = [str(Path(f).resolve().relative_to(p["root"])) if Path(f).resolve().is_relative_to(p["root"]) else f for f in files]
        manifest["pulls"].append({"kind": kind, "folder": folder, "files": rel, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        print(f"   {len(files)} files")
    dump_json(manifest_path, manifest)
    print(f"work/drive_manifest.json updated; now run probe_assets.py")


if __name__ == "__main__":
    main()
