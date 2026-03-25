---
description: Internal xlfg phase skill. Use only during /xlfg runs to turn recall and context into a lean run card, practical proof contract, and READY gate.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, Agent
---


# xlfg-plan-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Turn the gathered truth into a lean run card, a practical test contract, and a real readiness gate.

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
3. Use only the specialists that materially improve the plan:
   - `xlfg-query-refiner`
   - `xlfg-why-analyst`
   - `xlfg-root-cause-analyst` when debugging or symptom-heavy work
   - `xlfg-solution-architect`
   - `xlfg-test-strategist`
   - `xlfg-test-readiness-checker`
   - `xlfg-risk-assessor` for higher-risk changes
   - `xlfg-researcher` only if context phase proved that repo truth is insufficient
4. Update `spec.md` as the single source of truth:
   - direct asks, implied asks, and non-goals
   - outcome / why and false-success trap
   - repo and external findings
   - execution shape and verify mode
   - chosen solution and rejected shortcuts
   - task map
   - proof summary
   - PM / UX / Engineering / QA / Release notes
5. Update `test-contract.md` with 1–5 practical scenario contracts total.
6. Update `test-readiness.md` with a real `READY` or `REVISE` verdict.
7. Update `workboard.md` so the current plan and next action are visible.
8. Create optional docs only when they change a decision or proof obligation: `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, `risk.md`.

## Readiness rule

If `test-readiness.md` is `REVISE`, repair the plan yourself until it becomes `READY` or a true human-only blocker is explicit. Do not ask the user to sequence replanning.

## Guardrails

- Do not recreate the old split-file bureaucracy.
- If a fact already lives clearly in `spec.md`, do not mirror it elsewhere.
- Do not start implementation until the readiness gate is honest.
