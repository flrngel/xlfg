---
name: xlfg:prepare
description: Fast scaffold/version check. Bootstrap only if missing; migrate only on version drift; rebuild local knowledge views.
---

# /xlfg:prepare

Make xlfg ready in this repo **without paying a full init cost every run**.

## Rules

- Compare the installed xlfg/plugin version against the repo scaffold version in `docs/xlfg/meta.json` (or legacy `docs/xlfg/metadata.json`).
- If `docs/xlfg/` is missing, bootstrap the minimal scaffold.
- If the version differs, apply the missing structure changes and write a migration note under `docs/xlfg/migrations/`.
- Do not overwrite user-authored files.
- Keep `docs/xlfg/runs/` as local-only evidence by default.
- Record the current git/worktree context in `.xlfg/worktree.json`.
- Rebuild local generated views under `docs/xlfg/knowledge/_views/`.

## Required structure after prepare

### Tracked

- `docs/xlfg/meta.json`
- `docs/xlfg/index.md`
- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/cards/`
- `docs/xlfg/knowledge/events/`
- `docs/xlfg/knowledge/agent-memory/`
- `docs/xlfg/migrations/`

### Local generated

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/*.md`
- `docs/xlfg/knowledge/_views/agent-memory/*.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`
- `docs/xlfg/knowledge/_views/worktree.md`
- `.xlfg/worktree.json`

### Local-only evidence

- `docs/xlfg/runs/`
- `.xlfg/runs/`

## Gitignore rules

Ensure the repo root `.gitignore` contains:

- `.xlfg/`
- `docs/xlfg/runs/*`
- `!docs/xlfg/runs/.gitkeep`
- `!docs/xlfg/runs/README.md`
- `docs/xlfg/knowledge/_views/`

## Completion

Print:
- whether bootstrap was needed
- whether migration was needed
- previous repo scaffold version (if any)
- installed xlfg/plugin version
- version source used for the repo scaffold check
- git/worktree context summary
- changed paths
- whether local views were rebuilt
