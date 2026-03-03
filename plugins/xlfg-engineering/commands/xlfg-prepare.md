---
name: xlfg:prepare
description: Fast scaffold/version check. Bootstrap only if missing; migrate only on version drift.
---

# /xlfg:prepare

Make xlfg ready in this repo **without paying a full init cost every run**.

## Rules

- If `docs/xlfg/meta.json` exists and its version matches the plugin version, this command should be fast and effectively no-op.
- If `docs/xlfg/` is missing, bootstrap the minimal scaffold.
- If the version differs, apply the missing structure changes and write a migration note under `docs/xlfg/migrations/`.
- Do not overwrite user-authored files.
- Keep `docs/xlfg/runs/` as **local-only evidence** by default.

## Required structure after prepare

Tracked:
- `docs/xlfg/meta.json`
- `docs/xlfg/index.md`
- `docs/xlfg/knowledge/`
- `docs/xlfg/knowledge/agent-memory/`
- `docs/xlfg/migrations/`

Local-only:
- `docs/xlfg/runs/`
- `.xlfg/runs/`

## Gitignore rules

Ensure the repo root `.gitignore` contains:

- `.xlfg/`
- `docs/xlfg/runs/*`
- `!docs/xlfg/runs/.gitkeep`
- `!docs/xlfg/runs/README.md`

## Completion

Print:
- whether bootstrap was needed
- whether migration was needed
- previous version (if any)
- current version
- changed paths
