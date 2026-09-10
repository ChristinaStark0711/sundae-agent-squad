# sundae-agent-squad

AI agent squads for Sundae, built as [Claude Code](https://code.claude.com) subagents and skills.
The first squad, **video-production**, turns a CEO voiceover, a handful of usable event clips and
the company logo into a finished video, generating whatever b-roll is missing on
[Open Art](https://openart.ai) or [Higgsfield](https://higgsfield.ai) through their MCP connectors.

The repo is organised so more squads (social content, ads, decks, whatever comes next) can be
added the same way without touching the existing one.

## Quick start: the Sundae event video

1. Open this repo in Claude Code (web, desktop or CLI) with Open Art and Higgsfield connected.
2. Put the inputs in place:
   - `projects/sundae-event-video/assets/voiceover/` — the CEO voiceover (wav, mp3 or m4a)
   - `projects/sundae-event-video/assets/footage/` — every usable event clip
   - `projects/sundae-event-video/assets/brand/` — the logo as a transparent PNG (SVG is fine too)
   - optional `assets/music/` — a licensed music bed

   In a cloud session you can't drop files into the container, so list download URLs under
   `assets_urls:` in `projects/sundae-event-video/brief.md` instead and the intake agent fetches them.
3. Fill in the rest of `projects/sundae-event-video/brief.md` (tone, length, credit cap, must-show moments).
4. Run:

   ```
   /build-video projects/sundae-event-video
   ```

The squad inventories and transcribes the inputs, plans the edit, shows you the b-roll plan with
its credit cost, generates the clips after you approve (or automatically if the brief says
`approval: auto` and the plan is under `credit_cap`), assembles the cut with ffmpeg, runs QA and
hands back `projects/sundae-event-video/output/sundae-event-video_v1.mp4` plus a contact sheet
and a QA report.

Revisions:

```
/build-video projects/sundae-event-video --revise "tighten the opening, swap shot s07 for something with more people"
```

## Reels, TikToks and Shorts from a Google Drive library

The same squad has a **reels mode** for batches of 9:16 captioned shorts:

1. Share the Drive folders (Footage, Images, Voiceovers, Music, Brand) and put their links in
   `projects/<slug>/brief.md` under `drive_folders:` (start from `templates/brief-reels.md` or
   run `/new-video-brief <slug> --reels`). Enable the Google Drive connector in the chat; folders
   shared by link also work without it.
2. Run:

   ```
   /build-reels projects/sundae-reels
   ```

   The librarian pulls and catalogs everything, the planner writes a mix-and-match batch (no two
   videos share more than half their visuals, every voiceover is used), and the squad builds
   **one test video** with burned-in captions, the logo in the safe zone, music ducked under the
   voice and an end card, then **stops** and shows it to you.
3. Watch it, give notes if any, then:

   ```
   /build-reels projects/sundae-reels --continue
   ```

   Your notes become batch-wide settings and the remaining videos are built one at a time into
   `output/reels/`, with a batch report and, if `drive_output_folder` is set, an upload to Drive.

Format rules (safe zones, lengths, caption styles, vertical cropping) are in
`squads/video-production/playbooks/reels-format.md`.

## How the squad works

```
brief.md + assets
      │
      ▼
video-intake ─────► work/assets.json, transcript.json, stills/, footage_notes.md
      │
      ▼
video-story-editor ► work/shotlist.json   (every second of voiceover assigned to a real clip,
      │                                     a b-roll gap, or a logo card)
      ▼
broll-director ────► work/broll_plan.json (prompt, platform, model, params, credits per gap)
      │                       ── cost gate: approval unless brief says auto and under cap ──
      ▼
broll-generator ───► work/broll/*.mp4, broll_results.json  (Open Art or Higgsfield)
      │
      ▼
video-editor ──────► work/edl.json → output/<slug>_vN.mp4 + contact sheet
      │
      ▼
video-qa ──────────► work/qa_report.md  (PASS, or a fix list the editor applies)
      │
      ▼
video-producer reports: file, duration, credits spent, what to review
```

`video-producer` is the squad lead. It runs the phases, owns the credit budget, stops at the
gates, and writes the final report. Each member is a subagent under `.claude/agents/` and can
also be used on its own (for example `@agent-broll-director` to price a single shot).

## Where to run it (read this once)

The agents and the Open Art / Higgsfield / Google Drive **tools** work in any session, because
MCP connector traffic goes through Anthropic's servers. **Downloads do not**: pulling your clips
from Drive, fetching generated b-roll from Open Art or Higgsfield, and the first-time whisper
model download all go through the session's own network. Pick one of these setups:

| Setup | Media in | Media out | Notes |
|---|---|---|---|
| **A. Local Claude Code (desktop app or CLI) with Google Drive for Desktop** — recommended for real runs | the Drive folder is already on disk: put its path in the brief (`drive_folders: - {kind: auto, path: "~/Library/CloudStorage/GoogleDrive-you@sundae.com/My Drive/Sundae - Videos + Edits"}`) and nothing is downloaded | files land in `projects/<slug>/output/` on your machine | no network limits; whisper downloads its model once |
| **B. Cloud session (claude.ai/code) with network access set to Custom or Full** | share the Drive folder as *Anyone with the link* once; the librarian pulls files by id | files are in the container; the squad sends them to you or uploads the batch report to Drive | on the environment's **Network access** selector choose **Custom**, paste the list below into **Allowed domains**, and tick *Also include default list of common package managers* (or choose **Full**) |
| **C. Cloud session at the default Trusted level** | nothing but tiny files | nothing | planning, briefs, `--dry-run` rehearsals and code changes only |

Allowed domains for setup B (one per line):

```
drive.google.com
drive.usercontent.google.com
*.googleusercontent.com
openart.ai
*.openart.ai
higgsfield.ai
*.higgsfield.ai
huggingface.co
*.huggingface.co
*.cloudfront.net
```

If a download still fails, the error names the host; add it to the list. Check any session with
`python3 squads/video-production/scripts/doctor.py --network`.

## Rehearse before spending

Both commands take `--dry-run`: the squad runs every phase but stands in labelled placeholder
clips for the generated b-roll (zero credits), so you can check the cut, captions, crop and
pacing before the real run. `python3 squads/video-production/scripts/doctor.py` checks the local
tooling. In Claude Code on the web, `.claude/hooks/session-start.sh` installs the tooling
automatically when a session starts.

## Open Art vs Higgsfield

Open Art is the default: cheaper per clip and the quality is good. The squad moves a shot to
Higgsfield when the job needs something Open Art doesn't do from a CLI session, such as
uploading a reference still without a browser, scene analysis of the source footage, motion
transfer, reframing to vertical, upscaling, or a Higgsfield workflow (subtitles, Higgsedit).
The full decision table, model list and live credit costs are in
`squads/video-production/playbooks/platform-routing.md`.

## Repo layout

```
.claude/agents/          video-producer, drive-librarian, reels-planner, video-intake,
                         video-story-editor, broll-director, broll-generator, video-editor, video-qa
.claude/skills/          /build-video, /build-reels, /new-video-brief, /new-squad
squads/video-production/ SQUAD.md, playbooks/, templates/, scripts/
squads/_template/        starting point for a new squad
projects/                one folder per job (media is gitignored, plans and reports are not)
PROMPT.md                the master prompt: squad charter + kickoff prompt
CLAUDE.md                house rules every session loads
```

## Requirements

- Claude Code with the Open Art, Higgsfield and GitHub connectors.
- Python 3.10+.
- ffmpeg on PATH, or `pip install imageio-ffmpeg` (bundles a static build; the scripts find it automatically).
- Optional: `pip install gdown` for the Google Drive link-sharing fallback (the Drive connector
  covers private folders).
- Optional: `pip install faster-whisper` for word-level voiceover timestamps (also drives the
  burned-in captions). It downloads a model
  from Hugging Face on first use; where that is blocked (some sandboxes) the squad falls back to a
  timing estimate from the script in the brief. `pip install Pillow` for text on title cards.

```
pip install -r squads/video-production/scripts/requirements.txt
```

## Adding a squad

```
/new-squad social-content
```

That scaffolds `squads/social-content/SQUAD.md`, playbook and template folders, and a starter
agent in `.claude/agents/social-content-lead.md`. Edit the roster, write the playbooks, add a
skill as the entry point, and register the squad in `CLAUDE.md`.
