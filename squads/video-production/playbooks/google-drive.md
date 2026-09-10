# Google Drive access

## Two paths

| Path | When | How |
|---|---|---|
| **Google Drive connector** (preferred) | the connector is enabled in this chat | `ToolSearch("google drive")` loads its tools: search files, read/download a file by id, upload. Works for private folders. |
| **Link fallback** | connector not enabled, folder shared as *Anyone with the link* | `scripts/drive_pull.py <project> --from-brief` (gdown). Max 50 files per folder, public links only. |

The connector shows as installed on this account but toggled off per chat: enable it in the
chat's connector settings, then start (or restart) the session so the tools load.

## Folder layout the squad expects

```
<Your Drive folder>/
  Footage/     videos (any orientation)
  Images/      stills
  Voiceovers/  one file per voiceover (wav / mp3 / m4a)
  Music/       licensed beds
  Brand/       logo (transparent PNG), brand colors in brief.md
  Output/      (optional) where finished videos are uploaded
```

Map them in `brief.md`:

```yaml
drive_folders:
  - {kind: footage,   url: "https://drive.google.com/drive/folders/<id>"}
  - {kind: images,    url: "https://drive.google.com/drive/folders/<id>"}
  - {kind: voiceover, url: "https://drive.google.com/drive/folders/<id>"}
  - {kind: music,     url: "https://drive.google.com/drive/folders/<id>"}
  - {kind: brand,     url: "https://drive.google.com/drive/folders/<id>"}
drive_output_folder: "https://drive.google.com/drive/folders/<id>"   # optional
```

## Rules

- Read only, unless the producer explicitly asks for an upload to `drive_output_folder`.
- Never delete, move, rename or edit files in Drive.
- Keep original filenames locally; skip a download when the local file exists with the same size.
- Record what was pulled and from where in `work/drive_manifest.json` (file ids when the
  connector is used) so a later session can refresh only what changed.
- Large libraries: catalog everything, download only what the planner picks, if the connector
  can list without downloading. With the fallback, everything in the folder is downloaded.
- Media is gitignored; the catalog (`work/library.json`) can be committed if useful.
