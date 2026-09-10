# Platform routing: Open Art vs Higgsfield

Both are connected as MCP servers (`mcp__Open_Art__*`, `mcp__Higgsfield__*`). **Open Art is the
default**: it is cheaper per clip and the quality is good. Move a shot to Higgsfield only for a
reason in the table. Record the reason in `broll_plan.json`.

## Decision table

| Situation | Platform | Why |
|---|---|---|
| Ordinary b-roll from a text prompt | **Open Art** | cheapest per 1080p clip (`veo3-1` lite), broad model choice |
| B-roll that must start from a real still that is already in the Open Art account, or a still generated on Open Art | **Open Art** | `image2video` with `startFrame` |
| B-roll that must start from a real still that only exists on this machine (cloud / CLI session) | **Higgsfield** | `media_upload` gives a presigned PUT; Open Art exposes no CLI upload, only the in-app widget |
| Scene-by-scene analysis of long source footage | Higgsfield | `video_analysis_create` / `video_analysis_status` |
| Copy the camera move or motion of a real clip onto a generated scene | Higgsfield | Genjutsu `hf_mult_motion_control` via `generate_video` |
| Vertical (9:16) or square variant of the master, or of a clip | Higgsfield | `reframe` |
| Upscale a hero shot to 2K / 4K | Higgsfield | `upscale_video` (bytedance or topaz) |
| Burned-in captions, motion graphics, title animation | Higgsfield | workflows `subtitles`, `video-editing` (Higgsedit) |
| 6 or more shots to generate at once in a headless session | either; Higgsfield is simpler | `generate_video_batch` + `jobs_wait` poll up to 12 jobs per call |
| Open Art balance too low, model down, or repeated failure on a shot | Higgsfield | fallback |
| One continuous 20-30 s shot | either | Open Art `wan3-0` or `byte-plus-seedance-2-5`; Higgsfield `seedance_2_5` (4-30 s) |
| Free-trial unlimited generations exist and the **user asked** to use them | Higgsfield | `use_unlim: true`, only on explicit request |

## Open Art models for b-roll (snapshot 2026-09-10; re-check with `openart_model_cost`)

Credits for **one clip at the default configuration**. Other durations / resolutions cost
differently; price the exact config with `openart_model_cost({model, mode, params})`.

| Model id | Default config | Credits | Use it for |
|---|---|---|---|
| `pixverseV6` | 540p, 5 s, no audio | 50 | budget cutaways; stable, natural camera; raise `resolution` to 720p/1080p for a 1080p master |
| `fal-h3-max-turbo` | 480p, 5 s | 100 | proof-of-concept only, too soft for delivery |
| `wan3-0` | 480p, 5 s | 100 | long single shots up to 30 s at 720p/1080p; `mode: "prime"` for higher fidelity |
| `veo3-1` | 1080p, 4 s, audio, `mode: lite` | 120 | **default for 1080p b-roll**; 4/6/8 s; text2video and image2video; `generateAudio: false` |
| `wan2-7` | 720p, 5 s | 125 | most stable image2video from a real still |
| `kling-3-omni` / `kling-v3` | std, 5 s, sound | 175 | detailed 4K-capable shots, multi-shot sequencing; `generateSound: false` |
| `byte-plus-seedance-2-mini` | 720p, 5 s, audio | 200 | realistic people at a distance |
| `gemini-omni-flash` / `gemini-omni-1-1-flash` | 720p, 5 s | 250 | cinematic look; 1.1 goes to 4K and takes video references |
| `byte-plus-seedance-2-5` | 480p, 5 s | 300 | up to 30 s, large reference budget |
| `byte-plus-seedance-2` | 720p, 5 s, audio | 400 | most realistic people and hands |
| `minimax-h3` | 2K, 5 s | 450 | sharp 2K hero shots |

Open Art image models are 10-40 credits; `kling-3-omni` text2image is 10 credits and a good way
to make a reference still that stays inside Open Art (then `openart_upload_metadata_get` on its
URL gives the `startFrame` object).

