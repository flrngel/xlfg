# xlfg-engineering Plugin Development

## Versioning (required)

Every behavior change MUST update:

1. `.claude-plugin/plugin.json` (semver bump)
2. `.cursor-plugin/plugin.json` (semver bump)
3. `CHANGELOG.md`
4. `README.md`
5. `xlfg/__init__.py`

## Command and agent naming

- Top-level workflow: `/xlfg`
- Subcommands use `xlfg:` prefix: `/xlfg:init`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, ...
- Planning agents should write contracts or analysis files.
- Implementation agents should write task-scoped artifacts under `tasks/<task-id>/`.

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep them short:

- Agents: aim <= 200 characters
- Skills/commands: aim <= 200 characters

Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg:init` must be idempotent.
- `/xlfg` is a macro; keep the actual workflow in the subcommands.
- `/xlfg:plan` must finish before `/xlfg:implement` starts.
- `/xlfg` must never claim success unless verification evidence exists.

## Docs

Durable artifacts should live under `docs/xlfg/` in the target repo.

Ephemeral logs should live under `.xlfg/` and should be safe to delete.
