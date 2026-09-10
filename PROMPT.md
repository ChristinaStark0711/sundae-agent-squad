# Master prompts

Two prompts. The **charter** defines the squad and is what you paste into a Claude session (with
this repo open) to build, rebuild or extend the squad. The **kickoff** runs it on a job. A third,
shorter prompt adds a new squad to the repo.

---

## 1. Squad charter (build or extend the squad)

```
You are building a squad of AI agents in the `sundae-agent-squad` repo for Sundae. The repo is
the home for every squad I add for this business, so keep the structure generic: agents in
`.claude/agents/<squad>-*.md`, the squad's playbooks/templates/scripts in `squads/<squad>/`,
jobs in `projects/<slug>/`, an entry-point skill per squad in `.claude/skills/`, and house rules
in `CLAUDE.md`. Media never goes in git.

First squad: **video-production**. Its job, for this project and every future one like it:

- Inputs I provide: a voiceover from the CEO, the usable video clips we have (often not
  enough), and the company logo. Optionally a music bed and a script.
- Output: a finished video that flows smoothly, where generated b-roll fills every gap the
  real footage can't cover and matches the look of the real clips and the meaning of the
  voiceover at that moment. Logo used as a watermark and end card unless the brief says otherwise.
- B-roll is generated on Open Art by default (cheaper, quality is good) and on Higgsfield when
  the job needs it (uploading a local reference still from a CLI session, motion transfer,
  reframe to vertical, upscale, scene analysis, Higgsfield workflows). Both are connected as
  MCP servers; use their real tool names and preflight every cost.
- The squad must be able to run end to end from a brief with minimal input from me, stop for
  approval before spending credits (unless the brief says auto and the plan is under the cap),
  leave a paper trail in `projects/<slug>/work/` so any session can resume, and hand me the mp4,
  a contact sheet, a QA report and a credit summary.

Roster (one subagent each, least-privilege tools):
producer (lead, budget, gates, report) · intake (inventory, transcription with timestamps,
stills, footage notes) · story editor (timed shot list, real footage first, gaps marked) ·
b-roll director (prompt + platform + model + params + credits per gap) · b-roll generator
(executes the plan on Open Art / Higgsfield, downloads and verifies clips, one retry) · editor
(EDL → ffmpeg assembly, logo, music ducking, export, revisions) · QA (checklist, verdict, fix list).

Reels mode, same squad: a librarian that pulls videos, images, voiceovers, music and the logo
from named Google Drive folders (connector first, link-shared fallback) and catalogs them; a
batch planner that mixes and matches them into 9:16 shorts for Instagram Reels, TikTok and
YouTube Shorts with burned-in captions, safe-zone logo, music ducking and an end card; and a
hard gate that builds ONE test video, stops for my confirmation, then builds the rest with my
notes applied batch-wide.

Write the playbooks the agents follow (platform routing with current model ids and prices,
b-roll prompting formula, edit rules, QA checklist), the templates for every file the agents
exchange, the local scripts (probe, transcribe, extract frames, assemble, contact sheet, QA
checks; stdlib Python + ffmpeg), the `/build-video`, `/new-video-brief` and `/new-squad`
skills, a README, and a filled-in brief for the current job. Test the scripts with synthetic
media before you commit.
```

---

## 2. Kickoff (run the squad on a job)

Run real jobs from a local Claude Code session with Google Drive for Desktop, or from a cloud
environment whose Network access is Custom/Full (README, "Where to run it"). The default cloud
environment can plan and dry-run but cannot download media.

```
/build-video projects/sundae-event-video
```

or, in plain language:

```
Use the video-production squad on projects/sundae-event-video. The CEO voiceover, the event
clips and the logo are in assets/ (or listed under assets_urls in brief.md). Follow the brief:
16:9 1080p master, Open Art by default, show me the b-roll plan and its credit cost before
generating, then assemble, QA and give me the mp4, the contact sheet and the QA report.
```

Revision:

```
/build-video projects/sundae-event-video --revise "open on the stage wide, lose the coffee
insert at 0:41, hold the end card a second longer"
```

Fully automatic (brief must have `approval: auto` or pass `--auto`; still capped by `credit_cap`):

```
/build-video projects/sundae-event-video --auto
```

Reels batch from Google Drive (test one first, then the rest):

```
/build-reels projects/sundae-reels
```

then, after watching the test video:

```
/build-reels projects/sundae-reels --continue
```

---

## 3. Add another squad

```
/new-squad social-content "turn a finished video and a brief into platform-specific short cuts,
captions and post copy"
```

Then describe the roster when the skill asks, and it scaffolds `squads/social-content/`,
`.claude/agents/social-content-*.md` and an entry-point skill following the same conventions as
video-production.
