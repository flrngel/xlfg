# xlfg-engineering Plugin Development

## Versioning (required)

Every behavior change MUST update:

1. `.claude-plugin/plugin.json` (patch bump)
2. `.cursor-plugin/plugin.json` (patch bump)
3. `CHANGELOG.md`
4. `README.md`
5. `xlfg/__init__.py`
6. `pyproject.toml`
7. `NEXT_AGENT_CONTEXT.md`

Normal evolution should bump **patch** only.

## Read order for future agents

1. `NEXT_AGENT_CONTEXT.md`
2. `README.md`
3. the command files under `commands/`
4. scaffold + tests

Every shipped bundle must contain enough context that the next agent can continue without extra explanation. `NEXT_AGENT_CONTEXT.md` is the required handoff document for this repo.

## Command and agent naming

- Top-level workflow: `/xlfg`
- Subcommands use `xlfg:` prefix: `/xlfg:prepare`, `/xlfg:init`, `/xlfg:recall`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, ...
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
- `/xlfg` must always use deterministic recall before broad repo scanning.
- `/xlfg:plan` must finish before `/xlfg:implement` starts.
- `/xlfg` must never claim success unless verification evidence exists.
- Review is a confirmation gate, not a cleanup crew.

## Docs

Tracked durable artifacts should live under `docs/xlfg/knowledge/` and `docs/xlfg/meta.json` in the target repo.

The single tracked handoff document in a target repo should be `docs/xlfg/knowledge/current-state.md`.

Local episodic run evidence should live under `docs/xlfg/runs/`.

Ephemeral logs should live under `.xlfg/` and should be safe to delete.
