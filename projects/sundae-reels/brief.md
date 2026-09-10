---
slug: sundae-reels
company: Sundae
mode: reels
platforms: [instagram, tiktok, shorts]
count: 6                        # TODO how many videos in the first batch (video 1 is the test)
length_range_s: [20, 45]
max_length_s: 60
canvas: {width: 1080, height: 1920, fps: 30}
tone: "confident, quick, human; feels like Sundae, not an ad"
themes: ["what Sundae does", "the team", "customer wins", "behind the scenes"]   # TODO
hooks_style: "bold claim or question in the first line, captions from word one"
cta: "Follow for more"          # TODO
captions: {style: reels, highlight: true, position: 0.70, color: "#FFFFFF", accent: "#FFD400"}   # TODO accent = brand color
logo_placement: top-left
brand_color: "#111111"          # TODO Sundae brand background hex
music: library                  # none | library (uses whatever is in the Music folder)
loudness_lufs: -14
platform_preference: openart
credit_cap: 3000                # TODO total credits across Open Art + Higgsfield for the whole batch
approval: ask                   # the test video always stops for confirmation regardless
drive_folders:
  - {kind: footage,   url: "https://drive.google.com/drive/folders/REPLACE_FOOTAGE"}
  - {kind: images,    url: "https://drive.google.com/drive/folders/REPLACE_IMAGES"}
  - {kind: voiceover, url: "https://drive.google.com/drive/folders/REPLACE_VOICEOVERS"}
  - {kind: music,     url: "https://drive.google.com/drive/folders/REPLACE_MUSIC"}
  - {kind: brand,     url: "https://drive.google.com/drive/folders/REPLACE_BRAND"}
drive_output_folder: null       # optional: Drive folder to upload finished reels into
---

# What these videos are

Short vertical videos for Sundae's Instagram Reels, TikTok and YouTube Shorts, built from the
voiceovers, clips and photos in the Drive folders above, mixed and matched so each video feels
different, with generated b-roll only where the library has nothing that fits. Every video has
burned-in captions, the Sundae logo in the safe zone, and an end card with the CTA.

# Must show

- TODO: people, products, places or moments that should appear across the batch

# Must avoid

- Generated close-up faces presented as Sundae people
- Readable text, signage or logos inside generated clips
- Anything in the bottom fifth of the frame that has to be read (platform UI covers it)

# Notes for the squad

- Build the test video (r01) from the strongest voiceover and the best real footage; stop and show it before anything else
- Apply my notes on the test to the whole batch
- Open Art first for b-roll; explain any shot routed to Higgsfield
