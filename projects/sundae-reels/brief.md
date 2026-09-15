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
brand_color: "#111111"          # TODO Sundae brand background hex (logo folder has Sundae_Favicons-Red.png; confirm the red)
music: library                  # none | library (uses whatever is in the Music folder)
loudness_lufs: -14
platform_preference: openart
credit_cap: 8000              # Open Art 24,000 cr / Higgsfield 1,210 cr available (checked live 2026-09-15); raise this if a batch needs more
approval: ask                   # the test video always stops for confirmation regardless
drive_folders:
  # "Sundae - Videos + Edits" is now split into three subfolders (checked live 2026-09-15):
  # CLOUD SESSION (active): needs the environment's Network access set to Custom/Full and the Drive folder shared "Anyone with the link"
  - {kind: auto, url: "https://drive.google.com/drive/folders/18cZYq7REMliJfiVr4XP298NTVAJBGTXI"}   # Videos
  - {kind: auto, url: "https://drive.google.com/drive/folders/1gIKFk3kAc1Xez6b30z9y8zONCEl4frk5"}   # Pictures
  - {kind: auto, url: "https://drive.google.com/drive/folders/1VzesKHzFyX46vRqfR1OB8C8Y2CMt39b1"}   # Audio: 5 voiceover segments + "FULL DRAFT - all 5 stitched.mp3"
  # - {kind: brand, url: "https://drive.google.com/drive/folders/1Y3zm4TDFlaRc1H89YkZSo7YwQirg8NE0"}  # "Standard Sundae Logos" - see BRAND note below (Sundae_Logo.png, Sundae_Logo-Reversed.png, marks)
  #
  # LOCAL RUN alternative (a Claude Code session on your own Mac with Google Drive for Desktop):
  # comment out the url: lines above and uncomment the path: lines below.
  #
  # macOS (Google Drive for Desktop default mount):
  # - {kind: auto, path: "~/Library/CloudStorage/GoogleDrive-cstark@sundae.com/My Drive/Sundae - Videos + Edits/Videos"}
  # - {kind: auto, path: "~/Library/CloudStorage/GoogleDrive-cstark@sundae.com/My Drive/Sundae - Videos + Edits/Pictures"}
  # - {kind: auto, path: "~/Library/CloudStorage/GoogleDrive-cstark@sundae.com/My Drive/Sundae - Videos + Edits/Audio"}
  # Windows (Google Drive for Desktop default mount - usually drive letter G:):
  # - {kind: auto, path: "G:\\My Drive\\Sundae - Videos + Edits\\Videos"}
  # - {kind: auto, path: "G:\\My Drive\\Sundae - Videos + Edits\\Pictures"}
  # - {kind: auto, path: "G:\\My Drive\\Sundae - Videos + Edits\\Audio"}
  #
  # BRAND / LOGO: "Standard Sundae Logos" is owned by ccrammer@sundae.com and shared with you -
  # shared-with-me folders don't sync into your own My Drive automatically, so there's no
  # reliable local path for it. Simplest fix: open the folder in Drive, download
  # Sundae_Logo.png (and Sundae_Logo-Reversed.png if you want a light-background version) and
  # drop them straight into assets/brand/ in this project (local run), or - in a cloud run - copy
  # them into the Pictures subfolder of "Sundae - Videos + Edits": any image whose name contains
  # "logo" is sorted into assets/brand/ automatically.
drive_output_folder: null       # optional: Drive folder to upload finished reels into
# Note: one photo (IMG_6072 3.HEIC) is an iPhone HEIC. The squad auto-converts HEIC/HEIF to PNG
# during intake (pip install pillow-heif); without that package it's left as-is with a warning.
---

> **Credits, checked live 2026-09-15:** Open Art (Pro) has 24,000 credits, Higgsfield (Plus)
> has 1,210. Plenty for real generation - a 1080p Open Art b-roll shot runs about 120-180
> credits. `--dry-run` still works any time you want a free rehearsal of the cut, captions and
> pacing before spending real credits on a run.

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
