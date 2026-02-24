---
name: xlfg:init
description: Initialize xlfg scaffolding (docs/xlfg + .xlfg) in this repo.
---

# /xlfg:init

Create a small, durable **xlfg knowledge base** plus an ephemeral run-log directory.

> Tip: If you have the `xlfg` CLI installed in this repo, you can also run `xlfg init` to generate the same scaffolding. This command exists so you can stay fully inside Claude Code.


## Safety + idempotency rules

- Do **not** overwrite existing files.
- If a file already exists, only add missing sections.
- Do **not** modify unrelated docs or tooling.

## What to create

### 1) Directories

- `docs/xlfg/knowledge/`
- `docs/xlfg/runs/`
- `.xlfg/runs/`

### 2) Gitignore

Ensure the repo ignores ephemeral logs:

- Add `.xlfg/` to the repo root `.gitignore` (append if missing).

### 3) `docs/xlfg/index.md`

If missing, create:

```markdown
# xlfg

This folder is the **file-based context** system-of-record for `/xlfg` runs.

## Structure

- `knowledge/` — durable patterns, decisions, and checklists (commit this)
- `knowledge/testing.md` — durable testing learnings (commit this)
- `runs/` — one folder per run containing context investigations, specs, plans, task handoffs, reviews, and run summaries (commit this)

Ephemeral logs (do not commit):

- `.xlfg/runs/` — raw command outputs, traces, screenshots

## How to use

- Run `/xlfg` to start a new run.
- Each run writes artifacts to `docs/xlfg/runs/<run-id>/`.
- Verification logs land in `.xlfg/runs/<run-id>/`.

```

### 4) Durable knowledge files

Create these if missing:

#### `docs/xlfg/knowledge/quality-bar.md`

```markdown
# xlfg quality bar

Nothing is "done" unless:

- **Behavior is specified** (acceptance criteria)
- **Tests exist** for new behavior
- **Regression suite passes** (no breakages)
- **Lint / typecheck / build** pass (when applicable)
- **UX is validated** (screenshots, a11y, happy-path + failure-path)
- **Operational plan exists** (monitoring + rollback notes)

Evidence should be recorded in each run's `verification.md`.
```

#### `docs/xlfg/knowledge/decision-log.md`

```markdown
# xlfg decision log

Record durable architectural/product decisions made during `/xlfg` runs.

## Template

- **Date**:
- **Decision**:
- **Context**:
- **Alternatives considered**:
- **Consequences**:
- **Links**: (run folder, PR, issues)
```

#### `docs/xlfg/knowledge/patterns.md`

```markdown
# xlfg patterns

Reusable patterns discovered while shipping.

## Template

## Pattern: <name>

- **When to use**:
- **Why it works**:
- **Implementation notes**:
- **Pitfalls**:
- **Examples / links**:
```

#### `docs/xlfg/knowledge/testing.md`

```markdown
# xlfg testing knowledge

Durable testing learnings captured from `/xlfg` runs.

## Template

## Scenario: <name>

- **Failure that escaped**:
- **Why it escaped**:
- **Test pattern that catches it**:
- **Fast loop command**:
- **Full verification command**:
- **Flake signals / stabilization notes**:
- **Links**: (run folder, PR, issue)
```

## Completion

After scaffolding is created:

- Print the paths created
- Suggest running `/xlfg <your request>`
