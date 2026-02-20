# xlfg-engineering Plugin Development

## Versioning (required)

Every behavior change MUST update:

1. `.claude-plugin/plugin.json` (semver bump)
2. `CHANGELOG.md`
3. `README.md`

## Command and agent naming

- Top-level workflows: `/xlfg`, `/lfg`, `/slfg`
- Subcommands use `xlfg:` prefix: `/xlfg:init`, `/xlfg:verify`, ...

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep them short:

- Agents: aim <= 200 characters
- Skills/commands: aim <= 200 characters

Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg:init` must be idempotent.
- `/xlfg` must never claim success unless verification evidence exists.

## Docs

Durable artifacts should live under `docs/xlfg/` in the target repo.

Ephemeral logs should live under `.xlfg/` and should be safe to delete.
