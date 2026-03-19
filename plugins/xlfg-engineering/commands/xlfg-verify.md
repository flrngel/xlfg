---
name: xlfg:verify
description: Run proof-first verification with minimal context load, honest environment handling, and scorecard updates.
argument-hint: "[run-id | latest] [fast|full]"
---

# /xlfg:verify

Run verification commands and save evidence.

<input>#$ARGUMENTS</input>

## 0) Parse arguments

Treat arguments as:

- first token: `run-id` (or `latest`)
- optional second token: `fast` or `full`

If no mode is supplied, use the recommendation from `harness-profile.md`.

## 1) Select run

- If argument is `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat argument as the run id

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

Always read these first:

- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `proof-map.md`
- `workboard.md`
- `run-summary.md` if present

Read these only when needed:

- `query-contract.md`
- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `env-plan.md`
- `scorecard.md`
- `docs/xlfg/knowledge/current-state.md`
- `docs/xlfg/knowledge/commands.json`
- relevant failure / harness memory

Before running commands, mark in `workboard.md`:

- `verify: IN_PROGRESS`
- current next action
- active verify mode

## 2) Verify plan

The verify plan must satisfy all of these:

- the selected harness profile
- the scenario contract in `test-contract.md`
- the required evidence in `proof-map.md`
- the acceptance bar described by `spec.md`

### `fast`

Run the shortest honest feedback loop:

- declared `fast_check` for changed scenarios
- cheap lint / format / type / static checks when relevant
- cheap anti-monkey probes already called for by the plan

### `full`

Run layers in this order:

1. fast checks
2. scenario-targeted smoke checks
3. required e2e or real-flow checks
4. broader regression / build checks when justified

Rules:

- Do not jump straight to giant suites by default.
- Do not call static checks alone “verification” when the changed work is behavioral.
- Green commands are not enough if `proof-map.md` still overclaims or leaves a required gap.
- If `test-readiness.md` says `REVISE`, the run is RED until planning is fixed.

## 3) Environment handling

If smoke or e2e needs a local server:

- reuse a healthy one when safe
- do not start duplicates
- check port and health before assuming success
- write doctor output under `.xlfg/runs/<run-id>/doctor/<ts>/`

If the configured server is unhealthy, stop on the first actionable failure.

## 4) Adaptive verify agents

Use:

1. `xlfg-verify-runner` to execute layered commands and capture logs
2. `xlfg-verify-reducer` to write `verification.md`, update `scorecard.md`, update `proof-map.md`, and record the first actionable failure

## 5) Gate rule

Verification is GREEN only when all are true:

- required commands passed for the chosen mode
- `test-readiness.md` is `READY`
- scenario-targeted proof actually ran for changed scenarios
- required F2P / P2P items are green in `scorecard.md`
- `proof-map.md` has no unresolved required gaps
- `spec.md` still matches what was proven

If commands are green but the requirement is not honestly proven, the run is RED.

## 6) If failing, iterate correctly

If verification is RED:

- fix the first actionable failure
- update plan/proof artifacts when the failure changes the truth
- re-run `/xlfg:verify`

Do not continue to review while verification is RED.

## 7) Finish verification

If GREEN:

- update `workboard.md` to `verify: DONE`
- set `review: NEXT`
- record evidence locations and a brief PM / Engineering / QA status update
