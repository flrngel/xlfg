---
name: xlfg-file-context
description: Use docs/xlfg + .xlfg as the file-based context system for lean, autonomous SDLC runs.
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
      ...
  migrations/
    <from>-to-<to>.md
  runs/
    <run-id>/
      context.md
      memory-recall.md
      spec.md
      test-contract.md
      test-readiness.md
      workboard.md
      research.md                # optional
      diagnosis.md               # optional
      solution-decision.md       # optional
      flow-spec.md               # optional
      env-plan.md                # optional
      proof-map.md               # optional
      risk.md                    # optional
      verification.md
      verify-fix-plan.md
      review-summary.md          # optional
      run-summary.md             # optional
      compound-summary.md
      current-state-candidate.md # branch-local when needed
      tasks/
        <task-id>/
          task-brief.md

.xlfg/
  runs/
    <run-id>/
      doctor/
        <ts>/
      verify/
        <ts>/
```

## Workflow rules

- Seed only the lean core docs.
- Keep `spec.md` current instead of copying the same truth into multiple planning files.
- Create supporting docs only when they improve a decision, proof, or handoff.
- Let `workboard.md` carry stage truth and `verification.md` carry proof evidence.
- Compound only verified, reusable lessons.
