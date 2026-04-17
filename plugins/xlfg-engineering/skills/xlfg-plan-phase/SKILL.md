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
11. Update the objectives, tasks, blockers, and next-action sections of `workboard.md`. The `## Phase status` block is rendered by the conductor from `.xlfg/phase-state.json` — do not hand-write phase completion rows there. Create or refresh `tasks/<task-id>/task-brief.md` for each active task.
12. Create optional docs only when they change a decision or proof obligation: `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, `risk.md`.
13. If a required planning specialist returns only setup notes or no artifact, retry once via resume or exact re-dispatch before repairing the gap yourself. Do not collapse a broad packet into main-thread guesswork; re-split it first when needed.

## Readiness rule

If `test-readiness.md` is `REVISE`, repair the plan yourself until it becomes `READY` or a true human-only blocker is explicit. Do not ask the user to sequence replanning.

## Delegation packet rules

Follow `agents/_shared/dispatch-rules.md` for the full delegation contract (packet-size ladder, preseed rule, machine-readable headers with `PRIMARY_ARTIFACT` / `DONE_CHECK` / `RETURN_CONTRACT` / `OWNERSHIP_BOUNDARY` / `CONTEXT_DIGEST` / `PRIOR_SIBLINGS` / `Do not redo` / `Consume:`, micro-packet budget, proof budget, compaction, sequential-dispatch default, resume-same-specialist-before-fallback). Only the phase conductor may delegate.

Every plan-phase packet MUST begin with the machine-readable headers from `_shared/dispatch-rules.md §3`. `CONTEXT_DIGEST` carries **decisions + rationale + path refs**, not just facts, so siblings (`xlfg-root-cause-analyst` → `xlfg-solution-architect` → `xlfg-test-strategist` → `xlfg-task-divider`) build on each other instead of re-deriving the same diagnosis.

### Planning ownership boundaries

- `xlfg-why-analyst` owns user/operator value, non-goals, and false-success traps; it does not propose the solution.
- `xlfg-root-cause-analyst` owns causal mechanism and rejected symptom patches; it does not select the implementation option.
- `xlfg-solution-architect` owns option comparison and chosen solution; task hints stay non-canonical until `xlfg-task-divider` writes task packets.
- `xlfg-spec-author` owns behavior flow and scenario semantics; it does not choose proof commands or UI design acceptance IDs.
- `xlfg-ui-designer` owns UI/a11y design acceptance (`DA*`) and verify-time conformance; it does not duplicate review-phase UX critique.
- `xlfg-test-strategist` owns proof commands and scenario proof cards; it references flow scenario IDs and UI `DA*` IDs instead of restating their details.
- `xlfg-test-readiness-checker` owns the `READY`/`REVISE` gate only; it does not silently repair weak plans or invent new proof strategy.
- `xlfg-task-divider` owns canonical task IDs, scopes, owners, primary artifacts, and done checks. Default packet tier is **epic** (one packet per objective group); subdivide only when surfaces are truly unrelated.
- `xlfg-risk-assessor` owns safety gates, rollback triggers, and residual release pressure; it does not rewrite solution choice or proof cards.

Enforce the proof budget while creating task packets: each task `done_check` should be the cheapest honest task-local check, while broad build/full-suite/acceptance `ship_check` proof belongs to verify phase unless the task is the final integration lane or its changed surface requires that broad command immediately.

Compact specialist outputs before updating `spec.md`, `test-contract.md`, `test-readiness.md`, or `workboard.md`: carry forward decisions, scenario IDs, commands, task rows, blockers, and next action only; leave full reports in their artifacts. Do not paste full specialist reports into canonical run files.

## Guardrails

- Do not recreate the old split-file bureaucracy.
- If a fact already lives clearly in `spec.md`, do not mirror it elsewhere.
- Do not start implementation until the readiness gate is honest.
- For multi-objective runs, keep partial completion legible per objective instead of pretending the whole bundle is one task. If a task packet would produce multiple unrelated outputs, split it before implementation.
