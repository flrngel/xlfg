---
name: xlfg:implement
description: Implement the planned solution with minimal read amplification, adaptive subagent use, and explicit proof discipline.
argument-hint: "[run-id | latest]"
---

# /xlfg:implement

Implement the run one task at a time.

<input>#$ARGUMENTS</input>

## 1) Select run

- If the argument is `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat the argument as the run id

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

## 2) Read the minimum honest brief first

Always read these first:

- `spec.md`
- `plan.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`
- `proof-map.md`

Read these only when the task needs deeper context:

- `query-contract.md`
- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`
- `risk.md`
- `docs/xlfg/knowledge/current-state.md`
- relevant role memory under `docs/xlfg/knowledge/agent-memory/`

If `test-readiness.md` is missing or not `READY`, stop and return to `/xlfg:plan`.

## 3) Implementation doctrine

- Start from the run card, not from a file-reading marathon.
- Re-open deeper docs only when the active task genuinely needs them.
- Every task must still satisfy the direct asks, non-negotiable implied asks, and proof obligations.
- Do not ask the user to implement code, run major local tests, or orchestrate the repo-local harness when the agent can do it.
- Do not widen scope casually. If scope expands materially, update the plan first.
- Do not weaken tests to get green.
- Do not ship a symptom patch when the diagnosis says the root problem lives elsewhere.
- If a disproof probe trips, stop and update the plan instead of grinding forward.

## 4) Workboard discipline

Before the first task:

- set `implement` to `IN_PROGRESS`
- record the current next action
- note the active profile and research mode
- keep the PM / Engineering / QA status notes honest

After each task:

- update the task row
- record checks actually run
- record any new blocker or scope change
- record a short engineering note and QA focus note when useful

## 5) Default task loop

For each unchecked task in `plan.md`:

### 5A) Create the task brief

Ensure `tasks/<task-id>/task-brief.md` exists with:

- why this task matters
- objective / query / scenario IDs
- goal and file scope
- proof obligations
- required checks
- invariants
- disproof probe
- anti-monkey-fix warning

### 5B) Adaptive agent budget

Default path:

1. `xlfg-task-implementer` → `tasks/<task-id>/implementer-report.md`
2. run targeted checks for the task

Use `xlfg-test-implementer` only when:

- the task changes or adds proof
- planned checks do not yet have honest test coverage
- the task touches regression-prone behavior that the plan already flagged

Use `xlfg-task-checker` only when **one of these triggers fires**:

- profile is `deep`
- checks failed once and the fix is non-obvious
- the diff is broader than planned
- the task crosses a public interface / auth / money / destructive-data boundary
- the task changes multiple user-facing paths

If no trigger fires, do a disciplined self-check against `task-brief.md` and record that in `implementer-report.md`.

## 6) Acceptance rule

A task is complete only when:

- targeted checks pass
- required proof work for the task exists
- `plan.md` and `workboard.md` are updated
- `proof-map.md` points to planned or observed evidence
- the task still aligns with `spec.md`
- no known recall-derived trap was ignored silently

## 7) Anti-loop rule

Respect the checker-loop budget from `harness-profile.md`.

If repeated failures happen without a new diagnosis or plan update:

- stop the patch loop
- update the relevant run artifacts
- only then resume implementation

Do not brute-force your way to green.

## 8) Escalation rule

Step the run up when:

- scope expands across more flows than planned
- proof needs clearly exceed the current budget
- repeated failures expose a shallow diagnosis
- environment assumptions become unreliable
- preserving implied asks needs more proof than expected

If you escalate, update:

- `harness-profile.md`
- `spec.md`
- `plan.md`
- `workboard.md`
- `test-contract.md` / `test-readiness.md` / `proof-map.md` if proof changed

## 9) Finish implementation

When all tasks are complete, write or update `run-summary.md` with:

- query / intent summary
- why summary
- research summary
- what changed
- checks already run
- remaining verification obligations
- direct asks covered
- implied asks pending or deferred
- PM / Engineering / QA status
- known risks or `none`

Update `workboard.md`:

- `implement: DONE`
- `verify: NEXT`

Do not run final verification or review in this command.
