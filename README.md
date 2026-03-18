# xlfg-engineering-plugin

`/xlfg` is a **query-first, why-first, recall-first, proof-aware** software development harness for agents building production-grade services.

The core rule in this revision is simple:

> **Do not fan out, code, or verify blindly. Start by reloading the smallest relevant prior truth, define why the work matters, pick the minimum honest harness profile, and then prove the flow with explicit evidence.**

This repository includes:

1. A **Claude Code plugin** (in `plugins/xlfg-engineering`) with `/xlfg`, `/xlfg:prepare`, `/xlfg:recall`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, and `/xlfg:compound`.
2. An optional dependency-free **Python helper CLI** (`xlfg`) that can scaffold, recall, doctor, and verify the same file model locally.
3. A required bundle-level handoff doc: `NEXT_AGENT_CONTEXT.md`.
4. A research + comparison note for this patch: `docs/query-understanding-and-root-solution.md`.

## Read this repo in this order

1. `NEXT_AGENT_CONTEXT.md`
2. `docs/query-understanding-and-root-solution.md`
3. `plugins/xlfg-engineering/README.md`
4. `plugins/xlfg-engineering/commands/xlfg.md`
5. `xlfg/scaffold.py`
6. `tests/test_xlfg.py`

## Quick start (Claude Code)

1. Install the plugin from `plugins/xlfg-engineering`.
2. In your target repo, run:
   - `/xlfg "what you want built"`

`/xlfg` is a **macro command** that orchestrates the subcommands in order:

1. `/xlfg:prepare`
2. `/xlfg:recall`
3. `/xlfg:plan`
4. `/xlfg:implement`
5. `/xlfg:verify`
6. `/xlfg:review`
7. `/xlfg:compound`

Use `/xlfg:init` manually only when you want to bootstrap or repair the scaffold yourself.

## The key artifact model in target repos

Tracked durable knowledge:

- `docs/xlfg/index.md` — map of the knowledge base
- `docs/xlfg/meta.json` — canonical scaffold version and migration state
- `docs/xlfg/knowledge/current-state.md` — the single tracked handoff doc for the next agent
- `docs/xlfg/knowledge/` — decisions, patterns, testing, UX flows, failure memory, harness rules, role memory, and the append-only ledger
- `docs/xlfg/migrations/` — notes written when xlfg versions drift

Local run evidence (gitignored by default):

- `docs/xlfg/runs/<run-id>/query-contract.md` — direct asks, implied asks, quality requirements, developer intention, and the carry-forward anchor
- `docs/xlfg/runs/<run-id>/why.md` — why this work matters and what false success looks like
- `docs/xlfg/runs/<run-id>/harness-profile.md` — minimum honest harness intensity for this run
- `docs/xlfg/runs/<run-id>/workboard.md` — run-truth stage / task ledger
- `docs/xlfg/runs/<run-id>/proof-map.md` — scenario-to-evidence contract
- `docs/xlfg/runs/<run-id>/...` — diagnosis, solution decisions, behavior contracts, plans, scorecards, reviews, summaries
- `.xlfg/runs/<run-id>/verify/` — verification logs + exit codes
- `.xlfg/runs/<run-id>/doctor/` — dev-server and readiness reports

## Why this version is different

### Old failure mode
- request meaning drifted after several steps
- implied asks were easy to drop
- monkey fixes could look green
- recall existed but was not guaranteed to shape `/xlfg`
- coding started before prior failures and harness rules were reloaded
- review and verification had to rescue weak planning / implementation
- all runs paid roughly the same harness cost even when the task was small
- verification could go green while the real proof obligation stayed vague

### New discipline
- `/xlfg` itself now starts with recall and flows into a query-first, why-first planning step
- planning must write `query-contract.md`, `why.md`, `memory-recall.md`, `harness-profile.md`, `workboard.md`, and `proof-map.md` before coding
- harness intensity is selected explicitly (`quick`, `standard`, `deep`) instead of defaulting to maximal fan-out
- optional planning agents are loaded progressively only when the diagnosis justifies them
- verification is green only when command results **and** the proof map agree
- compound updates durable memory and the current-state handoff with why / proof / harness lessons

## What we kept from “super harness” systems, and what we rejected

Adopted:

- explicit task state / workboard
- bounded subagent budgets
- progressive skill / agent loading
- stronger separation between plan state, execution state, and durable memory
- one tracked handoff doc for the next agent

Rejected from the xlfg core path:

- mandatory server runtime / gateway stack
- vector search and semantic memory as a dependency
- giant always-on orchestration complexity for normal product work

The goal is a **production harness skill**, not a research demo.

## Optional local helper CLI

The Python CLI is intentionally secondary. It exists so local workflows can scaffold, recall, doctor, and verify the same file model. The product value is still the plugin workflow.

```bash
python -m pip install -e .
xlfg prepare
xlfg recall yesterday
xlfg recall 'login enter submit'
xlfg verify --mode full
```

## License

MIT
