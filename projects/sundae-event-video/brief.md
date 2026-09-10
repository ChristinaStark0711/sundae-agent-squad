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
credit_cap: 2500               # TODO confirm: total credits across Open Art + Higgsfield for this build
approval: ask                  # show the b-roll plan and cost before generating
logo_placement: watermark+endcard
brand_color: "#111111"         # TODO replace with Sundae's brand background hex
music: none                    # add assets/music/<file> if a licensed bed is available
assets_urls: []                # cloud session: list {kind, url, name} here instead of dropping files
script: |
  (Paste the CEO's voiceover script here if available. It sharpens timing and lets the story
  editor start before the audio is in.)
---

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
