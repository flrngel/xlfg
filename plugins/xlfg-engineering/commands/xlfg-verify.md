---
name: xlfg:verify
description: Run proof-first verification from the lean run card and keep the run honest.
argument-hint: "[run-id | latest] [fast|full]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, TodoWrite, Task
effort: high
---

# /xlfg:verify

Run verification commands and save evidence.

INPUT: `$ARGUMENTS`

## Select run and mode

- first token: `run-id` (or `latest`)
- optional second token: `fast` or `full`
- if no mode is supplied, use `spec.md` first, then `harness-profile.md` if present, otherwise choose the lightest honest mode

## Always read these first

- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`

Read only when needed:

- `verification.md`
- `research.md`
- `diagnosis.md`
- `env-plan.md`
- `proof-map.md`
- `run-summary.md`
- `docs/xlfg/knowledge/current-state.md`

## Verify plan

- `fast` = shortest honest proof for changed scenarios
- `full` = fast proof first, then smoke / e2e / broader regression only when justified
- static checks alone are not enough for behavioral work
- green commands are not enough if the required scenario was never actually exercised
- if `test-readiness.md` says `REVISE`, the run is RED until planning is fixed

## Environment handling

Reuse healthy local servers when possible. Do not start duplicates. Stop on the first actionable failure.

## Finish verification

Verification is GREEN only when changed behavior was proven, the readiness gate is satisfied, and `spec.md` still matches what was proven.

If GREEN, update `workboard.md`:

- `verify: DONE`
- `review: NEXT`
