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
3. Prefer the helper when available:
   - `xlfg verify --run <RUN_ID> --mode auto`
   - or `fast` / `full` when the run card makes the choice obvious
4. When the helper is unavailable or insufficient, use the verify specialists as lane owners with one required artifact each:
   - always run `xlfg-verify-runner`
   - then always run `xlfg-verify-reducer`
   - run `xlfg-env-doctor` when the harness is unhealthy or the proof depends on a running app
   - run `xlfg-ui-designer` as a design-vs-implementation verification lane when the task is UI-related — same trigger as plan-phase (intent mentions UI / frontend / visual / interaction / layout / component / screen / a11y, or the changed FILE_SCOPE includes `*.tsx|*.jsx|*.vue|*.svelte|*.html|*.css|*.scss|*.sass|*.less|*.styl` or files under common frontend dirs `src/components/`, `app/`, `pages/`, `ui/`, `frontend/`, `web/`). Dispatch with `PRIMARY_ARTIFACT: DOCS_RUN_DIR/ui-verification.md` and pass the plan-phase `ui-design.md` as the contract to verify against. Skip for pure-backend runs.
5. Keep verify fan-out small. Run one active verify specialist at a time in the required order above; do not ask verify specialists to spawn more specialists.
6. Keep these specialists foregrounded, short-lived, and leaf-only. Missing verify artifacts mean verification did not actually happen.
7. Require the verify artifacts to exist before accepting phase completion: `results.json`, `summary.md`, `verification.md`, and any required fix plan. If a specialist returns early without them or only narrates next steps, use `SendMessage` with the returned agent ID to resume the same specialist once. If no agent ID is available, re-dispatch the exact same packet once. Only then may you classify the phase as FAILED / RED.
8. Write or update `verification.md` with real evidence.
9. If verification is RED, write or update `verify-fix-plan.md` with the first actionable failure only.
10. Update `workboard.md` with the verification status and next action.

## Green rule

Do not call the run GREEN unless scenario-targeted proof actually ran for the changed behavior and the evidence matches the claims in `spec.md`.

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
- Only the phase conductor may delegate. Never ask a verify specialist to spawn nested subagents or hand off its lane to another worker.
- Default to **sequential** dispatch for artifact-producing planning/context work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Guardrails

- Static checks alone are not enough for behavioral work.
- Prefer the first actionable failure over a giant wall of logs.
- If the dev harness itself is unhealthy, classify that honestly before looping.
