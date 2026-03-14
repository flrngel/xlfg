---
name: xlfg-file-context
description: Use docs/xlfg + .xlfg as the file-based context system for why-first, proof-aware SDLC runs.
---

# xlfg-file-context

Use file-based context to keep long-horizon work reliable and legible.

## Core idea

Treat files as the system of record, but split **write model** from **read model**:

- **Tracked durable write model:** `docs/xlfg/knowledge/cards/`, `docs/xlfg/knowledge/events/`, `docs/xlfg/knowledge/agent-memory/<role>/cards/`, seed docs, and `docs/xlfg/meta.json`
- **Local generated read model:** `docs/xlfg/knowledge/_views/`
- **Local episodic evidence:** `docs/xlfg/runs/`
- **Ephemeral raw logs:** `.xlfg/`

## Standard structure

```text
docs/xlfg/
  index.md
  meta.json
  migrations/
    <from>-to-<to>.md
  knowledge/
    service-context.md
    write-model.md
    quality-bar-seed.md
    queries.md
    commands.json
    cards/
      current-state/
        <branch-slug>/
      quality-bar/
        <branch-slug>/
      decision-log/
        <branch-slug>/
      patterns/
        <branch-slug>/
      testing/
        <branch-slug>/
      ux-flows/
        <branch-slug>/
      failure-memory/
        <branch-slug>/
      harness-rules/
        <branch-slug>/
    events/
      <branch-slug>/
        <timestamp>--<run-id>--<slug>.json
    agent-memory/
      <role>/
        README.md
        cards/
          <branch-slug>/
            <timestamp>--<run-id>--<slug>.md
    _views/
      current-state.md
      quality-bar.md
      decision-log.md
      patterns.md
      testing.md
      ux-flows.md
      failure-memory.md
      harness-rules.md
      ledger.jsonl
      worktree.md
      agent-memory/
        <role>.md
  runs/
    <run-id>/
      context.md
      why.md
      memory-recall.md
      diagnosis.md
      solution-decision.md
      harness-profile.md
      flow-spec.md
      spec.md
      plan.md
      test-contract.md
      env-plan.md
      workboard.md
      proof-map.md
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
  worktree.json
  runs/
    <run-id>/
      doctor/
        <ts>/
      verify/
        <ts>/
```

## Core workflow

### 1) Prepare fast

- check canonical `docs/xlfg/meta.json` first; if a legacy `docs/xlfg/metadata.json` exists, treat it as legacy scaffold metadata only
- compare the installed xlfg/plugin version to the repo scaffold version
- if the version drifted, migrate only the missing structure
- record git/worktree context in `.xlfg/worktree.json`
- rebuild local `_views/`

### 2) Recall before broad scanning

Before repo fan-out:

- read `docs/xlfg/knowledge/_views/current-state.md`
- load the smallest relevant slice of durable memory
- use cards/events as the tracked source of truth when needed
- write `memory-recall.md`
- record both strong matches and explicit no-hit cases

### 3) Why + diagnosis + contract first

Before implementation, make sure the run has:

- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `workboard.md`
- `proof-map.md`

### 4) Map

- spawn subagents with isolated contexts
- give each a single responsibility and a single output path
- avoid chat coordination
- load optional agents progressively, only when the diagnosis shows a real need
- give a role its own durable cards only if that role repeatedly needs the same lesson

### 5) Reduce

- the lead merges results into canonical run files
- the plan must align tasks to scenario IDs, why, diagnosis, and proof obligations
- the plan should carry forward recall-derived rules when they matter

### 6) Implement with bounded pair loops

- test implementer writes targeted test changes and proof notes
- implementer writes code + implementer report
- checker reviews and writes checker report
- lead updates the plan, workboard, and proof map
- do not exceed the checker-loop budget from `harness-profile.md` without a fresh diagnosis

### 7) Verify honestly

- verification mode should match `harness-profile.md`
- a green command is not enough if `proof-map.md` still has a required gap
- update `verification.md`, `scorecard.md`, `proof-map.md`, and `workboard.md` together

### 8) Compound + rebuild views

- promote verified reusable lessons into tracked cards/events or role-memory cards
- rebuild local `_views/`
- never hand-edit `_views/` as the tracked source of truth
