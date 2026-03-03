---
name: xlfg:implement
description: Execute the planned tasks with explicit implementation agents, targeted proof, and no shortcut patches.
argument-hint: "[run-id | latest]"
---

# /xlfg:implement

Implement the planned work for a run. This command owns **coding + task-level proof**, but not final ship verification.

<input>#$ARGUMENTS</input>

## 1) Select run

- If `latest` or empty: use the newest folder under `docs/xlfg/runs/`
- Otherwise: treat the argument as the run id

Set:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`

## 2) Read the mandatory contracts

Read these first and refuse to proceed if any are missing:

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `env-plan.md`
- `scorecard.md`
- `risk.md` if present

## 3) Implementation doctrine

- **Review is not the cleanup crew.** Build cleanly now.
- **Do not patch the symptom if the diagnosis says the real problem lives elsewhere.**
- **Do not weaken tests to get green.**
- **Do not broaden file scope casually.** If scope must expand, update the plan first.
- **Use targeted checks after each task.** Final verification comes later.
- **If a disproof probe trips, stop and return to planning.**

## 4) Task loop

For each unchecked task in `plan.md`, in order:

### 4A) Create the task folder and brief

Ensure `tasks/<task-id>/` exists and write `task-brief.md` with:

- task goal
- scenario IDs
- allowed file scope
- required checks
- relevant invariants
- disproof probe / stop condition
- any blocker context

### 4B) Run the specified implementation agents

Run these agents in order for the task:

1. `xlfg-test-implementer` → `tasks/<task-id>/test-report.md`
2. `xlfg-task-implementer` → `tasks/<task-id>/implementer-report.md`
3. run the targeted checks required by the task
4. `xlfg-task-checker` → `tasks/<task-id>/checker-report.md`

### 4C) Acceptance rule

A task is only complete when:

- the targeted checks pass
- the checker verdict is `ACCEPT`
- the task checkbox in `plan.md` is marked complete

### 4D) Anti-loop rule

If the checker rejects the task twice **without a new diagnosis or plan update**:

- stop the patch loop
- update `diagnosis.md` and `solution-decision.md` if needed
- update `plan.md`
- only then resume implementation

## 5) Root-cause rule

If a workaround is the only safe short-term move, document it explicitly in:

- `tasks/<task-id>/implementer-report.md`
- `run-summary.md`
- `risk.md` or `verify-fix-plan.md` if it changes the ship gate

Do not silently present a workaround as the final solution.

## 6) Finish the implementation phase

When all tasks are complete, write or update `run-summary.md` with:

- what changed
- manual smoke steps
- targeted checks already run
- areas that still depend on `/xlfg:verify`
- known risks or `none`

Do not call final verification or review in this command. The workflow continues with `/xlfg:verify`.
