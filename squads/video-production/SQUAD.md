# video-production squad

**Job:** take a voiceover, whatever usable real footage exists, and the company logo; plan the
edit; generate the missing b-roll on Open Art (default) or Higgsfield; assemble, QA and deliver a
finished video. Built for Sundae's event video and reusable for any voiceover-led video.

**Entry point:** `/build-video projects/<slug> [--auto] [--draft] [--revise "notes"]`

## Roster

| Agent | Role | Spends credits? | Reads | Writes |
|---|---|---|---|---|
| `video-producer` | squad lead: runs phases, holds gates, owns budget, reports | no (checks balances) | brief, everything in `work/` | `work/run.log`, final report |
| `video-intake` | inventories assets, transcribes voiceover, extracts stills, describes footage | no (optional Higgsfield video analysis) | `assets/`, brief | `work/assets.json`, `work/transcript.json`, `work/stills/`, `work/refs/`, `work/footage_notes.md` |
| `video-story-editor` | beats → timed shot list; real footage first; marks gaps | no | transcript, footage notes, edit rules | `work/shotlist.json` |
| `broll-director` | prompt, platform, model, params and credits per gap | no (preflight only) | shot list, look profile, routing + prompting playbooks | `work/broll_plan.json` |
| `broll-generator` | uploads references, submits, polls, downloads, verifies, retries once | **yes** | broll plan | `work/broll/*.mp4`, `work/broll_results.json` |
| `video-editor` | EDL, ffmpeg assembly, logo, music, export, revisions | no | shot list, results, edit rules | `work/edl.json`, `output/<slug>_vN.mp4`, `output/<slug>_vN_sheet.jpg` |
| `video-qa` | checks the cut against brief, shot list and checklist | no | everything | `work/qa_report.md`, `work/qa_checks.json` |

All agents live in `.claude/agents/`. Tool lists are least-privilege: only the generator has the
generation tools; only the intake agent has Higgsfield upload and analysis tools.

## Pipeline and gates

```
1 intake ──► 2 story ──► 3 b-roll plan ──[cost gate]──► 4 generate ──► 5 edit ──► 6 QA ──► 7 deliver
                                                                          ▲              │
                                                                          └── fix list ──┘ (max 2 loops)
```

Gates the producer enforces:

- after 1: voiceover present, logo present, transcript engine not `none`
- after 3: **cost gate**. Proceed only with `approval: auto` in the brief and total ≤ `credit_cap`; otherwise show the plan and ask
- after 4: every shot succeeded, or the user decided what to do with failures
- after 6: PASS, or the fix loop ran twice and the rest is reported

## File contracts (`projects/<slug>/`)

| File | Producer | Schema |
|---|---|---|
| `brief.md` | human (or `/new-video-brief`) | `templates/brief.md` |
| `work/assets.json` | `scripts/probe_assets.py` | list of `{kind, path, duration, width, height, fps, has_audio, codec}` |
| `work/transcript.json` | `scripts/transcribe.py` | `{engine, duration, segments[{id,start,end,text,words[{w,start,end}]}]}` |
| `work/footage_notes.md` | video-intake | per-clip notes, Look profile, Gaps |
| `work/shotlist.json` | video-story-editor | `templates/shotlist.json` |
| `work/broll_plan.json` | broll-director | `templates/broll_plan.json` |
| `work/broll_results.json` | broll-generator | `templates/broll_results.json` |
| `work/edl.json` | video-editor | `templates/edl.json` |
| `work/render/timeline_report.json` | `scripts/assemble.py` | computed segment starts, totals, warnings |
| `work/qa_checks.json`, `work/qa_report.md` | `scripts/qa_checks.py`, video-qa | numbers; verdict + fix list |
| `work/run.log` | video-producer | one line per phase |

## Scripts (`squads/video-production/scripts/`)

| Script | Does |
|---|---|
| `common.py` | finds ffmpeg (PATH → `imageio-ffmpeg`), probes media without ffprobe |
| `probe_assets.py <project>` / `--file <path>` | inventory → `work/assets.json` |
| `download.py <url> <dest>` | fetch a remote asset or a generated clip |
| `transcribe.py <project> [--model small] [--script file]` | faster-whisper word timestamps, or an estimate from the script |
| `extract_frames.py <project>` / `--file <clip>` | viewing stills + one full-res reference frame per clip |
| `assemble.py <project> --edl work/edl.json --out output/x.mp4 [--draft] [--validate]` | EDL → mp4 |
| `contact_sheet.py <video> [--interval 2]` | thumbnail grid for reviewing |
| `qa_checks.py <project> <video>` | duration, black, silence, loudness, format → `work/qa_checks.json` |

Install extras: `pip install -r squads/video-production/scripts/requirements.txt`.

## Running a member alone

`@agent-broll-director price a 6 s wide establishing shot of a conference hall for projects/sundae-event-video`
works without the rest of the pipeline; each agent reads what exists in `work/` and says what is missing.

## Extending

- New deliverable type (vertical cut, 30 s social cut): add a section to `edit-rules.md` and a
  flag to `/build-video`; the editor reads the brief's `deliverables:` list.
- New platform: add a column to `platform-routing.md`, its tools to `broll-director` and
  `broll-generator`, and its mechanics section.
- New squad: `/new-squad <name>`.
