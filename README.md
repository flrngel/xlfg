# xlfg-engineering-plugin

`/xlfg` is a **why-first, recall-first, proof-aware** agent harness for building production-grade services.

The important change in **2.0.6** is the knowledge model:

> **Tracked knowledge is now written as immutable branch-scoped cards and immutable event files. Local `_views/` files are generated read models, not shared write targets.**

That change exists for one reason: multiple branches and linked worktrees were previously fighting over the same tracked rollup files, causing unnecessary PR conflicts and making compounding feel expensive.

This repository includes:

1. A **Claude Code plugin** in `plugins/xlfg-engineering`.
2. An optional dependency-free **Python helper CLI** (`xlfg`) for scaffolding, status, recall, worktree detection, doctoring, and verification.
3. A required repo handoff document: `NEXT_AGENT_CONTEXT.md`.
4. A focused design note for this patch: `docs/branch-safe-knowledge.md`.

## Read this repo in this order

1. `NEXT_AGENT_CONTEXT.md`
2. `docs/branch-safe-knowledge.md`
3. `plugins/xlfg-engineering/README.md`
4. `plugins/xlfg-engineering/commands/xlfg.md`
5. `xlfg/scaffold.py`
6. `xlfg/knowledge.py`
7. `tests/test_xlfg.py`

## Quick start

### Claude Code

1. Install the plugin from `plugins/xlfg-engineering`.
2. In the target repo, run:
   - `/xlfg "what you want built"`

`/xlfg` is a macro that orchestrates:

1. `/xlfg:prepare`
2. `/xlfg:recall`
3. `/xlfg:plan`
4. `/xlfg:implement`
5. `/xlfg:verify`
6. `/xlfg:review`
7. `/xlfg:compound`

Use `/xlfg:init` only for manual bootstrap or repair.

### Optional local helper

```bash
python -m pip install -e .
xlfg prepare
xlfg worktree
xlfg recall 'login enter submit'
xlfg knowledge rebuild
```

## Target-repo file model

### Tracked durable artifacts

- `docs/xlfg/meta.json` — scaffold/tool compatibility manifest
- `docs/xlfg/index.md` — map of the xlfg knowledge model
- `docs/xlfg/knowledge/service-context.md` — stable tracked service context seed
- `docs/xlfg/knowledge/write-model.md` — branch-safe write contract
- `docs/xlfg/knowledge/commands.json` — repo-specific commands, ports, and healthchecks
- `docs/xlfg/knowledge/cards/<kind>/<branch-slug>/<timestamp>--<run-id>--<slug>.md` — immutable shared knowledge cards
- `docs/xlfg/knowledge/events/<branch-slug>/<timestamp>--<run-id>--<slug>.json` — immutable structured memory events
- `docs/xlfg/knowledge/agent-memory/<role>/cards/<branch-slug>/<timestamp>--<run-id>--<slug>.md` — immutable role-specific memory cards
- `docs/xlfg/migrations/` — migration notes when scaffold versions drift

### Local generated read models

- `docs/xlfg/knowledge/_views/current-state.md` — concise next-agent handoff for this worktree
- `docs/xlfg/knowledge/_views/<kind>.md` — generated rollups of shared cards
- `docs/xlfg/knowledge/_views/agent-memory/<role>.md` — generated role-memory rollups
- `docs/xlfg/knowledge/_views/ledger.jsonl` — generated ledger view from immutable event files
- `docs/xlfg/knowledge/_views/worktree.md` — generated git/worktree context and write namespace

### Local evidence (gitignored by default)

- `docs/xlfg/runs/<run-id>/...` — run contracts, plans, proof maps, reviews, summaries
- `.xlfg/runs/<run-id>/...` — raw verify logs, doctor reports, and ephemeral execution traces

## Why this version matters

### Old failure mode

- multiple branches or worktrees edited the same tracked files (`current-state.md`, `patterns.md`, `ledger.jsonl`, role-memory markdown)
- PRs conflicted even when the actual lessons were unrelated
- compounding felt risky, so agents either skipped it or produced noisy manual merges
- generated rollup files became a hidden write target instead of a read model

### Current rule

- **write tracked memory only as immutable cards/events**
- **rebuild `_views/` locally for reading**
- **never hand-edit generated `_views/` on feature branches**

That keeps durable knowledge useful without turning every branch into a merge conflict magnet.

## Core harness discipline

- `/xlfg` must use recall before broad repo fan-out.
- planning must define `why.md`, `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `test-contract.md`, `env-plan.md`, `workboard.md`, and `proof-map.md` before coding
- implementation must follow the diagnosis and proof contract, not shortcut toward a symptom patch
- verification is only green when commands **and** proof obligations agree
- compound promotes only verified, reusable lessons and rebuilds local views afterward

## License

MIT
