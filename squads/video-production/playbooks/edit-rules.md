# Edit rules

These are defaults. The brief overrides them; taste overrides them when you can say why.

## Structure

1. **Cold open (0-4 s)**: the strongest real moment, cut so the first voiceover word lands on a
   visual beat. If the brief asks for logo-first, a 1.5-2.5 s logo sting on the brand background,
   then the open.
2. **Body**: the voiceover, covered shot by shot. Chapters follow the voiceover's ideas.
3. **End card (3-4 s)**: logo centered on the brand background, optional one-line tagline or URL
   if the brief supplies it. The voiceover should finish 0.5-1 s before the card, or the last
   words can sit over the card if the line is a closer.

Target length = voiceover length + end card, unless the brief sets a length.

## Pacing

- 2-6 s per shot. Under 1.5 s reads as a glitch; over 7 s needs a reason (a slow reveal, a
  strong real moment).
- Cut on phrase boundaries and on the beat of the delivery. Use the word timestamps.
- Alternate scale: wide → medium → detail. Never three of the same in a row.
- Real footage at least half the runtime when the footage allows. Never three generated shots
  in a row if a real one is available.
- Match energy: a static shot under an energetic line feels dead; a fast push under a reflective
  line feels cheap.
- Match motion direction across a cut when both shots move (left-to-right stays left-to-right).

## Transitions

- Hard cuts by default.
- Crossfade 0.4-0.5 s only between two generated shots or at a chapter change.
- Fade from black 0.5 s at the start; fade to black 1.0 s at the end (after the end card hold).
- No wipes, no zoom transitions, no light leaks.

## Framing and format

- Master: 1920x1080, 30 fps (match the footage's fps if it is uniformly 24 or 25), H.264 High,
  CRF 18, yuv420p, AAC 192 kbps, faststart. Vertical variant by `reframe` on Higgsfield or a
  second EDL with `fit: cover` on a 1080x1920 canvas.
- `fit: cover` (scale + center crop) for footage close to the canvas ratio. `fit: contain` with a
  brand-color or blurred pad only when a crop loses the subject.
- Phone footage shot vertical: crop to 16:9 only if the subject survives; otherwise use it as
  a contained insert with a blurred pad, and prefer generated or other real shots.

## Logo

- Watermark: bottom-right, 6-8% of frame width, 80-90% opacity, 3% margin, from the end of the
  cold open to the start of the end card. Skip it if the brief says clean.
- End card: logo at 30-35% of frame width, centered, on the brand background color.
- Never stretch, recolor or crop the logo. Transparent PNG only; convert SVG first.

## Audio

- Voiceover is the master. Normalize the mix with `loudnorm` to about -16 LUFS integrated,
  -1.5 dBTP.
- Music (only if supplied and licensed): about -22 dB under the voice, `duck: true`
  (sidechain against the voiceover), fade out over the last 2 s. No music under the first
  voiceover word unless the brief asks.
- Nat sound from real clips: optional, low (-24 dB), never under the voiceover's first sentence.
- Generated clips are silent in the mix.

## Color

- Keep the real footage as shot. If generated clips are visibly more saturated or contrasty,
  pull them toward the footage rather than the other way. The assemble script does not grade;
  ask the b-roll director to re-prompt the look instead.

## Versioning

`output/<slug>_v1.mp4`, `_v2`, ... Keep every EDL as `work/edl_v<N>.json`. Note what changed
in `work/run.log`.
