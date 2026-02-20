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
      repo-map.md
      spec.md
      plan.md
      test-plan.md
      risk.md
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

## Map → Reduce pattern (how to avoid chaos)

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

## File ownership rule

To avoid conflicts:

- Subagents **never** edit shared canonical files (like `plan.md`).
- Subagents write to their own output file only.
- The lead agent merges.

## “Map, not manual”

Prefer a small index (like `docs/xlfg/index.md`) with links to deeper sources, rather than duplicating guidance in prompts.
