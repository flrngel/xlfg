---
name: xlfg:plan
description: Create or refresh the lean run brief without writing production code.
argument-hint: "[feature description, bugfix, research task, or product request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, TodoWrite, Task
effort: high
---

# /xlfg:plan

Create a real plan the agent can execute. Do **not** write production code in this command.

INPUT: `$ARGUMENTS`

If the request is empty, ask the user what they want built, fixed, or researched and stop.

## Core rules

- Recall before broad fan-out.
- Research is part of SDLC, but only when the repo cannot answer the question or the user explicitly asked for research.
- `spec.md` is the run card and the single source of truth.
- Do not create duplicate planning files by default.
- The agent owns the work unless the blocker is truly human-only.

## Phase 0 — Bootstrap and run creation

If scaffold/meta is missing or stale, do the smallest silent sync needed and continue.

Create `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>` and write only these core files:

- `context.md`
- `memory-recall.md`
- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`

Create these optional files only when they change a decision:

- `research.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`
- `proof-map.md`
- `risk.md`

## Phase 1 — Minimal recall and repo scan

Read first:

- `context.md`
- `memory-recall.md` if present
- `docs/xlfg/knowledge/current-state.md` if present

Then do the smallest repo scan that answers:

- where the changed behavior likely lives
- which interfaces / flows matter
- how the repo is verified locally
- which constraints should survive the run

## Phase 2 — Write the run card

`spec.md` must include:

- direct asks, implied asks, non-goals
- why / user outcome / false-success warning
- repo findings and external findings (`repo-only` when none)
- harness profile and verify mode
- chosen solution and rejected shortcuts
- task map
- proof summary
- PM / UX / Engineering / QA / Release notes

## Phase 3 — Proof before code

Write `test-contract.md` with 1–5 practical scenario cards.

Write `test-readiness.md` with a hard verdict:

- `READY` — the plan names practical proof
- `REVISE` — the proof is vague, too expensive, or missing

Initialize `workboard.md`.

## Planning gate

Implementation may start only when all are true:

- `memory-recall.md` is honest
- `spec.md` is coherent and specific
- `test-contract.md` names practical proof
- `test-readiness.md` says `READY`
- `workboard.md` is initialized

Finish by returning only:

- `RUN_ID`
- work kind
- harness profile
- research mode
- `test-readiness` verdict
