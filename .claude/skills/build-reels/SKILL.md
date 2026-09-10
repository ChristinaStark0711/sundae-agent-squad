---
name: build-reels
description: "Run the video-production squad in reels mode: pull videos, images, voiceovers, music and the logo from the Google Drive folders in a project brief, plan a mix-and-match batch of 9:16 short videos with burned-in captions for Instagram Reels, TikTok and YouTube Shorts, build ONE test video and stop for confirmation, then build the rest with --continue. Use when asked for reels, shorts, TikToks, vertical videos or a batch of social videos from a Drive library."
argument-hint: "[project-dir] [--count N] [--continue] [--auto] [--revise \"notes\"]"
---

# /build-reels $ARGUMENTS

Produce a batch of 9:16 captioned short videos for the project at `$0`.

Flags anywhere in the arguments:
- `--count N` — override the brief's `count`
- `--continue` — the test video was approved; build the remaining videos from `work/batch.json`
- `--auto` — skip the batch-plan cost question (the test-video stop still happens)
- `--revise "notes"` — apply notes to the test video (or to a named video id) and re-render it

## Do this

1. Confirm `$0/brief.md` exists and has `mode: reels` and `drive_folders:` (or assets already in
   `assets/`). If not, offer `/new-video-brief $0 --reels`.
2. Delegate to the **`video-producer`** subagent in reels mode with the project path, the flags,
   the brief's constraints and any user notes. The producer runs R0-R5 from
   `.claude/agents/video-producer.md`: library → transcripts → batch plan → **test video, then
   stop** → (on `--continue`) the rest → deliver.
3. On the first run, end your turn after the producer presents the test video: the file, its
   contact sheet, the credits spent, the plan for the remaining videos, and the question "go
   ahead with the rest as planned, or change something first?". Do not build more.
4. On `--continue`, relay the producer's per-video progress only at the end (or when it stops
   for a failure or the credit cap), then the batch report and the Drive links if uploaded.
5. If a file-sending tool exists, send the test video and the final batch report.

## Rules

- The test video always stops for confirmation, even with `--auto` or `approval: auto`.
- No paid generation before the batch plan's cost has been shown (or `--auto`) and never past
  `credit_cap`. Never pass `use_unlim` unless the user asked here.
- The user's notes on the test video become batch-wide settings; write them into
  `work/batch.json` under `meta.approved_settings` before continuing.
- If the Google Drive connector isn't enabled in this chat, say so with the fix and use the
  link-sharing fallback if the folders are shared by link; otherwise stop.
