# xlfg-engineering (Claude Code plugin)

`/xlfg` is a **why-first, recall-first, proof-aware SDLC macro** for Claude Code.

The defining change in **2.0.6** is that xlfg now uses a **branch-safe knowledge model**:

- tracked memory is written as immutable cards and immutable event files
- worktree-local `_views/` files are generated read models
- `/xlfg:compound` no longer asks branches to edit the same shared rollup docs

## Commands

| Command | Purpose |
|---|---|
| `/xlfg` | Macro that runs prepare → recall → plan → implement → verify → review → compound |
| `/xlfg:prepare` | Fast scaffold/version check; records git worktree context and rebuilds local knowledge views |
| `/xlfg:init` | Manual bootstrap / repair of `docs/xlfg/` + `.xlfg/` scaffolding |
| `/xlfg:recall` | Deterministic recall over generated views, immutable cards/events, role memory, and local runs |
| `/xlfg:plan` | Reload memory, define why, diagnose the real problem, choose the harness profile, and write shared contracts |
| `/xlfg:implement` | Execute bounded task loops with explicit implementation agents, workboard updates, and proof-aware discipline |
| `/xlfg:verify` | Run profile-aware layered verification + write evidence |
| `/xlfg:review` | Run the review lenses justified by the harness profile and changed surface |
| `/xlfg:compound` | Promote reusable lessons into immutable cards/events and rebuild local views |

## Key artifact model

Before coding, every serious run should produce:

- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`

These are the shared contracts for implementation, verification, review, and compounding.

## Tracking model

### Tracked write model

- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/cards/<kind>/<branch-slug>/...`
- `docs/xlfg/knowledge/events/<branch-slug>/...json`
- `docs/xlfg/knowledge/agent-memory/<role>/cards/<branch-slug>/...`
- `docs/xlfg/meta.json`

### Local read model

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/<kind>.md`
- `docs/xlfg/knowledge/_views/agent-memory/<role>.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`
- `docs/xlfg/knowledge/_views/worktree.md`

### Local evidence

- `docs/xlfg/runs/` → local episodic evidence, gitignored by default
- `.xlfg/` → ephemeral raw logs, gitignored

This split avoids PR conflicts while keeping the next-agent handoff fast inside each worktree.

## Planning and implementation doctrine

- Start from **why**, not from code shape.
- Use deterministic recall before wide fan-out.
- Load optional agents progressively; do not fan out just because they exist.
- Choose the **minimum honest harness profile** (`quick`, `standard`, `deep`).
- Keep `workboard.md` current; it is execution truth.
- Keep `proof-map.md` current; it is proof truth.
- Review is confirmation, not cleanup.
- Compound writes immutable lessons; `_views/` are regenerated afterward.

## Agents

Planning:
- `xlfg-why-analyst`
- `xlfg-repo-mapper`
- `xlfg-root-cause-analyst`
- `xlfg-spec-author`
- `xlfg-test-strategist`
- `xlfg-env-doctor`
- `xlfg-solution-architect`
- `xlfg-harness-profiler`
- `xlfg-risk-assessor`
- `xlfg-brainstorm`
- context investigators / researcher when needed

Implementation:
- `xlfg-test-implementer`
- `xlfg-task-implementer`
- `xlfg-task-checker`

Verify:
- `xlfg-verify-runner`
- `xlfg-verify-reducer`

Review:
- `xlfg-security-reviewer`
- `xlfg-performance-reviewer`
- `xlfg-ux-reviewer`
- `xlfg-architecture-reviewer`

Subagent model:
- `/xlfg` subagents use `sonnet`.
- High-value specialists can read role-specific generated views under `docs/xlfg/knowledge/_views/agent-memory/`.
- Durable role memory is promoted as tracked cards under `docs/xlfg/knowledge/agent-memory/<role>/cards/`.

## Skills

- `xlfg-file-context`
- `xlfg-quality-gates`
- `xlfg-recall`

## Installation

Point Claude Code at `plugins/xlfg-engineering` as a plugin directory.

## Versioning

Only patch versions are bumped in normal evolution. Update all of these together:

- `xlfg/__init__.py`
- `pyproject.toml`
- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`
- `plugins/xlfg-engineering/CHANGELOG.md`
- `plugins/xlfg-engineering/README.md`
- `NEXT_AGENT_CONTEXT.md`

## Recall model

`/xlfg:recall` is intentionally deterministic. It supports temporal run recall and typed lexical query documents, but does not depend on vector search, HyDE, or LLM query expansion. If the helper CLI is absent, the same recall discipline can still be performed directly over the tracked cards/events and local generated views.
