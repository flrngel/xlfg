---
name: xlfg-file-context
description: Use docs/xlfg + .xlfg as file-based context for independent subagents. Use for long SDLC workflows.
---

# xlfg-file-context

Use file-based context to keep long-horizon work reliable and legible.

## When to use

- Any `/xlfg` run
- Long tasks that exceed chat memory
- Multi-agent work where coordination needs to be deterministic

## Core idea

Treat files as the system of record:

- **Durable (commit):** `docs/xlfg/` — specs, plans, reviews, run summaries, lessons
- **Ephemeral (gitignore):** `.xlfg/` — raw logs, screenshots, traces

## Standard structure

```
docs/xlfg/
  index.md
  knowledge/
    quality-bar.md
    decision-log.md
    patterns.md
  runs/
    <run-id>/
      context.md
      context/
        adjacent.md
        constraints.md
        unknowns.md
      repo-map.md
      spec.md
      plan.md
      test-plan.md
      risk.md
      tasks/
        <task-id>/
          implementer-report.md
          checker-report.md
      verification.md
      reviews/
      run-summary.md

.xlfg/
  runs/
    <run-id>/
      verify/
      screenshots/
      traces/
```

## Expand → Map → Reduce pattern (how to avoid chaos)

### Expand context

- Spawn investigation subagents with isolated contexts.
- Each investigator reads canonical `context.md` and writes exactly one file under `context/`.
- Lead agent merges findings back into canonical `context.md`.
- Any scope expansion beyond the original request needs explicit user approval.

### Map

- Spawn subagents with **isolated contexts**.
- Give each one:
  - `DOCS_RUN_DIR/context.md`
  - a single output path
  - a single responsibility
- Subagents write their findings to files (no chat coordination).

### Reduce

- A lead agent reads all subagent outputs.
- The lead agent writes the canonical `plan.md` and updates progress checkboxes.

### Mandatory pair loop for every task

- Implementer writes code + tests and a task handoff file.
- Checker reads task contract + diffs and writes `checker-report.md`.
- Lead agent arbitrates and updates `plan.md`.
- Keep the loop bounded (max 3 checker rounds per task).

## File ownership rule

To avoid conflicts:

- Subagents **never** edit shared canonical files (like `plan.md`).
- Subagents write to their own output file only.
- The lead agent merges.
- Checker agents are read-only on production code by default.

## “Map, not manual”

Prefer a small index (like `docs/xlfg/index.md`) with links to deeper sources, rather than duplicating guidance in prompts.
