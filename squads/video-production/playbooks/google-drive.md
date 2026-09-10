# Google Drive access

## What the connector can and cannot do

The Google Drive connector (`mcp__Google_Drive__*`) can **list and describe** any file the
account can see (`search_files`, `get_file_metadata`, `list_recent_files`), **download small
files inline** as base64 (`download_file_content`, fine for a logo, a photo, a short audio clip;
not for a 300 MB video), and **upload** (`create_file`). It must be enabled per chat in the
connector settings.

Large media therefore comes down by file id with `gdown`, which needs the file or its folder
shared as *Anyone with the link* (view only). Recommended setup: share the one parent folder by
link once; keep the connector for listing, cataloguing and uploads.

| Need | Tool / script |
|---|---|
| list a folder | `search_files` query `parentId = '<folder id>' and (mimeType contains 'video/' or mimeType contains 'image/' or mimeType contains 'audio/')`, paginate with `pageToken` |
| file details | `get_file_metadata` (name, mimeType, size, modifiedTime) |
| small file (< ~5 MB) | `download_file_content` → `scripts/drive_pull.py <project> --b64 assets/<kind>/<name>` with the base64 on stdin |
| video / big file | `scripts/drive_pull.py <project> --file-id <id> --kind <kind> --name "<name>"` (link-shared) |
| whole link-shared folder | `scripts/drive_pull.py <project> --from-brief` (50 files per folder max) |
| upload a result | `create_file` with `parentId`, `title`, `contentMimeType`, `base64Content`, `disableConversionToGoogleType: true` (small files) |
| check visibility | `get_file_permissions` on the folder id |

Folder id = the part of the folder URL after `/folders/`.

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
