# Reels format: Instagram Reels, TikTok, YouTube Shorts

One master per video works on all three when it follows these rules. Make platform-specific
variants only if the brief asks.

## Spec

| | Value |
|---|---|
| Canvas | 1080x1920, 9:16, 30 fps (24/25 if all sources are), H.264 High, CRF 18-20, yuv420p, AAC 192 kbps, faststart |
| Length | 15-45 s sweet spot; ≤ 60 s for Reels/Shorts feeds; TikTok allows longer but shorter performs. `max_length_s` in the brief; QA fails above it |
| Loudness | -14 LUFS integrated, -1 dBTP (the platforms normalise to about -14) |
| File size | keep under ~50 MB; CRF 20 if a 60 s video goes over |

## Safe zones (1080x1920)

| Zone | Keep clear of |
|---|---|
| Top 220 px | status bar, "Reels"/"For You" headers |
| Bottom 420 px | caption text, username, sound, CTA buttons |
| Right 130 px | like / comment / share column |
| Left 60 px | edge |

Practical placement: **logo** top-left or top-right at 12-15% width with a 6% margin;
**captions** centred with their baseline at 62-72% of the height (`captions.py --position 0.70`);
**hook text** (if any) at 25-35% height; nothing that must be read in the bottom fifth.

## Structure

1. **Hook (0-2 s)**: the strongest visual and the voiceover's first punchy line, captions on
   from the first word. No fade-in longer than 0.3 s; no logo sting first.
2. **Body**: 1.5-4 s per shot, cut on the words, visual changes every sentence or faster.
   Alternate real footage, images with motion, generated b-roll; never two generated in a row.
3. **End card (2-3 s)**: logo + CTA ("Follow for more", "Link in bio", the brief's line).
   The voiceover's last words may run over it.

## Vertical from horizontal sources

- `fit: cover` with `focus_x` from the library (0 = left, 1 = right) keeps the subject in frame;
  default 0.5 loses the subject in most two-shot or off-centre framings, so set it.
- `fit: blur` (blurred background, full clip inside) only for screen recordings, wide group shots
  or anything a crop destroys. Use it sparingly; it reads as lazy when overused.
- Higgsfield `reframe` (AI outpaint to 9:16) for a hero shot that must stay wide; it costs credits.
- Images: `type: image` with `motion: push-in` (default), `push-out`, `pan-left`, `pan-right`;
  `zoom` 0.10-0.20; 2-3.5 s each. Portrait images crop well; landscape images pan.

## Captions

- Always on. Style `reels` (bold uppercase, thick outline, spoken-word highlight) by default;
  `clean` for corporate; `minimal` (box, sentence case) for calm content. Brief overrides.
- 2-4 words per caption, max 24 characters per line, one line. Never cover a face.
- Timing from the word timestamps; when the transcript is `estimated`, QA must watch for drift
  and the producer should say so in the report.
- Emoji are allowed only if the brief asks; the caption font must then support them.

## Sound

- Voiceover leads. Music from the library (or none) at about -22 dB with ducking; fade out 1.5 s.
- No nat sound from generated clips. Nat sound from real clips only if the brief asks.

## Mix and match

- Every voiceover gets at least one video. Extra videos reuse a voiceover only with a different
  visual set and hook.
- No two videos share more than 50% of their visuals; no asset opens more than one video.
- Rotate energy across the batch (calm / medium / high) and rotate openers (real clip, image,
  generated).
- Batch outputs go to `output/reels/<slug>_r<nn>_<platform>.mp4` with a `batch_report.md`
  listing each video's hook, assets, length, credits and QA verdict.

## Test-first gate

The first video (`r01`) is built alone and shown to the user with its contact sheet. Nothing
else is generated or rendered until they say go. Their notes on the test become batch-wide
settings (caption style, logo placement, crop policy, music level) and are written to
`work/batch.json.meta.approved_settings` before the rest runs.
