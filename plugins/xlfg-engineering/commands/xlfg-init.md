---
name: xlfg:init
description: Manual bootstrap / repair for xlfg scaffolding in this repo.
---

# /xlfg:init

Use this when you want to explicitly bootstrap or repair the xlfg scaffold.

`/xlfg` itself should normally use `/xlfg:prepare`, not force a full init every run.

## Safety + idempotency rules

- Do not overwrite existing files.
- If a file already exists, only add missing structure.
- Do not modify unrelated docs or tooling.
- Respect the tracking model: tracked cards/events/seed docs, local generated `_views/`, local runs, ephemeral `.xlfg/`.

## What to create or repair

### Tracked

- `docs/xlfg/index.md`
- `docs/xlfg/meta.json`
- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/knowledge/quality-bar-seed.md`
- `docs/xlfg/knowledge/queries.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/cards/README.md`
- `docs/xlfg/knowledge/events/README.md`
- `docs/xlfg/knowledge/cards/<kind>/.gitkeep`
- `docs/xlfg/knowledge/events/.gitkeep`
- `docs/xlfg/knowledge/agent-memory/README.md`
- `docs/xlfg/knowledge/agent-memory/<role>/README.md`
- `docs/xlfg/knowledge/agent-memory/<role>/cards/.gitkeep`
- `docs/xlfg/migrations/`

### Local generated

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/<kind>.md`
- `docs/xlfg/knowledge/_views/agent-memory/<role>.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`
- `docs/xlfg/knowledge/_views/worktree.md`
- `.xlfg/worktree.json`

### Local-only evidence

- `docs/xlfg/runs/`
- `.xlfg/runs/`

### Gitignore

Ensure the repo root `.gitignore` contains:

- `.xlfg/`
- `docs/xlfg/runs/*`
- `!docs/xlfg/runs/.gitkeep`
- `!docs/xlfg/runs/README.md`
- `docs/xlfg/knowledge/_views/`

## Completion

After scaffolding is created or repaired:

- print created paths
- print the scaffold version written to `docs/xlfg/meta.json`
- print the detected worktree context
- confirm that local views were rebuilt
- suggest running `/xlfg <your request>`
