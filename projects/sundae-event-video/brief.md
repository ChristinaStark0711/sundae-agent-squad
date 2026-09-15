---
slug: sundae-event-video
company: Sundae
title: Sundae company event recap
deliverables:
  - {name: master, aspect: "16:9", width: 1920, height: 1080, fps: 30}
target_length_s: null          # voiceover length + end card
tone: "warm, proud, energetic; feels like being in the room"
audience: "Sundae employees, customers and partners; company site and LinkedIn"
platform_preference: openart   # Open Art by default; Higgsfield when the routing playbook says so
credit_cap: 6000              # Open Art 24,000 cr / Higgsfield 1,210 cr available (checked live 2026-09-15); raise this if a batch needs more
approval: ask                  # show the b-roll plan and cost before generating
logo_placement: watermark+endcard
brand_color: "#111111"         # TODO replace with Sundae's brand background hex
music: none                    # add assets/music/<file> if a licensed bed is available
assets_urls: []                # cloud session: list {kind, url, name} here instead of dropping files
drive_folders:
  # "Sundae - Videos + Edits" is now split into three subfolders (checked live 2026-09-15):
  - {kind: auto, url: "https://drive.google.com/drive/folders/18cZYq7REMliJfiVr4XP298NTVAJBGTXI"}   # Videos
  - {kind: auto, url: "https://drive.google.com/drive/folders/1gIKFk3kAc1Xez6b30z9y8zONCEl4frk5"}   # Pictures
  - {kind: auto, url: "https://drive.google.com/drive/folders/1VzesKHzFyX46vRqfR1OB8C8Y2CMt39b1"}   # Audio: segments 1-5 + "FULL DRAFT - all 5 stitched.mp3"
  - {kind: brand, url: "https://drive.google.com/drive/folders/1Y3zm4TDFlaRc1H89YkZSo7YwQirg8NE0"}  # "Standard Sundae Logos"
  # Local session with Google Drive for Desktop? Replace the url: lines above with path: lines (no download at all),
  # pointing at the same three subfolders plus the logos folder, e.g.:
  # - {kind: auto,  path: "~/Library/CloudStorage/GoogleDrive-cstark@sundae.com/My Drive/Sundae - Videos + Edits/Videos"}
  # - {kind: auto,  path: "~/Library/CloudStorage/GoogleDrive-cstark@sundae.com/My Drive/Sundae - Videos + Edits/Pictures"}
  # - {kind: auto,  path: "~/Library/CloudStorage/GoogleDrive-cstark@sundae.com/My Drive/Sundae - Videos + Edits/Audio"}
  # - {kind: brand, path: "~/Library/CloudStorage/GoogleDrive-cstark@sundae.com/Shared drives/<drive>/.../Standard Sundae Logos"}
voiceover_file: "FULL DRAFT - all 5 stitched.mp3"   # the squad uses this one; segments 1-5 are the same read in parts
# Note: one photo (IMG_6072 3.HEIC) is an iPhone HEIC. The squad auto-converts HEIC/HEIF to PNG
# during intake (pip install pillow-heif); without that package it's left as-is with a warning
# and won't be usable, since the bundled ffmpeg can't read HEIC directly.
script: |
  (Paste the CEO's voiceover script here if available. It sharpens timing and lets the story
  editor start before the audio is in.)
---

> **Credits, checked live 2026-09-15:** Open Art (Pro) has 24,000 credits, Higgsfield (Plus)
> has 1,210. Plenty for real generation - a 1080p Open Art b-roll shot runs about 120-180
> credits. `--dry-run` still works any time you want a free rehearsal of the cut, captions and
> pacing before spending real credits on a run.

# What this video is

A recap of Sundae's company event, narrated by the CEO. We filmed the event but don't have
enough usable clips to cover the whole voiceover, so the squad fills the gaps with generated
b-roll that matches the real footage and what the CEO is saying at that moment. It should feel
like a real second camera was there, not like a stock montage.

# Inputs

- Voiceover: `assets/voiceover/` — CEO narration, single track (wav/mp3/m4a)
- Footage: `assets/footage/` — every usable clip from the event, any length, any orientation
- Logo: `assets/brand/` — Sundae logo, transparent PNG (SVG accepted; intake converts it)
- Music: none for now

# Must show

- Every usable real clip should appear at least once if it fits the narration
- The Sundae logo as a watermark through the body and on the end card
- TODO: named moments the CEO refers to (keynote, awards, team activity, venue exterior...)

# Must avoid

- Generated close-up faces presented as Sundae people
- Readable text, signage or logos inside generated clips
- Anything that contradicts what the CEO says on screen at that moment

# Notes for the squad

- Match the real footage's look (phone/mirrorless, room light, venue colors) in every generated clip
- Prefer detail inserts, crowd-from-behind, venue and abstract-brand shots for gaps
- Open Art first; explain any shot routed to Higgsfield
- Deliver `output/sundae-event-video_v1.mp4`, the contact sheet and `work/qa_report.md`
