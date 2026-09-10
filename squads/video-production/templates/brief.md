---
slug: my-video
company: Company Name
title: Working title
deliverables:
  - {name: master, aspect: "16:9", width: 1920, height: 1080, fps: 30}
# - {name: vertical, aspect: "9:16", width: 1080, height: 1920, fps: 30}
target_length_s: null          # null = voiceover length + end card
tone: "warm, confident, energetic"
audience: "employees and customers"
platform_preference: openart   # openart | higgsfield | auto
credit_cap: 2000               # total credits across platforms for this build
approval: ask                  # ask | auto  (auto proceeds without asking when under credit_cap)
logo_placement: watermark+endcard   # none | endcard | watermark+endcard | opening+endcard
brand_color: "#111111"         # background for logo cards
music: none                    # none | assets/music/<file>
assets_urls: []                # cloud sessions: [{kind: voiceover|footage|brand|music, url: "...", name: "file.ext"}]
script: |
  (Optional. Paste the voiceover script here if you have it; it improves timing when
  transcription is unavailable and lets the story editor plan before the audio arrives.)
---

# What this video is

One paragraph: what it is for, where it will be shown, what the viewer should feel and do.

# Inputs

- Voiceover: `assets/voiceover/<file>` — who is speaking, roughly how long
- Footage: `assets/footage/` — what was filmed, on what, anything to avoid
- Logo: `assets/brand/<file>` — transparent PNG preferred
- Music: none / `assets/music/<file>` (licensed)

# Must show

- moments, people (with consent), places, products that have to be in the cut

# Must avoid

- anything not to show or imply

# Notes for the squad

- style references, previous videos, anything else
