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
2. `docs/branch-safe-knowledge.md`
3. `README.md`
4. the command files under `commands/`
5. scaffold + tests

Every shipped bundle must contain enough context that the next agent can continue without extra explanation. `NEXT_AGENT_CONTEXT.md` is the required handoff document for this repo.

## Command and agent naming

- Top-level workflow: `/xlfg`
- Subcommands use `xlfg:` prefix: `/xlfg:prepare`, `/xlfg:init`, `/xlfg:recall`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, ...
- Planning agents should write contracts or analysis files.
- Implementation agents should write task-scoped artifacts under `tasks/<task-id>/`.
- New harness-shaping files should usually be added to the run scaffold **only** if they clarify execution truth or proof truth.

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
- `/xlfg:plan` must write `why.md`, `harness-profile.md`, `workboard.md`, and `proof-map.md` before implementation.
- `/xlfg:plan` should load optional agents progressively instead of always fanning out.
- `/xlfg:plan` must finish before `/xlfg:implement` starts.
- `/xlfg` must never claim success unless verification evidence exists and the proof map is honest.
- Review is a confirmation gate, not a cleanup crew.
- `/xlfg:compound` must write immutable cards/event files, not edit shared generated views.

## Docs

### Tracked durable artifacts in target repos

- `docs/xlfg/meta.json`
- `docs/xlfg/index.md`
- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/cards/`
- `docs/xlfg/knowledge/events/`
- `docs/xlfg/knowledge/agent-memory/<role>/cards/`
- `docs/xlfg/migrations/`

### Local generated read models in target repos

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/*.md`
- `docs/xlfg/knowledge/_views/agent-memory/*.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`
- `docs/xlfg/knowledge/_views/worktree.md`

### Local run evidence

- `docs/xlfg/runs/`
- `.xlfg/`
