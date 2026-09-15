---
slug: sundae-16x9-short
company: Sundae
title: Sundae short brand story (16:9)
deliverables:
  - {name: master, aspect: "16:9", width: 1920, height: 1080, fps: 30}
target_length_s: 45             # keep this one clearly under a minute; paired with the long-form cut in projects/sundae-event-video/
tone: "confident, quick, human; feels like Sundae, not an ad"
audience: "Sundae site, LinkedIn, sales decks; anyone who needs the story in under a minute"
platform_preference: openart   # Open Art by default; Higgsfield when the routing playbook says so
credit_cap: 3000               # smaller cap than the long-form cut - fewer b-roll shots needed at 45s
approval: ask                  # show the b-roll plan and cost before generating
logo_placement: watermark+endcard
brand_color: "#111111"         # TODO replace with Sundae's confirmed brand background hex
music: none                    # add assets/music/<file> if a licensed bed is available
assets_urls: []                # cloud session: list {kind, url, name} here instead of dropping files
drive_folders:
  # Same three subfolders of "Sundae - Videos + Edits" as the other Sundae projects (checked live 2026-09-15):
  - {kind: auto, url: "https://drive.google.com/drive/folders/18cZYq7REMliJfiVr4XP298NTVAJBGTXI"}   # Videos
  - {kind: auto, url: "https://drive.google.com/drive/folders/1gIKFk3kAc1Xez6b30z9y8zONCEl4frk5"}   # Pictures
  - {kind: auto, url: "https://drive.google.com/drive/folders/1VzesKHzFyX46vRqfR1OB8C8Y2CMt39b1"}   # Audio: 5 voiceover segments + "FULL DRAFT - all 5 stitched.mp3"
  #
  # BRAND / LOGO: any image pulled from the Pictures folder whose name contains "logo" is sorted
  # into assets/brand/ automatically. If nothing lands there, drop a Sundae logo PNG into
  # assets/brand/ directly (see projects/sundae-event-video/brief.md for the full note).
drive_output_folder: null       # optional: Drive folder to upload the finished video into
# Note: one photo (IMG_6072 3.HEIC) is an iPhone HEIC; the squad auto-converts HEIC/HEIF to PNG
# during intake (pip install pillow-heif); without that package it's left as-is with a warning.
voiceover_file: null            # deliberately NOT the "FULL DRAFT - all 5 stitched.mp3" file - see notes below
script: |
  (No fixed script - pick one of the individual voiceover segments per the notes below.)
---

> **Credits, checked live 2026-09-15:** Open Art (Pro) has 24,000 credits, Higgsfield (Plus)
> has 1,210. `--dry-run` still works any time you want a free rehearsal of the cut, captions and
> pacing before spending real credits on a run.

# What this video is

A short, punchy 16:9 cut of the Sundae story for the site, LinkedIn and sales decks - the same
asset library as `projects/sundae-event-video/` (long-form) and `projects/sundae-reels/`
(vertical shorts), but built to land in under a minute. One clear point, made well, not a
compressed version of the long cut.

# Inputs

- Voiceover: pulled from the Audio Drive folder - see "Notes for the squad" for which file to use
- Footage: pulled from the Videos/Pictures Drive folders
- Logo: pulled from the Pictures Drive folder (filename contains "logo") or `assets/brand/`
- Music: none for now

# Must show

- Whatever in the library best represents Sundae's work and team; no single mandatory shot, but favor real footage of people and product over generic b-roll

# Must avoid

- Generated close-up faces presented as Sundae people
- Readable text, signage or logos inside generated clips
- Anything that contradicts what the voiceover says on screen at that moment

# Notes for the squad

- The Audio folder has 5 individual voiceover segments plus one "FULL DRAFT - all 5 stitched"
  file. `projects/sundae-event-video/` already uses the full stitched file for the long-form
  16:9 cut - use ONE of the individual segments here instead (not the stitched draft), so this
  video is naturally short. Pick whichever single segment stands alone best as a complete
  thought with a clear beginning, a point being made, and a natural close; if none stands alone
  cleanly, trim the strongest one to its self-contained core rather than concatenating two.
- Real narrative arc required: a hook in the first 2 seconds, a body that develops that one
  point with specific real footage (not generic filler), a close that lands the point before the
  end card/CTA.
- Match the real footage's look (phone/mirrorless, room light, venue colors) in every generated
  clip; prefer detail inserts, crowd-from-behind and abstract-brand shots for gaps.
- Open Art first; explain any shot routed to Higgsfield.
- Deliver `output/sundae-16x9-short_v1.mp4`, the contact sheet and `work/qa_report.md`.
