---
name: xlfg-file-context
description: Use docs/xlfg + .xlfg as the file-based context system for long SDLC runs.
---

# xlfg-file-context

Use file-based context to keep long-horizon work reliable and legible.

## Core idea

Treat files as the system of record:

- **Tracked durable knowledge:** `docs/xlfg/knowledge/` + `docs/xlfg/meta.json`
- **Local episodic evidence:** `docs/xlfg/runs/`
- **Ephemeral raw logs:** `.xlfg/`

## Standard structure

```text
docs/xlfg/
  index.md
  meta.json
  knowledge/
    quality-bar.md
    decision-log.md
    patterns.md
    testing.md
    ux-flows.md
    failure-memory.md
    harness-rules.md
    commands.json
    agent-memory/
      root-cause-analyst.md
      test-strategist.md
      env-doctor.md
      task-implementer.md
      verify-reducer.md
      ux-reviewer.md
  migrations/
    <from>-to-<to>.md
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

### 1) Prepare fast

- Check canonical `docs/xlfg/meta.json` first; if a legacy `docs/xlfg/metadata.json` exists, treat it as legacy scaffold metadata only.
- Compare the installed xlfg/plugin version to the repo scaffold version. If they match, do not re-init.
- If the version drifted, migrate only the missing structure.

### 2) Diagnose + contract first

Before implementation, make sure the run has:

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`

### 3) Map

- Spawn subagents with isolated contexts.
- Give each a single responsibility and a single output path.
- Avoid chat coordination.
- Give a role its own memory file only if that role repeatedly needs the same lesson.

### 4) Reduce

- The lead merges results into canonical files.
- The plan must align tasks to scenario IDs and diagnosis.

### 5) Implement with bounded pair loops

- Test implementer writes targeted test changes and proof notes.
- Implementer writes code + implementer report.
- Checker reviews and writes checker report.
- Lead updates the plan.
- Do not exceed 2 checker loops per task without a fresh diagnosis.
