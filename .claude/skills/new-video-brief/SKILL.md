---
name: new-video-brief
description: "Scaffold a new video project folder (brief.md from the template, asset folders, work and output dirs) for the video-production squad. Use when starting a new video job."
argument-hint: "[slug] [company] [--reels]"
allowed-tools: Bash(mkdir *) Bash(cp *) Bash(touch *) Read Write
---

# /new-video-brief $ARGUMENTS

Create `projects/$0/` for a new video job.

1. `mkdir -p projects/$0/assets/{voiceover,footage,brand,music} projects/$0/work projects/$0/output`
   and `touch projects/$0/assets/{voiceover,footage,brand,music}/.gitkeep`.
2. Copy `squads/video-production/templates/brief.md` (or `templates/brief-reels.md` when
   `--reels` is in the arguments; also create `assets/images/`) to `projects/$0/brief.md`, set
   `slug: $0` and, if given, `company: $1`.
3. Ask the user (one message) for what the template leaves blank: purpose, tone, length,
   deliverables, credit cap, approval mode, logo placement, brand color, must-show / must-avoid,
   and whether inputs will be dropped into `assets/`, listed as URLs, or pulled from Google
   Drive folders (`drive_folders:`; ask for the folder links). For reels also ask: how many
   videos, platforms, length range, caption style, CTA, hooks style. Fill the brief with their
   answers; leave clear placeholders for anything unanswered.
4. Tell them where to put the files and that `/build-video projects/$0` starts the squad.
