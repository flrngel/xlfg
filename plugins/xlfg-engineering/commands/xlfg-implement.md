---
name: xlfg:implement
description: Implement from the run card with minimal read amplification and no user-managed phase choreography.
argument-hint: "[run-id | latest]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, TodoWrite, Task
effort: high
---

# /xlfg:implement

Implement the run one task at a time.

INPUT: `$ARGUMENTS`

## Select run

- empty or `latest` → newest run under `docs/xlfg/runs/`
- otherwise treat the argument as the run id

## Always read these first

- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`

Read supporting docs only when the active task truly needs them:

- `research.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`
- `risk.md`
- `memory-recall.md`
- `docs/xlfg/knowledge/current-state.md`

If `test-readiness.md` is missing or not `READY`, return to planning and fix it yourself before coding.

## Doctrine

- Start from `spec.md`, not from a file-reading marathon.
- Default to one implementation owner.
- Use test or checker subagents only when the task changes proof, crosses a risky boundary, or failed once in a non-obvious way.
- Run the smallest targeted check after each meaningful change.
- Update `workboard.md` and `spec.md` when the truth changes.
- Do not ask the user to run repo-local checks or continue the workflow for you.

## Default path

1. `xlfg-task-implementer` for the active task when a focused implementation agent is genuinely helpful
2. run targeted task checks

## Finish implementation

When tasks are complete, update or write `run-summary.md` with what changed, checks already run, remaining verification obligations, and real risks.

Update `workboard.md`:

- `implement: DONE`
- `verify: NEXT`
