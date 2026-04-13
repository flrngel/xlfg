---
description: Internal xlfg phase skill. Use only during /xlfg runs to turn intent plus context into a lean run card, atomic task packets, a practical proof contract, and a READY gate.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, Agent, SendMessage
---

# xlfg-plan-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Turn the resolved intent and gathered truth into a lean run card, a practical test contract, and a real readiness gate.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read:
   - `context.md`
   - `memory-recall.md`
   - `spec.md`
   - `test-contract.md`
   - `test-readiness.md`
   - `workboard.md`
   - `docs/xlfg/knowledge/current-state.md`
3. Treat the intent contract in `spec.md` as canonical. Do not recreate a second intent file.
4. Use specialists as lane owners for plan quality:
   - always run `xlfg-root-cause-analyst` for bugfixes or symptom-heavy work
   - always run `xlfg-solution-architect`
   - always run `xlfg-test-strategist`
   - always run `xlfg-task-divider` after solution choice so every active task becomes one atomic packet
   - always run `xlfg-test-readiness-checker` before implementation
   - run `xlfg-why-analyst` when user value, UX, or operator impact matters
   - run `xlfg-spec-author` when scenario-level flow detail is needed
   - run `xlfg-risk-assessor` for higher-risk changes
   - run `xlfg-env-doctor` when the proof depends on a running app
   - run `xlfg-researcher` only if context phase proved that repo truth is insufficient
   - run `xlfg-brainstorm` only when the intent phase left multiple viable solution directions
   - run `xlfg-ui-designer` when the task is UI-related — the trigger fires if `spec.md` intent mentions UI / frontend / visual / interaction / layout / component / screen / a11y, or the planned task scope includes `*.tsx|*.jsx|*.vue|*.svelte|*.html|*.css|*.scss|*.sass|*.less|*.styl` or files under common frontend dirs (`src/components/`, `app/`, `pages/`, `ui/`, `frontend/`, `web/`). Dispatch with `PRIMARY_ARTIFACT: DOCS_RUN_DIR/ui-design.md` so the implementer has a directly checkable design contract before coding. Skip for pure-backend runs.
5. Keep the default specialist budget lean. Run the required plan specialists one lane at a time, then add at most one optional specialist when the current artifacts leave a concrete unresolved gap. Do not ask planning specialists to spawn more specialists.
6. Keep specialists foregrounded and require their artifacts before synthesis. Default to sequential plan specialists unless two packets are truly independent. If a specialist returns only setup notes or a missing artifact, use `SendMessage` with the returned agent ID to resume the same specialist once. If no agent ID is available, re-dispatch the same packet once.
7. The main conductor should synthesize `spec.md` and the final plan from specialist artifacts instead of replacing those lanes with its own first-pass reasoning.
8. Update `spec.md` as the single source of truth:
   - keep the intent contract and objective groups accurate
   - fill outcome / why and false-success trap
   - record repo and external findings
   - set execution shape and verify mode
   - record the chosen solution and rejected shortcuts
   - map tasks to objective IDs and scenario IDs
   - ensure each active task records `scope`, `primary_artifact`, and `done_check` in the `Task map`
   - keep proof summary and PM / UX / Engineering / QA / Release notes current
9. Update `test-contract.md` with 1–5 practical scenario contracts total, ensuring each active objective has explicit proof.
10. Update `test-readiness.md` with a real `READY` or `REVISE` verdict.
11. Update `workboard.md` so objectives, tasks, blockers, and the next action stay visible. Create or refresh `tasks/<task-id>/task-brief.md` for each active task.
12. Create optional docs only when they change a decision or proof obligation: `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, `risk.md`.
13. If a required planning specialist returns only setup notes or no artifact, retry once via resume or exact re-dispatch before repairing the gap yourself. Do not collapse a broad packet into main-thread guesswork; re-split it first when needed.

## Readiness rule

If `test-readiness.md` is `REVISE`, repair the plan yourself until it becomes `READY` or a true human-only blocker is explicit. Do not ask the user to sequence replanning.

## Delegation packet rules

- Preseed the target artifact before dispatch. The parent conductor should create the file named in `PRIMARY_ARTIFACT` with `Status: IN_PROGRESS`, the scoped mission, and a short checklist so the specialist is resuming a concrete work item instead of starting from an empty chat turn.
- Every specialist packet must begin with machine-readable headers:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only
```

- Pass objective context, not just a naked query. Include the exact ask, nearby constraints, and why the artifact matters to the next phase.
- Only the phase conductor may delegate. Never ask a planning specialist to spawn nested subagents or split work by launching its own workers.
- Default to **sequential** dispatch for artifact-producing planning/context work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Guardrails

- Do not recreate the old split-file bureaucracy.
- If a fact already lives clearly in `spec.md`, do not mirror it elsewhere.
- Do not start implementation until the readiness gate is honest.
- For multi-objective runs, keep partial completion legible per objective instead of pretending the whole bundle is one task. If a task packet would produce multiple unrelated outputs, split it before implementation.
