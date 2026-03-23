---
name: xlfg:compound
description: Convert a completed run into durable knowledge and a short next-agent handoff.
argument-hint: "[run-id | latest]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, TodoWrite, Task
effort: medium
---

# /xlfg:compound

Turn a completed run into durable knowledge that improves future runs.

INPUT: `$ARGUMENTS`

Read if present:

- `spec.md`
- `memory-recall.md`
- `research.md`
- `diagnosis.md`
- `solution-decision.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`
- `proof-map.md`
- `verification.md`
- `review-summary.md`
- `run-summary.md`
- `docs/xlfg/knowledge/current-state.md`

Extract only reusable, verified lessons. Prefer shared knowledge over role memory unless the lesson is clearly role-specific.

Refresh `current-state.md` only when the repo-wide handoff really changed; otherwise write `current-state-candidate.md` in the run folder.

Write `compound-summary.md`, update the workboard to `compound: DONE`, and print where knowledge was written.
