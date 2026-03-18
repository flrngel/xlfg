---
name: xlfg:implement
description: Implement the planned root solution task-by-task while preserving the request contract, why, and proof map.
argument-hint: "[run-id | latest]"
---

# /xlfg:implement

Implement the run one task at a time. Do **not** skip the planning contract.

<input>#$ARGUMENTS</input>

## 1) Select run

- If the argument is `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat the argument as the run id

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

## 2) Read the run contract before touching code

Read these files first, in this order if present:

- `query-contract.md`
- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `env-plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`
- `risk.md` if present
- `docs/xlfg/knowledge/current-state.md` if present
- relevant role memory under `docs/xlfg/knowledge/agent-memory/`

Extract from `query-contract.md` before starting:
- direct asks
- non-negotiable implied asks
- developer / product intention
- prohibited shallow fixes
- the carry-forward anchor

Extract from `harness-profile.md` before starting:
- selected profile (`quick` | `standard` | `deep`)
- max ordered tasks
- max checker loops per task
- max parallel subagents
- escalation triggers

If either contract is missing or vague, stop and repair it before coding.

## 3) Implementation doctrine

- **Query before code.** Every task must still satisfy the direct asks and non-negotiable implied asks.
- **Why before code.** Every task must still serve `why.md`, not just a visible symptom.
- **Review is not the cleanup crew.** Build cleanly now.
- **Do not patch the symptom if the diagnosis says the real problem lives elsewhere.**
- **Do not weaken tests to get green.**
- **Do not broaden file scope casually.** If scope must expand, update the plan first.
- **Use targeted checks after each task.** Final verification comes later.
- **If a disproof probe trips, stop and return to planning.**
- **If a task only fixes one obvious entrypoint while alternate paths remain broken, that is a monkey fix. Reject it.**
- **Do not repeat a known failure pattern** already called out in `memory-recall.md`, `current-state.md`, or role memory.
- **Do not mark a task done if its proof obligation is still undefined.** Update `proof-map.md` or return to planning.

## 4) Workboard discipline

`workboard.md` is the run-truth ledger during implementation.

Before the first task:
- set `implement` to `IN_PROGRESS`
- mark the current next action
- note the active profile and any active escalations
- re-copy the carry-forward anchor into the current notes if needed

After each task:
- update the task row status
- record the checks actually run
- record any new blocker, scope expansion, or escalation
- keep `current next action` honest

## 5) Task loop

For each unchecked task in `plan.md`, in order:

### 5A) Create the task folder and brief

Ensure `tasks/<task-id>/` exists and write `task-brief.md` with:

- why this task matters to the run
- direct asks / implied asks / acceptance criteria covered (`Q*`, `I*`, `A*`)
- task goal
- scenario IDs
- allowed file scope
- proof obligations from `proof-map.md`
- required checks
- relevant invariants
- disproof probe / stop condition
- anti-monkey-fix warning for this task
- any blocker context
- reused recall rules that matter for this task

### 5B) Run the specified implementation agents

Run these agents in order for the task:

1. `xlfg-test-implementer` → `tasks/<task-id>/test-report.md`
2. `xlfg-task-implementer` → `tasks/<task-id>/implementer-report.md`
3. run the targeted checks required by the task
4. `xlfg-task-checker` → `tasks/<task-id>/checker-report.md`

Keep task work scoped. Do not spawn optional subagents beyond the profile budget unless an escalation trigger fired.

### 5C) Acceptance rule

A task is only complete when:

- the targeted checks pass
- the checker verdict is `ACCEPT`
- the task checkbox in `plan.md` is marked complete
- the task row in `workboard.md` is updated
- the relevant `proof-map.md` rows now have concrete planned or observed evidence paths
- the relevant direct asks and non-negotiable implied asks are still covered or explicitly deferred
- no known recall-derived trap was ignored silently
- the task still aligns to `query-contract.md` and `why.md`

### 5D) Anti-loop rule

Use the checker-loop budget from `harness-profile.md`.

If the checker rejects the task up to that limit **without a new diagnosis or plan update**:

- stop the patch loop
- update `query-contract.md` if the request understanding changed
- update `diagnosis.md` and `solution-decision.md` if needed
- update `plan.md`, `workboard.md`, and `proof-map.md`
- only then resume implementation

Do not brute-force your way to green.

## 6) Escalation rule

Step the run up to a deeper harness profile if any of these become true:

- the scope expands across more user-facing flows than planned
- the task crosses an auth / money / destructive-data boundary
- the required proof clearly exceeds the current profile budget
- repeated checker failures reveal the diagnosis was too shallow
- the environment plan is no longer credible for the changed surface
- preserving the implied asks clearly requires more proof than originally budgeted

If you escalate:
- update `harness-profile.md`
- update `workboard.md`
- update `plan.md`
- call out what changed and why

## 7) Root-cause rule

If a workaround is the only safe short-term move, document it explicitly in:

- `tasks/<task-id>/implementer-report.md`
- `run-summary.md`
- `risk.md` or `verify-fix-plan.md` if it changes the ship gate

Do **not** silently present a workaround as the final solution.

## 8) Finish the implementation phase

When all tasks are complete, write or update `run-summary.md` with:

- query / intent summary
- why summary
- what changed
- manual smoke steps
- targeted checks already run
- areas that still depend on `/xlfg:verify`
- proof obligations still open in `proof-map.md`
- direct asks covered
- implied asks still pending or explicitly deferred
- known risks or `none`
- which recall-derived rules mattered most during implementation

Update `workboard.md`:
- `implement: DONE`
- `verify: NEXT`

Do not call final verification or review in this command. The workflow continues with `/xlfg:verify`.
