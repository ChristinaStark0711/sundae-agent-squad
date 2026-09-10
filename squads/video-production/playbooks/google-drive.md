# Google Drive access

## Three ways in, in order of preference

1. **Local mount (no download).** Google Drive for Desktop puts the folder on disk. In
   `brief.md` use `{kind: auto, path: "~/Library/CloudStorage/GoogleDrive-<you>/My Drive/<folder>"}`
   (Windows: `G:\My Drive\<folder>`). `drive_pull.py --from-brief` links the files into
   `assets/` and sorts them by type. Works in local Claude Code sessions only.
2. **Download by file id** (`drive_pull.py --file-id`, gdown). Needs the file or its folder
   shared as *Anyone with the link* and a session whose network can reach `drive.google.com`
   (local sessions, or a cloud environment with **Custom** / **Full** network access; the default
   **Trusted** level blocks it). Check with `doctor.py --network`.
3. **The connector** (`mcp__Google_Drive__*`). Always works for **listing and metadata**
   (`search_files`, `get_file_metadata`) and for **uploading** small files (`create_file`).
   `download_file_content` returns the bytes as base64 inside the tool result; re-emitting that
   through the model corrupts binaries even at a few KB (tested), so treat it as a last resort
   for tiny text-like files only, and always verify the written file opens.

The connector must be enabled per chat in the connector settings. It is the librarian's source
of truth for *what exists* in a folder; how the bytes arrive depends on the session (see the
README's "Where to run it").

| Need | Tool / script |
|---|---|
| list a folder | `search_files` query `parentId = '<folder id>' and (mimeType contains 'video/' or mimeType contains 'image/' or mimeType contains 'audio/')`, paginate with `pageToken` |
| file details | `get_file_metadata` (name, mimeType, size, modifiedTime) |
| local Drive for Desktop folder | `{kind: auto, path: "..."}` in the brief → `scripts/drive_pull.py <project> --from-brief` (links, no download) |
| tiny file, last resort | `download_file_content` → `scripts/drive_pull.py <project> --b64 assets/<kind>/<name>` (base64 on stdin; verify the file opens) |
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

One flat folder with everything in it also works: give it `kind: auto` and the librarian sorts
by file type (videos → footage, photos → images, audio → voiceover unless the name says
music/bed/track, images named logo/mark → brand).

Map them in `brief.md`:

```yaml
drive_folders:
  - {kind: auto,      url: "https://drive.google.com/drive/folders/<id>"}   # flat folder, sorted by type
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
