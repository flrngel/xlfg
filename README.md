# xlfg-engineering-plugin

`/xlfg` is a **recall-first, diagnosis-first, contract-shared** software development workflow for agents building production-grade services.

The core rule in this revision is simple:

> **Do not fan out, code, or verify blindly. Start by recalling the smallest relevant prior truth, then define the problem, the flow, the test contract, and the environment contract.**

This repository includes:

1. A **Claude Code plugin** (in `plugins/xlfg-engineering`) with `/xlfg`, `/xlfg:prepare`, `/xlfg:recall`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, and `/xlfg:compound`.
2. An optional dependency-free **Python helper CLI** (`xlfg`) that can scaffold, recall, doctor, and verify the same file model locally.
3. A required bundle-level handoff doc: `NEXT_AGENT_CONTEXT.md`.

## Read this repo in this order

1. `NEXT_AGENT_CONTEXT.md`
2. `plugins/xlfg-engineering/README.md`
3. `plugins/xlfg-engineering/commands/xlfg.md`
4. `xlfg/scaffold.py`
5. `tests/test_xlfg.py`

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
- `docs/xlfg/knowledge/` — decisions, patterns, test learnings, UX flows, failure memory, harness rules, role memory, and the append-only ledger
- `docs/xlfg/migrations/` — notes written when xlfg versions drift

Local run evidence (gitignored by default):

- `docs/xlfg/runs/<run-id>/` — diagnosis, solution decisions, contracts, plans, scorecards, reviews, summaries
- `.xlfg/runs/<run-id>/verify/` — verification logs + exit codes
- `.xlfg/runs/<run-id>/doctor/` — dev-server and readiness reports

## Why this version is different

### Old failure mode
- recall existed but was not guaranteed to shape `/xlfg`
- coding started before prior failures and harness rules were reloaded
- review and verification had to rescue weak planning / implementation
- target repos had shared knowledge but no single handoff doc for the next agent

### New discipline
- `/xlfg` itself now starts with recall
- planning must write `memory-recall.md` before broad repo fan-out
- a target repo now has `docs/xlfg/knowledge/current-state.md` as a tracked handoff doc
- compound updates both durable memory and the current-state handoff
- more specialist roles can keep compact memory without bloating every prompt

## Deterministic recall, not experimental RAG

This project keeps the useful pieces of `/recall` and QMD while avoiding retrieval machinery that is hard to audit in production.

Adopted:

- temporal recall over local run history
- exact lexical / typed query documents
- stage- and role-aligned memory lookup
- append-only durable memory events in `ledger.jsonl`
- a single tracked handoff document (`current-state.md`) for the next agent

Intentionally omitted from the core path:

- vector search
- HyDE / hypothetical query generation
- LLM query expansion
- mandatory reranking
- graph visualization as a required dependency

The goal is **auditable recall**: the agent should know why a memory matched and where it came from.

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
