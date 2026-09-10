---
name: build-video
description: "Run the video-production squad end-to-end on a project folder (brief + voiceover + footage + logo) to produce a finished video with generated b-roll from Open Art or Higgsfield. Use when asked to build, assemble, produce or revise a video from a brief."
argument-hint: "[project-dir] [--auto] [--draft] [--dry-run] [--revise \"notes\"]"
---

# /build-video $ARGUMENTS

Produce a finished video for the project at `$0` (for example `projects/sundae-event-video`).

Flags anywhere in the arguments:
- `--auto` — treat the brief as `approval: auto` for this run (still capped by `credit_cap`)
- `--draft` — stop after a 540p draft render instead of the master
- `--revise "notes"` — revision of the latest version; rerun from the earliest phase the notes touch
- `--dry-run` — no credits: labelled placeholder clips stand in for generated b-roll so the whole pipeline can be rehearsed

## Do this

1. Confirm the project exists and read `brief.md`. If it does not exist, say so and offer
   `/new-video-brief <slug>`.
2. Delegate the whole build to the **`video-producer`** subagent with: the project path, the
   flags above, the brief's constraints, and the user's notes if any. The producer runs the seven
   phases in `squads/video-production/SQUAD.md`, delegates to the other squad members, and holds
   the gates.
3. When the producer stops at a gate (missing inputs, cost approval, failed shots, QA loop
   exhausted), relay its question to the user in one message with the numbers and a recommended
   answer. Resume the producer with the user's decision (same subagent, via SendMessage, so it
   keeps its context).
4. When the producer finishes, relay its final report unchanged, then send the video and the
   contact sheet to the user if a file-sending tool exists.

## Rules

- No paid generation before the cost gate has been passed (brief `approval: auto` or `--auto`,
  and plan total ≤ `credit_cap`), or the user has approved in this conversation.
- Never pass `use_unlim` unless the user asked for it here.
- Never commit media. Do commit `brief.md` and the JSON/Markdown in `work/` if the user asks to save the run.
- If the Open Art or Higgsfield tools are not available in this session, say which and stop
  before phase 3; the local phases (intake, story, edit of real footage only) still work.
