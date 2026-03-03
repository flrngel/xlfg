# xlfg-engineering Plugin Development

## Versioning (required)

Every behavior change MUST update:

1. `.claude-plugin/plugin.json` (patch bump)
2. `.cursor-plugin/plugin.json` (patch bump)
3. `CHANGELOG.md`
4. `README.md`
5. `xlfg/__init__.py`
6. `pyproject.toml`

Normal evolution should bump **patch** only.

## Command and agent naming

- Top-level workflow: `/xlfg`
- Subcommands use `xlfg:` prefix: `/xlfg:prepare`, `/xlfg:init`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, ...
- Planning agents should write contracts or analysis files.
- Implementation agents should write task-scoped artifacts under `tasks/<task-id>/`.

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep them short:

- Agents: aim <= 200 characters
- Skills/commands: aim <= 200 characters

Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg:prepare` should be fast and idempotent.
- `/xlfg:init` is manual bootstrap / repair only.
- `/xlfg` is a macro; keep the actual workflow in the subcommands.
- `/xlfg:plan` must finish before `/xlfg:implement` starts.
- `/xlfg` must never claim success unless verification evidence exists.

## Docs

Tracked durable artifacts should live under `docs/xlfg/knowledge/` and `docs/xlfg/meta.json` in the target repo.

Local episodic run evidence should live under `docs/xlfg/runs/`.

Ephemeral logs should live under `.xlfg/` and should be safe to delete.
