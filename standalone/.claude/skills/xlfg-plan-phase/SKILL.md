---
description: Internal xlfg phase skill. Use only during /xlfg runs to turn intent plus context into a lean run card, practical proof contract, and READY gate.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, Agent
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
   - always run `xlfg-test-readiness-checker` before implementation
   - run `xlfg-why-analyst` when user value, UX, or operator impact matters
   - run `xlfg-spec-author` when scenario-level flow detail is needed
   - run `xlfg-risk-assessor` for higher-risk changes
   - run `xlfg-env-doctor` when the proof depends on a running app
   - run `xlfg-researcher` only if context phase proved that repo truth is insufficient
   - run `xlfg-brainstorm` only when the intent phase left multiple viable solution directions
5. Keep specialists foregrounded and require their artifacts before synthesis.
6. The main conductor should synthesize `spec.md` and the final plan from specialist artifacts instead of replacing those lanes with its own first-pass reasoning.
7. Update `spec.md` as the single source of truth:
   - keep the intent contract and objective groups accurate
   - fill outcome / why and false-success trap
   - record repo and external findings
   - set execution shape and verify mode
   - record the chosen solution and rejected shortcuts
   - map tasks to objective IDs and scenario IDs
   - keep proof summary and PM / UX / Engineering / QA / Release notes current
8. Update `test-contract.md` with 1–5 practical scenario contracts total, ensuring each active objective has explicit proof.
9. Update `test-readiness.md` with a real `READY` or `REVISE` verdict.
10. Update `workboard.md` so objectives, tasks, blockers, and the next action stay visible.
11. Create optional docs only when they change a decision or proof obligation: `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, `risk.md`.
12. If a required planning specialist returns only setup notes or no artifact, retry once or record the failure before repairing the gap yourself.

## Readiness rule

If `test-readiness.md` is `REVISE`, repair the plan yourself until it becomes `READY` or a true human-only blocker is explicit. Do not ask the user to sequence replanning.

## Guardrails

- Do not recreate the old split-file bureaucracy.
- If a fact already lives clearly in `spec.md`, do not mirror it elsewhere.
- Do not start implementation until the readiness gate is honest.
- For multi-objective runs, keep partial completion legible per objective instead of pretending the whole bundle is one task.
