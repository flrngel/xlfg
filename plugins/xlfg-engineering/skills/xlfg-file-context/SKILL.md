---
name: xlfg-file-context
description: Use docs/xlfg + .xlfg as the file-based context system for long SDLC runs.
---

# xlfg-file-context

Use file-based context to keep long-horizon work reliable and legible.

## Core idea

Treat files as the system of record:

- **Tracked durable knowledge:** `docs/xlfg/knowledge/` + `docs/xlfg/meta.json`
- **Tracked next-agent handoff:** `docs/xlfg/knowledge/current-state.md`
- **Local episodic evidence:** `docs/xlfg/runs/`
- **Ephemeral raw logs:** `.xlfg/`

## Standard structure

```text
docs/xlfg/
  index.md
  meta.json
  knowledge/
    current-state.md
    quality-bar.md
    decision-log.md
    patterns.md
    testing.md
    ux-flows.md
    failure-memory.md
    harness-rules.md
    ledger.jsonl
    commands.json
    agent-memory/
      root-cause-analyst.md
      solution-architect.md
      test-strategist.md
      env-doctor.md
      test-implementer.md
      task-implementer.md
      task-checker.md
      verify-reducer.md
      ux-reviewer.md
      architecture-reviewer.md
      security-reviewer.md
      performance-reviewer.md
  migrations/
    <from>-to-<to>.md
  runs/
    <run-id>/
      context.md
      memory-recall.md
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

### 1) Prepare fast

- Check canonical `docs/xlfg/meta.json` first; if a legacy `docs/xlfg/metadata.json` exists, treat it as legacy scaffold metadata only.
- Compare the installed xlfg/plugin version to the repo scaffold version. If they match, do not re-init.
- If the version drifted, migrate only the missing structure.

### 2) Recall before broad scanning

Before repo fan-out:

- read `docs/xlfg/knowledge/current-state.md`
- load the smallest relevant slice of durable memory
- write `memory-recall.md`
- record both strong matches and explicit no-hit cases

### 3) Diagnose + contract first

Before implementation, make sure the run has:

- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`

### 4) Map

- Spawn subagents with isolated contexts.
- Give each a single responsibility and a single output path.
- Avoid chat coordination.
- Give a role its own memory file only if that role repeatedly needs the same lesson.

### 5) Reduce

- The lead merges results into canonical files.
- The plan must align tasks to scenario IDs and diagnosis.
- The plan should carry forward recall-derived rules when they matter.

### 6) Implement with bounded pair loops

- Test implementer writes targeted test changes and proof notes.
- Implementer writes code + implementer report.
- Checker reviews and writes checker report.
- Lead updates the plan.
- Do not exceed 2 checker loops per task without a fresh diagnosis.

### 7) Compound + refresh handoff

- Promote verified reusable lessons into shared knowledge or role memory.
- Append durable memory events to the ledger.
- Refresh `current-state.md` so the next agent can start fast.
