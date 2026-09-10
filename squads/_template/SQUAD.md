# __SQUAD__ squad

**Job:** __PURPOSE__

**Entry point:** `/<verb>-<thing> projects/<slug>` (create the skill under `.claude/skills/`)

## Roster

| Agent | Role | Spends money? | Reads | Writes |
|---|---|---|---|---|
| `__SQUAD__-lead` | runs the pipeline, holds gates, reports | no | brief, `work/` | `work/run.log`, final report |
| `__SQUAD__-<role>` | ... | ... | ... | ... |

Agents live in `.claude/agents/__SQUAD__-*.md`. Give each the minimum tool list; name MCP tools
explicitly (`mcp__<server>__<tool>`).

## Pipeline and gates

```
1 intake ──► 2 plan ──[approval gate]──► 3 execute ──► 4 review ──► 5 deliver
```

State which gates stop for the user and what the lead must show at each one.

## File contracts (`projects/<slug>/`)

| File | Producer | Schema |
|---|---|---|
| `brief.md` | human | `templates/brief.md` |
| `work/...` | ... | ... |

## Playbooks

- `playbooks/` — the rules the agents follow. Write them before the agents; the agents cite them.

## Scripts

- `scripts/` — stdlib Python helpers the agents run. Keep them deterministic and testable.
