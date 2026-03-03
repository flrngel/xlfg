---
name: xlfg-file-context
description: Use docs/xlfg + .xlfg as the file-based context system for long SDLC runs.
---

# xlfg-file-context

Use file-based context to keep long-horizon work reliable and legible.

## Core idea

Treat files as the system of record:

- **Durable (commit):** `docs/xlfg/` — diagnosis, contracts, plans, reviews, scorecards, lessons
- **Ephemeral (gitignore):** `.xlfg/` — raw logs, screenshots, traces, doctor reports

## Standard structure

```text
docs/xlfg/
  index.md
  knowledge/
    quality-bar.md
    decision-log.md
    patterns.md
    testing.md
    ux-flows.md
    failure-memory.md
    harness-rules.md
    commands.json
  runs/
    <run-id>/
      context.md
      diagnosis.md
      solution-decision.md
      flow-spec.md
      spec.md
      plan.md
      test-contract.md
      env-plan.md
      scorecard.md
      risk.md
      tasks/
        <task-id>/
          task-brief.md
          test-report.md
          implementer-report.md
          checker-report.md
      verification.md
      verify-fix-plan.md
      reviews/
      run-summary.md
      compound-summary.md

.xlfg/
  runs/
    <run-id>/
      doctor/
        <ts>/
      verify/
        <ts>/
```

## Core workflow

### 1) Diagnose + contract first

Before implementation, make sure the run has:

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`

### 2) Map

- Spawn subagents with isolated contexts.
- Give each a single responsibility and a single output path.
- Avoid chat coordination.

### 3) Reduce

- The lead merges results into canonical files.
- The plan must align tasks to scenario IDs and diagnosis.

### 4) Implement with bounded pair loops

- Test implementer writes targeted test changes and proof notes.
- Implementer writes code + implementer report.
- Checker reviews and writes checker report.
- Lead updates the plan.
- Do not exceed 2 checker loops per task without a fresh diagnosis.
