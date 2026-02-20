# Agent Instructions

This repo is a **Claude Code plugin** implementing `/xlfg` (Extreme LFG): an evidence-backed SDLC workflow that coordinates independent subagents via file-based context.

## Start here

- Plugin root: `plugins/xlfg-engineering`
- Commands: `plugins/xlfg-engineering/commands/`
- Agents: `plugins/xlfg-engineering/agents/`
- Skills: `plugins/xlfg-engineering/skills/`

## Working agreement

- Keep all `description:` fields short (aim: <= 200 chars) to avoid Claude Code context-budget drops.
- Prefer **file-based context** over long prompts. Put durable guidance in docs, not in monolithic command text.
- Update all three when changing plugin behavior:
  - `plugins/xlfg-engineering/.claude-plugin/plugin.json` (version bump)
  - `plugins/xlfg-engineering/CHANGELOG.md`
  - `plugins/xlfg-engineering/README.md`

## Quality bar

- Commands must be safe-by-default and idempotent where possible.
- No feature is "done" unless verification steps are explicit and repeatable.
- Favor "map not manual": link to deeper docs instead of duplicating large bodies of text.
