---
description: Internal xlfg phase skill. Use only during /xlfg runs to run layered proof, reduce results into verification.md, and surface the first actionable failure.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write, Agent
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
4. When the helper is unavailable or insufficient, use the verify specialists:
   - `xlfg-env-doctor`
   - `xlfg-verify-runner`
   - `xlfg-verify-reducer`
5. Write or update `verification.md` with real evidence.
6. If verification is RED, write or update `verify-fix-plan.md` with the first actionable failure only.
7. Update `workboard.md` with the verification status and next action.

## Green rule

Do not call the run GREEN unless scenario-targeted proof actually ran for the changed behavior and the evidence matches the claims in `spec.md`.

## Guardrails

- Static checks alone are not enough for behavioral work.
- Prefer the first actionable failure over a giant wall of logs.
- If the dev harness itself is unhealthy, classify that honestly before looping.
