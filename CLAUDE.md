# sundae-agent-squad

Home for Sundae's AI agent squads. A squad is a set of Claude Code subagents
(`.claude/agents/<squad>-*.md`) plus the playbooks, templates and scripts they share
(`squads/<squad>/`). Squads do their work inside `projects/<slug>/`.

## Layout

```
.claude/agents/         one file per squad member (Claude Code subagents)
.claude/skills/         slash commands: /build-video, /build-reels, /new-video-brief, /new-squad
squads/<squad>/SQUAD.md roster, pipeline, handoffs for that squad
squads/<squad>/playbooks/  the rules the agents follow (routing, prompting, editing, QA)
squads/<squad>/templates/  brief / shotlist / EDL templates
squads/<squad>/scripts/    stdlib Python + ffmpeg helpers the agents run
projects/<slug>/        one folder per job: brief.md, assets/, work/, output/
PROMPT.md               the master prompt that defines and kicks off a squad
```

## Squads

| Squad | Entry point | What it does |
|---|---|---|
| video-production | `/build-video projects/<slug>` | Voiceover + partial footage + logo in, finished video out. Generates the missing b-roll on Open Art (default) or Higgsfield. |
| video-production (reels mode) | `/build-reels projects/<slug>` | Pulls a library from Google Drive, plans a mix-and-match batch of 9:16 captioned shorts (Reels / TikTok / Shorts), builds one test video, stops for confirmation, then builds the rest with `--continue`. |

Roster and pipeline: `squads/video-production/SQUAD.md`.

## House rules for every squad

1. **Credits are money.** Preflight every generation (`openart_model_cost`, or Higgsfield `get_cost: true`), stay under the brief's `credit_cap`, and stop for approval before the first paid generation unless the brief says `approval: auto`. Never pass `use_unlim` on your own initiative.
2. **Open Art first.** It is cheaper and the quality is good. Switch to Higgsfield only for the reasons in `squads/video-production/playbooks/platform-routing.md`.
3. **Never commit media.** `assets/`, `work/` and `output/` are gitignored. Commit briefs, plans, EDLs, reports and code.
4. **Leave a paper trail.** Every phase writes JSON or Markdown into `projects/<slug>/work/` and appends to `work/run.log`. A new session must be able to resume from those files alone.
5. **Real footage beats generated footage.** Generated b-roll fills gaps and adds texture; it never replaces a usable real clip, and it never fabricates identifiable people as if they were real employees or attendees.
6. **Scripts are stdlib Python + ffmpeg.** ffmpeg comes from PATH or `pip install imageio-ffmpeg`. Optional extras: `faster-whisper` (voiceover timestamps), `Pillow` (title cards).
7. **Test one before many.** Any batch job builds one test video, stops for the user's confirmation, and applies their notes to the rest.
8. **Adding a squad:** run `/new-squad <name>`. It scaffolds `squads/<name>/` and `.claude/agents/<name>-*.md` from `squads/_template/`, then add a row to the table above.

## Tool names

Connected MCP servers appear as `mcp__Open_Art__*`, `mcp__Higgsfield__*`, `mcp__github__*` and
`mcp__Google_Drive__*` (the Drive connector must be enabled per chat; `drive-librarian` falls back
to link-shared folders via `scripts/drive_pull.py` when it isn't).
If a server is connected under a different name in your session, update the `tools:` lines in
`.claude/agents/*.md` (or widen them to `mcp__<server>`).
