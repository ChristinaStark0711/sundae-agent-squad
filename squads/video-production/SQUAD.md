# video-production squad

**Job:** take a voiceover, whatever usable real footage exists, and the company logo; plan the
edit; generate the missing b-roll on Open Art (default) or Higgsfield; assemble, QA and deliver a
finished video. Built for Sundae's event video and reusable for any voiceover-led video.

**Entry points:**
- `/build-video projects/<slug> [--auto] [--draft] [--revise "notes"]` — one voiceover-led video (16:9 by default)
- `/build-reels projects/<slug> [--count N] [--continue] [--auto] [--revise "notes"]` — a mix-and-match batch of 9:16 captioned shorts from a Google Drive library; builds one test video, stops, then the rest on `--continue`

## Roster

| Agent | Role | Spends credits? | Reads | Writes |
|---|---|---|---|---|
| `video-producer` | squad lead: runs phases, holds gates, owns budget, reports | no (checks balances) | brief, everything in `work/` | `work/run.log`, final report |
| `drive-librarian` | pulls videos / images / voiceovers / music / logo from Google Drive folders, catalogs them, uploads finished videos back when asked | no | brief `drive_folders`, Drive | `assets/*`, `work/library.json`, `work/drive_manifest.json` |
| `reels-planner` | mix-and-match batch plan for 9:16 shorts; marks video 1 as the test | no | library, transcripts, reels-format playbook | `work/batch.json` |
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

### Reels mode

```
R0 library (drive-librarian) ──► R1 transcripts (video-intake) ──► R2 batch plan (reels-planner)
      ──[cost question]──► R3 TEST VIDEO r01 (story → director → generator → editor+captions → QA)
      ──[always stops: user watches r01 and confirms]──► R4 remaining videos, one at a time
      ──► R5 deliver: output/reels/*.mp4, batch_report.md, optional Drive upload
```

Per-video files live in `work/videos/<id>/` (shotlist, broll_plan, broll_results, edl,
captions.ass, render/, qa_report). Scripts take the matching path flags.

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
| `work/library.json` | drive-librarian | `templates/library.json` |
| `work/drive_manifest.json` | drive-librarian / `scripts/drive_pull.py` | what was pulled from which folder |
| `work/transcripts/<stem>.json` | `scripts/transcribe.py --audio --out` | one transcript per voiceover |
| `work/batch.json` | reels-planner | `templates/batch.json` |
| `work/videos/<id>/captions.ass` | `scripts/captions.py` | burned-in captions for that video |
| `output/reels/batch_report.md` | video-producer | per-video hook, assets, length, credits, QA |

## Scripts (`squads/video-production/scripts/`)

| Script | Does |
|---|---|
| `common.py` | finds ffmpeg (PATH → `imageio-ffmpeg`), probes media without ffprobe |
| `probe_assets.py <project>` / `--file <path>` | inventory → `work/assets.json` |
| `download.py <url> <dest>` | fetch a remote asset or a generated clip |
| `transcribe.py <project> [--model small] [--script file]` | faster-whisper word timestamps, or an estimate from the script |
| `extract_frames.py <project>` / `--file <clip>` | viewing stills + one full-res reference frame per clip |
| `assemble.py <project> --edl work/edl.json --out output/x.mp4 [--draft] [--validate] [--render-dir]` | EDL → mp4; clip / image (Ken Burns) / card items, 9:16 crop focus, captions |
| `contact_sheet.py <video> [--interval 2]` | thumbnail grid for reviewing |
| `qa_checks.py <project> <video> [--max-length 60] [--edl --transcript --shotlist --report --out]` | duration, black, silence, loudness, format, length limit → `work/qa_checks.json` |
| `captions.py <project> [--transcript] [--out] [--style reels\|clean\|minimal] [--highlight] [--position 0.70]` | word-timed captions → ASS file the assembler burns in |
| `drive_pull.py <project> --from-brief` / `--file-id <id> --kind <kind>` / `--b64 <path>` | download link-shared Drive folders or files (gdown); write small connector downloads from base64 |
| `make_placeholder.py <project> --plan <broll_plan.json> --out-dir <dir>` | dry run: labelled stand-in clips for generated b-roll, credits 0 |
| `batch_report.py <project>` | compile `output/reels/batch_report.md` from batch.json and each video's QA / results |
| `doctor.py [--install]` | preflight: ffmpeg + filters, fonts, Pillow, faster-whisper, gdown, disk |

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
