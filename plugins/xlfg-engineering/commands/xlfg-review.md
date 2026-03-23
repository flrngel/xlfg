---
name: xlfg:review
description: Run a risk-shaped review after verification without turning review into ceremony.
argument-hint: "[run-id | latest]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, TodoWrite, Task
effort: medium
---

# /xlfg:review

Review the run after verification.

INPUT: `$ARGUMENTS`

## Always read these first

- `spec.md`
- `verification.md`
- `workboard.md`

Read only when a chosen lens needs them:

- `test-contract.md`
- `research.md`
- `diagnosis.md`
- `proof-map.md`
- `run-summary.md`
- `docs/xlfg/knowledge/current-state.md`

## Review doctrine

- Review is confirmation, not where quality is manufactured.
- Pick 0–2 lenses for standard work; only go deeper when the changed surface or risk justifies it.
- Use security / performance / UX / architecture reviewers only when those risks are actually present.

## Default review budget

- `quick`: 0–1 lens
- `standard`: 1–2 lenses
- `deep`: up to 4 lenses

## Finish review

If review passes, update `workboard.md`:

- `review: DONE`
- `compound: NEXT`
