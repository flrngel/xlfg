---
name: xlfg:implement
description: Execute the planned work with why-first discipline, profile-bounded task loops, and proof-aware implementation.
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

## 2) Read the mandatory contracts and memory

Read these first and refuse to proceed if any are missing:

- `memory-recall.md`
- `why.md`
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
- `docs/xlfg/knowledge/_views/current-state.md` if present
- relevant generated role memory under `docs/xlfg/knowledge/_views/agent-memory/`
- exact source cards/events only when a generated view needs precision

Extract from `harness-profile.md` before starting:

- selected profile (`quick` | `standard` | `deep`)
- max ordered tasks
- max checker loops per task
- max parallel subagents
- escalation triggers

If the profile is missing or vague, stop and repair it before coding.

## 3) Implementation doctrine

- **Why before code.** Every task must still serve `why.md`, not just a visible symptom.
- **Review is not the cleanup crew.** Build cleanly now.
- **Do not patch the symptom if the diagnosis says the real problem lives elsewhere.**
- **Do not weaken tests to get green.**
- **Do not broaden file scope casually.** If scope must expand, update the plan first.
- **Use targeted checks after each task.** Final verification comes later.
- **If a disproof probe trips, stop and return to planning.**
- **Do not repeat a known failure pattern** already called out in `memory-recall.md`, `current-state.md`, generated role memory, or source cards.
- **Do not mark a task done if its proof obligation is still undefined.** Update `proof-map.md` or return to planning.

## 4) Workboard discipline

`workboard.md` is the run-truth ledger during implementation.

Before the first task:
- set `implement` to `IN_PROGRESS`
- mark the current next action
- note the active profile and any active escalations

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
- task goal
- scenario IDs
- allowed file scope
- proof obligations from `proof-map.md`
- required checks
- relevant invariants
- disproof probe / stop condition
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
- no known recall-derived trap was ignored silently
- the task still aligns to `why.md`
