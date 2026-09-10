# Writing b-roll prompts

A b-roll clip has to cut invisibly next to real footage shot on real cameras at a real event.
Write for that, not for a showreel.

## The formula (40-90 words, one paragraph)

`[shot + camera move] [subject] [action] [setting] [lighting / time] [lens / format / grade] [mood]. [exclusions]`

Example for a line like "we brought the whole company together":

> Wide handheld shot, slow push-in, a modern conference room filling with people seen from behind
> and in profile, taking seats and greeting each other, warm tungsten room light mixed with
> daylight from tall windows, shot on a mirrorless camera at 35 mm, natural color, slight film
> grain, lively and welcoming. No on-screen text, no logos, no signage, no captions, nobody
> looking into the lens.

## Match the real footage

Read the **Look profile** in `work/footage_notes.md` and carry it into every prompt:

- color temperature and grade (warm tungsten hall vs cool daylight office)
- camera feel (handheld phone, gimbal, tripod) and lens (wide phone look vs 50 mm)
- resolution and grain (phone footage is clean and slightly flat; don't ask for anamorphic flares)
- venue details that recur (wood floors, white walls, stage lights, branded backdrop color)

Generated shots should look like a second camera operator at the same event.

## Choose the mode

| Need | Mode | Prompt focus |
|---|---|---|
| Generic cutaway, new scene | `text2video` | full formula |
| Must be **this** venue / product / table, and a still exists | `image2video` (`startFrame`) | describe only the **motion** and what changes: "slow push-in, people cross frame, light stays" |
| Same subject in a new setting across several shots | `element2video` | describe the new scene, name the subject as "the [object] in the reference" |
| Start on one frame and land on another | `image2video` with `endFrame` | describe the transition |

For `image2video`, never re-describe the scene in detail; the model has it. Describe camera,
motion, duration of the move, and what must stay still.

## Shot vocabulary that cuts well

- **Establishing**: wide, slow push or lateral drift, 5-6 s.
- **Detail inserts**: hands on laptops, name badges on a table, coffee cups, lanyards, a phone
  filming the stage, cables being plugged, sticky notes, a whiteboard being written on. 3-4 s.
- **Crowd energy without faces**: from behind, over shoulders, silhouettes against stage light,
  applause hands, people walking into frame out of focus. 4-5 s.
- **Place and time**: exterior of a building at golden hour, city street, an office at dusk,
  a sign-free lobby. 5 s.
- **Abstract brand**: soft bokeh in the brand colors, light through glass, slow-moving fabric or
  confetti, particles. 4-5 s. Use sparingly.
- **Product / screens**: a dashboard on a monitor (say "abstract UI, no readable text"), a
  device on a desk, a delivery box, whatever the company actually sells.

## Exclusions, always at the end

`No on-screen text, no logos, no signage, no captions, no watermarks, no subtitles.` Add
`nobody looking into the lens` for crowd shots, `hands natural, five fingers` for any hands
insert, and `no distortion, straight architecture` for interiors.

## People

Generated people are extras, not staff. Keep them mid-distance, turned away, in profile, out of
focus or in silhouette. Do not prompt for a close-up "CEO", "founder" or "employee" face. Do not
put a real person's likeness in a prompt or a reference unless the brief says they consented.

## Parameters

- Duration: shot length rounded up to the model's allowed value; 5 s default; 6-8 s for wides.
- Aspect ratio from the brief (16:9 default; 9:16 only if the deliverable is vertical).
- Audio off (`generateAudio: false`, `generate_audio: false`, `sound: "off"`); the voiceover is
  the soundtrack. Nat sound from the real clips can be mixed in by the editor if wanted.
- Resolution: 720p cuts fine into a 1080p master for short inserts; use 1080p for wides and any
  shot longer than 5 s. Only go 2K/4K if the master is 4K.

## Before you submit

Read the prompt as the model will: is the subject unambiguous, is there exactly one camera move,
does it match the look profile, does it end with the exclusions, is it under 90 words?
