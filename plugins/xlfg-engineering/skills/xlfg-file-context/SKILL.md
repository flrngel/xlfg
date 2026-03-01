---
name: xlfg-file-context
description: Use docs/xlfg + .xlfg as the file-based context system for long SDLC runs.
---

# xlfg-file-context

Use file-based context to keep long-horizon work reliable and legible.

## When to use

- Any `/xlfg` run
- Long tasks that exceed chat memory
- Multi-agent work where coordination must be deterministic

## Core idea

Treat files as the system of record:

- **Durable (commit):** `docs/xlfg/` — contracts, plans, reviews, scorecards, lessons
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
      flow-spec.md
      spec.md
      plan.md
      test-contract.md
      env-plan.md
      scorecard.md
      risk.md
      tasks/
        <task-id>/
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

### 1) Contract first

Before implementation, make sure the run has:

- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`

### 2) Map

- Spawn subagents with isolated contexts.
- Give each a single responsibility and a single output path.
- Avoid chat coordination.

### 3) Reduce

- The lead merges results into canonical files.
- The plan must align tasks to scenario IDs.

### 4) Implement with bounded pair loops

- Implementer writes code + tests + implementer report.
- Checker reviews and writes checker report.
- Lead updates the plan.
- Do not exceed 3 checker loops per task without a fresh diagnosis.

## File ownership rule

To avoid conflicts:

- Subagents do **not** edit shared canonical files unless explicitly assigned as reducers.
- Subagents write to their owned output file.
- The lead merges.

## What belongs in durable memory vs ephemeral logs

### Durable
- flow contracts
- test contracts
- scorecards
- patterns and decisions
- failure memory and harness rules

### Ephemeral
- raw command output
- dev-server logs
- screenshots / traces
- temporary local diagnostics
