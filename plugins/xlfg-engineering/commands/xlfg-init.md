---
name: xlfg:init
description: Initialize xlfg scaffolding (contracts, knowledge, and .xlfg logs) in this repo.
---

# /xlfg:init

Create the durable **xlfg knowledge base** plus the ephemeral execution-log directory.

> Tip: If you have the CLI installed, `xlfg init` generates the same scaffolding.

## Safety + idempotency rules

- Do **not** overwrite existing files.
- If a file already exists, only add missing sections.
- Do **not** modify unrelated docs or tooling.

## What to create

### Directories

- `docs/xlfg/knowledge/`
- `docs/xlfg/runs/`
- `.xlfg/runs/`

### Gitignore

Ensure `.xlfg/` is listed in the repo root `.gitignore`.

### Durable knowledge files

Create these if missing:

- `docs/xlfg/index.md`
- `docs/xlfg/knowledge/quality-bar.md`
- `docs/xlfg/knowledge/decision-log.md`
- `docs/xlfg/knowledge/patterns.md`
- `docs/xlfg/knowledge/testing.md`
- `docs/xlfg/knowledge/ux-flows.md`
- `docs/xlfg/knowledge/failure-memory.md`
- `docs/xlfg/knowledge/harness-rules.md`
- `docs/xlfg/knowledge/commands.json`

### Important default in this version

The knowledge base must support three pre-implementation contracts:

- `flow-spec.md` — what the user flow must do
- `test-contract.md` — what verification must prove
- `env-plan.md` — how the harness and dev server must behave

## Completion

After scaffolding is created:

- Print created paths
- Suggest running `/xlfg <your request>`
