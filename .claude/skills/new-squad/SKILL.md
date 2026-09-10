---
name: new-squad
description: "Scaffold a new AI agent squad in this repo (squads/<name>/ with SQUAD.md, playbooks, templates, scripts, plus a lead agent in .claude/agents/) from squads/_template. Use when asked to add, create or start a new squad."
argument-hint: "[squad-name] \"[one-line purpose]\""
allowed-tools: Bash(mkdir *) Bash(cp *) Bash(sed *) Read Write Edit Glob
---

# /new-squad $ARGUMENTS

Create a squad called `$0` (lowercase, hyphens) whose purpose is `$1`.

1. Refuse if `squads/$0/` or `.claude/agents/$0-lead.md` already exists.
2. `cp -r squads/_template squads/$0` and replace `__SQUAD__` with `$0` and `__PURPOSE__` with
   `$1` in every file under `squads/$0/`.
3. Copy `squads/_template/agents/lead.md` to `.claude/agents/$0-lead.md` with the same
   replacements. Delete `squads/$0/agents/` afterwards (agents live in `.claude/agents/`).
4. Design the roster with the user before writing more agents: for each member, one line each
   for role, what it reads, what it writes, which tools it needs (least privilege, name MCP tools
   explicitly), and whether it spends money. Write each as `.claude/agents/$0-<role>.md` using the
   frontmatter conventions in `.claude/agents/video-producer.md`.
5. Create the entry-point skill `.claude/skills/<verb>-<thing>/SKILL.md` that delegates to
   `$0-lead`, mirroring `.claude/skills/build-video/SKILL.md`.
6. Add the squad to the tables in `CLAUDE.md` and `squads/README.md`.
7. Report the files created and what is still a placeholder.
