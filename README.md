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

## Open Art vs Higgsfield

Open Art is the default: cheaper per clip and the quality is good. The squad moves a shot to
Higgsfield when the job needs something Open Art doesn't do from a CLI session, such as
uploading a reference still without a browser, scene analysis of the source footage, motion
transfer, reframing to vertical, upscaling, or a Higgsfield workflow (subtitles, Higgsedit).
The full decision table, model list and live credit costs are in
`squads/video-production/playbooks/platform-routing.md`.

## Repo layout

```
.claude/agents/          video-producer, video-intake, video-story-editor, broll-director,
                         broll-generator, video-editor, video-qa
.claude/skills/          /build-video, /new-video-brief, /new-squad
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
- Optional: `pip install faster-whisper` for word-level voiceover timestamps. It downloads a model
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
