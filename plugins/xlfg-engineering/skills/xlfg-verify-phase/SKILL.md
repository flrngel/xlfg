---
description: Internal xlfg phase skill. Use only during /xlfg runs to run layered proof, reduce results into verification.md, and surface the first actionable failure.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write, Agent, SendMessage
---

# xlfg-verify-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Run honest layered proof for the changed behavior and reduce the results into a crisp pass/fail state.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read:
   - `spec.md`
   - `test-contract.md`
   - `test-readiness.md`
   - `workboard.md`
   - optional `proof-map.md`, `env-plan.md`, `risk.md`
   - `docs/xlfg/knowledge/current-state.md`
3. Run the planned test commands directly:
   - Execute the commands defined in `test-contract.md` `fast_check` and `ship_check` fields
   - Default test runner: `python3 -m unittest discover tests/ -v` unless `test-contract.md` specifies otherwise
   - **Smoke-first rule for `ship_phase: acceptance` scenarios**: if any scenario declares `ship_phase: acceptance`, run its `smoke_check` first. On deterministic smoke failure (identifiable pattern, non-flaky), stop immediately, classify RED, write `verify-fix-plan.md` from the smoke failure, and do NOT run `ship_check` this round. Only escalate to acceptance when the smoke result is green or shows a clearly non-deterministic pattern. This prevents paying 3× (or more) for a deterministic bug that one run already diagnosed.
4. Use the verify specialists as lane owners with one required artifact each:
   - always run `xlfg-verify-runner`
   - then always run `xlfg-verify-reducer`
   - run `xlfg-env-doctor` when the harness is unhealthy or the proof depends on a running app
   - run `xlfg-ui-designer` as a design-vs-implementation verification lane when the task is UI-related — same trigger as plan-phase (intent mentions UI / frontend / visual / interaction / layout / component / screen / a11y, or the changed FILE_SCOPE includes `*.tsx|*.jsx|*.vue|*.svelte|*.html|*.css|*.scss|*.sass|*.less|*.styl` or files under common frontend dirs `src/components/`, `app/`, `pages/`, `ui/`, `frontend/`, `web/`). **Gate on task-checker DA coverage**: before dispatching, scan the most recent `tasks/<task-id>/checker-report.md` artifacts produced during implement-phase. If every plan-phase DA id (`DA1`..`DAN` in `ui-design.md`) is marked `pass` in at least one checker report, skip this lane and append a one-line skip note to `verification.md` (`xlfg-ui-designer skipped — task-checker DAs covered`). Run only when checker reports are missing, leave any DA unresolved, or mark any DA `fail`. Dispatch with `PRIMARY_ARTIFACT: DOCS_RUN_DIR/ui-verification.md` and pass the plan-phase `ui-design.md` as the contract to verify against. Skip for pure-backend runs.
5. Keep verify fan-out small. Run one active verify specialist at a time in the required order above; do not ask verify specialists to spawn more specialists.
6. Keep these specialists foregrounded, short-lived, and leaf-only. Missing verify artifacts mean verification did not actually happen.
7. Require the verify artifacts to exist before accepting phase completion: `results.json`, `summary.md`, `verification.md`, and any required fix plan. If a specialist returns early without them or only narrates next steps, use `SendMessage` with the returned agent ID to resume the same specialist once. If no agent ID is available, re-dispatch the exact same packet once. Only then may you classify the phase as FAILED / RED.
8. Write or update `verification.md` with real evidence.
9. If verification is RED, write or update `verify-fix-plan.md` with the first actionable failure only.
10. Update the verification-status and next-action sections of `workboard.md`. The `## Phase status` block is rendered by the conductor from `.xlfg/phase-state.json`.

## Green rule

Do not call the run GREEN unless scenario-targeted proof actually ran for the changed behavior and the evidence matches the claims in `spec.md`.

## Delegation packet rules

Follow `agents/_shared/dispatch-rules.md` for the full delegation contract (packet-size ladder, preseed rule, machine-readable headers with `PRIMARY_ARTIFACT` / `DONE_CHECK` / `RETURN_CONTRACT` / `OWNERSHIP_BOUNDARY` / `CONTEXT_DIGEST` / `PRIOR_SIBLINGS` / `Do not redo` / `Consume:`, micro-packet budget, proof budget, compaction, sequential-dispatch default, resume-same-specialist-before-fallback). Only the phase conductor may delegate.

Every verify-phase packet MUST begin with the machine-readable headers from `_shared/dispatch-rules.md §3`. `CONTEXT_DIGEST` carries scenario IDs and harness facts so the specialist does not re-read upstream phase outputs. Siblings is how `xlfg-verify-reducer` consumes `xlfg-verify-runner`'s `results.json`/`summary.md` instead of re-running the harness or re-summarizing logs from scratch.

### Verification ownership boundaries

- `xlfg-verify-runner` owns command execution and raw evidence capture only; it does not judge final run truth beyond noting observed failures.
- `xlfg-verify-reducer` owns GREEN/RED/FAILED reduction and first actionable failure; it consumes runner artifacts and must not rerun commands unless the packet explicitly asks for a missing-artifact recovery.
- `xlfg-env-doctor` owns harness health classification only when the harness is unhealthy or running-app proof depends on it.
- `xlfg-ui-designer` verify mode owns DA conformance only when checker reports did not already pass every DA; it does not duplicate review-phase UX critique.

Keep dispatches as **micro-packets**: command order, scenario IDs, prior task evidence anchors, and stop conditions only. Do not paste full task reports or long logs into verify packets; point to the artifacts instead.

Treat implementation `DONE_CHECK` results as prior evidence. Verify phase owns broad `fast_check`, `smoke_check`, and `ship_check` proof; run each declared command once per verify invocation unless retrying a classified harness/flaky failure.

Compact runner/reducer artifacts before updating `verification.md`, `proof-map.md`, or `workboard.md`: carry forward commands, exit codes, log paths, GREEN/RED/FAILED status, first actionable failure, and next action only. Do not paste full specialist reports into canonical run files.

## Guardrails

- Static checks alone are not enough for behavioral work.
- Prefer the first actionable failure over a giant wall of logs.
- If the dev harness itself is unhealthy, classify that honestly before looping.
