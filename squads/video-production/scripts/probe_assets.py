#!/usr/bin/env python3
"""Inventory a project's assets (or one file) → work/assets.json.

usage: probe_assets.py <project> | --file <path>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import dump_json, kind_of, probe, project_paths

FOLDER_KINDS = {"voiceover": "voiceover", "footage": "footage", "brand": "brand", "music": "music"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?")
    ap.add_argument("--file", help="probe a single file and print JSON")
    args = ap.parse_args()

    if args.file:
        print(json.dumps(probe(args.file), indent=2))
        return
    if not args.project:
        ap.error("project path or --file required")

    p = project_paths(args.project)
    items = []
    for f in sorted(p["assets"].rglob("*")):
        if not f.is_file() or f.name.startswith("."):
            continue
        rel_folder = f.relative_to(p["assets"]).parts[0] if len(f.relative_to(p["assets"]).parts) > 1 else ""
        media = kind_of(f)
        role = FOLDER_KINDS.get(rel_folder, "other")
        entry = {"kind": role, "media": media, "path": str(f.relative_to(p["root"])), "bytes": f.stat().st_size}
        if media in ("video", "audio", "image"):
            entry.update({k: v for k, v in probe(f).items() if k != "path"})
        items.append(entry)

    summary = {
        "voiceover": [i for i in items if i["kind"] == "voiceover"],
        "footage": [i for i in items if i["kind"] == "footage"],
        "brand": [i for i in items if i["kind"] == "brand"],
        "music": [i for i in items if i["kind"] == "music"],
        "other": [i for i in items if i["kind"] == "other"],
    }
    out = {"project": str(p["root"]), "items": items, "counts": {k: len(v) for k, v in summary.items()}}
    dump_json(p["work"] / "assets.json", out)

    print(f"assets.json: {len(items)} files")
    for i in items:
        dur = f"{i['duration']:.1f}s" if i.get("duration") else "-"
        dims = f"{i.get('display_width')}x{i.get('display_height')}" if i.get("display_width") else "-"
        print(f"  {i['kind']:9} {i['media']:6} {dur:>8} {dims:>10} {i['path']}")
    problems = []
    if not summary["voiceover"]:
        problems.append("no voiceover in assets/voiceover/")
    if len(summary["voiceover"]) > 1:
        problems.append("more than one voiceover file; the squad uses the first")
    if not summary["brand"]:
        problems.append("no logo in assets/brand/")
    for b in summary["brand"]:
        if b["media"] == "vector":
            problems.append(f"logo {b['path']} is SVG; convert to transparent PNG")
    if not summary["footage"]:
        problems.append("no footage in assets/footage/ (everything will be generated)")
    for pr in problems:
        print("  ! " + pr)


if __name__ == "__main__":
    main()
