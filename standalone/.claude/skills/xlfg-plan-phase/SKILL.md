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
5. Keep specialists foregrounded and require their artifacts before synthesis. Default to sequential plan specialists unless two packets are truly independent. If a specialist returns only setup notes or a missing artifact, use `SendMessage` with the returned agent ID to resume the same specialist once. If no agent ID is available, re-dispatch the same packet once.
6. The main conductor should synthesize `spec.md` and the final plan from specialist artifacts instead of replacing those lanes with its own first-pass reasoning.
7. Update `spec.md` as the single source of truth:
   - keep the intent contract and objective groups accurate
   - fill outcome / why and false-success trap
   - record repo and external findings
   - set execution shape and verify mode
   - record the chosen solution and rejected shortcuts
   - map tasks to objective IDs and scenario IDs
   - ensure each active task records `scope`, `primary_artifact`, and `done_check` in the `Task map`
   - keep proof summary and PM / UX / Engineering / QA / Release notes current
8. Update `test-contract.md` with 1–5 practical scenario contracts total, ensuring each active objective has explicit proof.
9. Update `test-readiness.md` with a real `READY` or `REVISE` verdict.
10. Update `workboard.md` so objectives, tasks, blockers, and the next action stay visible. Create or refresh `tasks/<task-id>/task-brief.md` for each active task.
11. Create optional docs only when they change a decision or proof obligation: `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, `risk.md`.
12. If a required planning specialist returns only setup notes or no artifact, retry once via resume or exact re-dispatch before repairing the gap yourself. Do not collapse a broad packet into main-thread guesswork; re-split it first when needed.

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
- Default to **sequential** dispatch for artifact-producing planning/context work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Guardrails

- Do not recreate the old split-file bureaucracy.
- If a fact already lives clearly in `spec.md`, do not mirror it elsewhere.
- Do not start implementation until the readiness gate is honest.
- For multi-objective runs, keep partial completion legible per objective instead of pretending the whole bundle is one task. If a task packet would produce multiple unrelated outputs, split it before implementation.
