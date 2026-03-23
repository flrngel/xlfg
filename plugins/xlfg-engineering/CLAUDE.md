# xlfg-engineering Plugin Development

## Versioning (required)

Every behavior change MUST update:

1. `CHANGELOG.md`
2. `README.md`
3. `xlfg/__init__.py`
4. `pyproject.toml`
5. `NEXT_AGENT_CONTEXT.md`

Normal evolution should bump **patch** only.

## Read order for future agents

1. `NEXT_AGENT_CONTEXT.md`
2. `docs/planning-autonomy-2026-refresh.md`
3. `README.md`
4. the command files under `commands/`
5. scaffold + tests

Every shipped bundle must contain enough context that the next agent can continue without extra explanation. `NEXT_AGENT_CONTEXT.md` is the required handoff document for this repo.

## Command and agent naming

- Top-level workflow: `/xlfg`
- Subcommands use `xlfg:` prefix: `/xlfg:prepare`, `/xlfg:init`, `/xlfg:recall`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, ...
- Planning agents should write contracts or analysis files.
- Implementation agents should write task-scoped artifacts under `tasks/<task-id>/`.
- New harness-shaping files should usually be added to the run scaffold **only** if they clarify request truth, execution truth, or proof truth.

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep them short:

- Agents: aim <= 200 characters
- Skills/commands: aim <= 200 characters

Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg:prepare` is manual maintenance, not a routine `/xlfg` stage.
- `/xlfg:init` is manual bootstrap / repair only.
- `/xlfg` is autonomous by default; phase commands remain available as escape hatches.
- `/xlfg` must always use deterministic recall before broad repo scanning.
- `/xlfg:plan` must produce a lean run card: `context.md`, `memory-recall.md`, `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`. Optional docs exist only when they change a decision.
- `/xlfg:plan` should stay **lead-owned** and use a small specialist budget by default.
- `/xlfg:plan` must finish before `/xlfg:implement` starts.
- `/xlfg:implement` must stop if `test-readiness.md` is not `READY`.
- `/xlfg` must never claim success unless verification evidence exists and scenario-targeted proof actually ran.
- Review is a confirmation gate, not a cleanup crew.
- Do not let the plan assume the user will implement code or run major repo-local verification later.

## Docs

Tracked durable artifacts should live under `docs/xlfg/knowledge/` and `docs/xlfg/meta.json` in the target repo.

The single tracked handoff document in a target repo should be `docs/xlfg/knowledge/current-state.md`.

Local episodic run evidence should live under `docs/xlfg/runs/`.

Ephemeral logs should live under `.xlfg/` and should be safe to delete.