Mode names on Open Art are the top-level `mode` argument: `text2video`, `image2video`
(the still is the literal first frame), `element2video` (the still is a subject reference in a
new scene). Some models also have a `mode` **form field** inside `params` for quality tier
(`veo3-1`: lite/fast/normal; `wan3-0`: standard/prime). Don't confuse the two.

## Higgsfield models for b-roll (snapshot 2026-09-10; preflight with `get_cost: true`)

| Model id | Notes |
|---|---|
| `seedance_2_5` | Higgsfield's general default; 4-30 s; 480p/720p/1080p; `generate_audio: false`; `mode: omni_reference` with `start_image` / `image_references` |
| `kling3_0` | `mode: std / pro / 4k`; 3-15 s; `sound: "off"`; `start_image` / `end_image` |
| `veo3_1` | 4 / 6 / 8 s; `quality: basic / high / ultra`; `start_image`; ultra-realistic |
| `cinematic_studio_video_v2` | genre and speed-ramp control; 3-12 s |
| `minimax_h3` | 2K, 4-15 s, keyframes and references |
| `gemini_omni_flash_1_1` | up to 4K; `mode: text-to-video / image-to-video / reference-to-video` |
| `hf_mult_motion_control` | Genjutsu motion transfer: images with role `image`, one driving video with role `video` |

Use `models_explore` with `action: "get"` and the model id for the exact parameters, roles and
aspect ratios before submitting.

## Mechanics

### Open Art

1. `openart_model_list` → pick model + mode. `openart_model_form_get(model, mode)` → exact schema.
2. `openart_model_cost({model, mode, params})` → credits for that config.
3. `openart_generate_video({model, mode, params, projectId?})` → `historyId`, status `PENDING`.
4. Poll `openart_creation_get(historyId)`; honour `pollAfterSeconds`; terminal states are
   `COMPLETED`, `FAILED`, `CANCELLED`. Round-robin across submitted jobs.
5. The completed result carries media URLs; download them with `scripts/download.py`.
6. References: `openart_upload_list({includeMetadata: true})` lists account uploads with ready
   reference objects (`{type, id, url, label}`) for `startFrame` / `endFrame` / `visualReferences`.
   `openart_upload_metadata_get({mediaUrl, mediaType})` builds the same object from any Open Art
   media URL (an upload or a generation). There is no CLI upload; the picker widget only works in
   app hosts.
7. `openart_creation_list` shows history; `openart_account_get` shows plan and credits.

### Higgsfield

1. `models_explore({action: "get", model_id})` → parameters, media roles, aspect ratios.
2. Local reference: `media_upload({filename})` → `upload_url` + instructions →
   `curl -f -X PUT --upload-file <file> "<upload_url>"` → `media_confirm` → `media_id`.
   Web reference: `media_import_url({url})` → `media_id`.
3. Preflight: `generate_video({params: {..., get_cost: true}})`.
4. Submit: `generate_video_batch({requests: [{index, params}]})` (1-12 per call, headless) or
   `generate_video` (single, opens a widget in app hosts).
5. Poll: `jobs_wait({jobs: [{index, job_id}]})`, ≤12 per call, ≤15 s per call, repeat until
   `all_terminal`. Then optionally one `show_generation_by_ids` for the whole set.
6. Results carry URLs; download with `scripts/download.py`. A completed `job_id` can be reused as
   a media input (for example in `reframe` or `upscale_video`).
7. If a response contains `adjustments`, apply them; if it names a `recovery_tool`, call it
   immediately. `unlim_choice` means stop and ask the user which balance to use.

### Credits and safety

- Preflight every configuration. Sum per platform. Compare with the brief's `credit_cap` and the
  live balances (`openart_account_get`, Higgsfield `balance`).
- One variant per shot by default. Two only for the opening shot or shots flagged critical.
- Never set `use_unlim` unless the user asked for it in this conversation.
- Downloads and polling are free; generations, upscales, reframes and analyses are not.
