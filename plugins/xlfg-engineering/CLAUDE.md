# xlfg-engineering Plugin Development

## Versioning (required)

Every behavior change MUST update:

1. `CHANGELOG.md`
2. `README.md`
3. `plugins/xlfg-engineering/.claude-plugin/plugin.json`
4. `plugins/xlfg-engineering/.cursor-plugin/plugin.json`
5. `plugins/xlfg-engineering/.codex-plugin/plugin.json`
6. `NEXT_AGENT_CONTEXT.md`

Normal evolution should bump **patch** unless the public entry model changes materially.

## Read order for future agents

1. `NEXT_AGENT_CONTEXT.md`
2. `docs/planning-autonomy-2026-refresh.md`
3. `README.md`
4. `plugins/xlfg-engineering/commands/xlfg.md`
5. `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md`
6. scaffold + tests

Every shipped bundle must contain enough context that the next agent can continue without extra explanation. `NEXT_AGENT_CONTEXT.md` is the required handoff document for this repo.

## Entry model

- Public plugin entrypoint: `/xlfg-engineering:xlfg` (aliased as `/xlfg` via `name: xlfg` in command frontmatter)
- Public standalone entrypoint: `/xlfg`
- Public Codex entrypoints: `$xlfg` and `$xlfg-debug` through `plugins/xlfg-engineering/codex/skills/`
- The main command uses `name: xlfg` to register `/xlfg` as a short alias. Do not remove it.
- Hidden support and phase skills under `plugins/xlfg-engineering/skills/` should stay `user-invocable: false`.
- Do not add Codex `name:` frontmatter to the Claude hidden phase skills; Codex-specific public skills live under `codex/skills/`.
- Do not point a command at a repo-relative plugin file path. Installed plugins are not laid out like the source repo.
- The correct architecture is **one public entrypoint that batches hidden phase skills**.

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep them short:

- Agents: aim <= 200 characters
- Skills/commands: aim <= 220 characters

Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg:init` is manual bootstrap / repair only.
- `/xlfg` is autonomous by default and should not ask the user to run internal phases.
- `/xlfg` must always use deterministic recall before broad repo scanning.
- `/xlfg` must resolve intent before broad repo/context fan-out; the intent contract lives in `spec.md`.
- `/xlfg` must produce a lean run card: `context.md`, `memory-recall.md`, `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`. Optional docs exist only when they change a decision.
- `/xlfg` must stop and repair the plan if `test-readiness.md` is not `READY`.
- `/xlfg` must never claim success unless verification evidence exists and scenario-targeted proof actually ran.
- Review is a confirmation gate, not a cleanup crew.
- Do not let the plan assume the user will implement code or run major repo-local verification later.
- Use current Claude Code tool names in frontmatter (`Skill`, `WebSearch`, `WebFetch`, etc.). Do not reintroduce stale `Task` wording.

## Docs

Tracked durable artifacts should live under `docs/xlfg/knowledge/` and `docs/xlfg/meta.json` in the target repo.

The single tracked handoff document in a target repo should be `docs/xlfg/knowledge/current-state.md`.

Local episodic run evidence should live under `docs/xlfg/runs/`.

Ephemeral logs should live under `.xlfg/` and should be safe to delete.


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.
