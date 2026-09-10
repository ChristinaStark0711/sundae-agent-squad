# Squads

| Squad | Status | Entry point | Lead agent |
|---|---|---|---|
| [video-production](video-production/SQUAD.md) | active | `/build-video projects/<slug>`, `/build-reels projects/<slug>` | `video-producer` |
| [_template](_template/SQUAD.md) | template | `/new-squad <name>` copies it | — |

Each squad folder holds `SQUAD.md` (roster, pipeline, handoffs), `playbooks/` (the rules the
agents follow), `templates/` (briefs and work files) and `scripts/` (helpers the agents run).
The agents themselves live in `.claude/agents/` so Claude Code can find them; they are prefixed
with the squad name.
