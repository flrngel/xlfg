# xlfg-engineering (Claude Code plugin)

`/xlfg` is a **query-first, why-first, recall-first, proof-aware SDLC macro** for Claude Code.

It is designed for:

- long-horizon tasks
- multi-file changes
- user-flow-sensitive product work
- evidence-backed verification and review
- compounding from real failures instead of vague summaries

## Commands

| Command | Purpose |
|---|---|
| `/xlfg` | Macro that runs prepare → recall → plan → implement → verify → review → compound |
| `/xlfg:prepare` | Fast scaffold/version check; compare installed tool version vs repo scaffold version and migrate only on drift |
| `/xlfg:init` | Manual bootstrap / repair of `docs/xlfg/` + `.xlfg/` scaffolding |
| `/xlfg:recall` | Deterministic recall over current-state, knowledge, role memory, the ledger, and local runs |
| `/xlfg:plan` | Reload memory, refine the request into a query contract, write the why, diagnose the root problem, choose the harness profile, and write the shared contracts before coding |
| `/xlfg:implement` | Execute bounded task loops with explicit implementation agents, workboard updates, and proof-aware discipline |
| `/xlfg:verify` | Run profile-aware layered verification + write evidence |
| `/xlfg:review` | Run only the review lenses justified by the harness profile and changed surface |
| `/xlfg:compound` | Convert a run into durable knowledge, role memory, and a refreshed next-agent handoff |

`/xlfg` intentionally mirrors Compound’s macro style: it is a set of other commands, not one giant hidden workflow prompt.

## Key artifact model

Before coding, every serious run should produce:

- `query-contract.md`
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

These are the shared contracts for implementation, verification, review, and compounding. `query-contract.md` is the request truth; later files must trace back to it.

## Tracking model

- `docs/xlfg/knowledge/current-state.md` → tracked handoff doc for the next agent
- latest `docs/xlfg/runs/*/current-state-candidate.md` → local branch/worktree handoff when a feature branch has not promoted a repo-wide update yet
- `docs/xlfg/knowledge/` → tracked durable knowledge
- `docs/xlfg/knowledge/ledger.jsonl` → append-only durable memory events
- `docs/xlfg/runs/` → local episodic evidence, gitignored by default
- `.xlfg/` → ephemeral raw logs, gitignored

This split keeps git clean while preserving local run history for compounding.

## Planning and implementation doctrine

- Start from **why**, not from code shape.
- Use deterministic recall before wide fan-out.
- Load optional agents progressively; do not fan out just because they exist.
- Choose the **minimum honest harness profile** (`quick`, `standard`, `deep`).
- Keep `workboard.md` current; it is the run-truth ledger.
- Keep `proof-map.md` current; green commands are not enough when proof is still vague.
- Review is confirmation, not cleanup.

## Agents

Planning:
- `xlfg-query-refiner`
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
- Certain agents have **role-specific memory** under `docs/xlfg/knowledge/agent-memory/`.
- The first tracked context doc in a target repo should always be `current-state.md`.

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

`/xlfg:recall` is intentionally **deterministic**. It supports temporal run recall and typed lexical query documents, but does not depend on vector search, HyDE, or LLM query expansion. If the helper CLI is absent, the same recall discipline can still be performed directly over the tracked files with `rg`, `find`, and file reads.
