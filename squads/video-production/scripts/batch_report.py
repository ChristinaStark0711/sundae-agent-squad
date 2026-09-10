#!/usr/bin/env python3
"""Compile output/reels/batch_report.md from work/batch.json and each video's work folder.

usage: batch_report.py <project> [--out output/reels/batch_report.md]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import load_json, probe, project_paths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out", default="output/reels/batch_report.md")
    args = ap.parse_args()
    p = project_paths(args.project)
    batch = load_json(p["work"] / "batch.json")
    rows, total_credits, total_len = [], 0, 0.0
    for v in batch.get("videos", []):
        vid = v["id"]
        vdir = p["videos"] / vid
        verdict, fixes = "not built", ""
        qa = vdir / "qa_report.md"
        if qa.exists():
            m = re.search(r"Verdict:\s*(PASS|FAIL)", qa.read_text())
            verdict = m.group(1) if m else "unknown"
            fixes = str(len(re.findall(r"^\s*\d+\.", qa.read_text(), re.M)))
        credits = 0
        res = vdir / "broll_results.json"
        if res.exists():
            credits = int((load_json(res).get("totals") or {}).get("all", 0))
        out_file = v.get("output")
        dur, size = "", ""
        if out_file and (p["root"] / out_file).exists():
            info = probe(p["root"] / out_file)
            dur = f"{info.get('duration') or 0:.1f}s"
            size = f"{(p['root'] / out_file).stat().st_size / 1e6:.1f} MB"
            total_len += info.get("duration") or 0
        n_real = sum(1 for x in v.get("visuals", []) if x.get("kind") == "footage")
        n_img = sum(1 for x in v.get("visuals", []) if x.get("kind") == "image")
        n_gen = len(v.get("broll_gaps", []))
        total_credits += credits
        rows.append(f"| {vid}{' (test)' if v.get('is_test') else ''} | {v.get('hook','')[:60]} | {Path(v.get('voiceover',{}).get('path','')).name} "
                    f"| {n_real} / {n_img} / {n_gen} | {dur} | {credits} | {verdict}{(' (' + fixes + ' fixes)') if fixes and verdict == 'FAIL' else ''} | {out_file or ''} |")
    meta = batch.get("meta", {})
    md = [f"# Batch report: {meta.get('slug', p['root'].name)}", "",
          f"Videos: {len(rows)} · Platforms: {', '.join(meta.get('platforms', []))} · Canvas: {meta.get('canvas', {}).get('width')}x{meta.get('canvas', {}).get('height')}",
          f"Credits spent: {total_credits} (cap {meta.get('credit_cap')}) · Total runtime: {total_len:.0f}s",
          f"Approved settings from the test video: {meta.get('approved_settings') or 'none recorded'}", "",
          "| Video | Hook | Voiceover | real / image / generated | Length | Credits | QA | File |",
          "|---|---|---|---|---|---|---|---|", *rows, ""]
    vm = meta.get("variety_matrix") or {}
    if vm:
        md += ["## Where each asset appears", "", "| Asset | Videos |", "|---|---|"]
        md += [f"| {k} | {', '.join(v)} |" for k, v in vm.items()]
        md.append("")
    out = p["root"] / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"{args.out}: {len(rows)} videos, {total_credits} credits")


if __name__ == "__main__":
    main()
