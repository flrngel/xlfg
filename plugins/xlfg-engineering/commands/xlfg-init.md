---
description: Manual bootstrap / repair for xlfg scaffolding in this repo.
---

# xlfg init

Use this when you want to explicitly bootstrap or repair the xlfg scaffold.

`/xlfg` itself should normally sync scaffold quietly. Use this command only when you intentionally want a manual bootstrap or repair.

## Safety + idempotency rules

- Do **not** overwrite existing files.
- If a file already exists, only add missing sections.
- Do **not** modify unrelated docs or tooling.
- Respect the tracking model: `knowledge/` tracked, `runs/` local-only, `.xlfg/` ephemeral.

## What to create or repair

### Directories

Tracked:
- `docs/xlfg/knowledge/`
- `docs/xlfg/knowledge/agent-memory/`
- `docs/xlfg/migrations/`
- `docs/xlfg/meta.json`

Local-only:
- `docs/xlfg/runs/`
- `.xlfg/runs/`

### Gitignore

Ensure the repo root `.gitignore` contains:

- `.xlfg/`
- `docs/xlfg/runs/*`
- `!docs/xlfg/runs/.gitkeep`
- `!docs/xlfg/runs/README.md`

### Durable knowledge files

Create these if missing:

- `docs/xlfg/index.md`
- `docs/xlfg/knowledge/current-state.md`
- `docs/xlfg/knowledge/quality-bar.md`
- `docs/xlfg/knowledge/decision-log.md`
- `docs/xlfg/knowledge/patterns.md`
- `docs/xlfg/knowledge/testing.md`
- `docs/xlfg/knowledge/ux-flows.md`
- `docs/xlfg/knowledge/failure-memory.md`
- `docs/xlfg/knowledge/harness-rules.md`
- `docs/xlfg/knowledge/ledger.jsonl`
- `docs/xlfg/knowledge/ledger.md`
- `docs/xlfg/knowledge/queries.md`
- `docs/xlfg/knowledge/commands.json`
- role memories under `docs/xlfg/knowledge/agent-memory/`

## Completion

After scaffolding is created or repaired:

- Print created paths
- Print the scaffold version written to `docs/xlfg/meta.json`
- Suggest running `/xlfg <your request>`
