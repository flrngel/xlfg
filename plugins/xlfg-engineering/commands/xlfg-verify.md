---
name: xlfg:verify
description: Run profile-aware layered verification and update the proof map, scorecard, and workboard with evidence.
argument-hint: "[run-id | latest] [fast|full]"
---

# /xlfg:verify

Run verification commands and save evidence.

<input>#$ARGUMENTS</input>

## 0) Parse arguments

Treat arguments as:

- First token: `run-id` (or `latest`)
- Optional second token: `fast` or `full`

If no mode is supplied, use the recommended verify mode from `harness-profile.md`.

## 1) Select run

- If argument is `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat argument as the run id

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

Read first (if present):

- `query-contract.md`
- `memory-recall.md`
- `why.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`
- `run-summary.md`
- `docs/xlfg/knowledge/current-state.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/failure-memory.md`
- `docs/xlfg/knowledge/harness-rules.md`
- `docs/xlfg/knowledge/agent-memory/env-doctor.md`
- `docs/xlfg/knowledge/agent-memory/verify-reducer.md`

Before running commands, mark in `workboard.md`:
- `verify: IN_PROGRESS`
- current next action
- note that the carry-forward anchor was re-read

## 2) Decide the layered verify plan

The verify plan must match **all three** of these:
- the selected harness profile
- the `proof-map.md` obligations
- the direct asks / non-negotiable implied asks in `query-contract.md`

### `fast`

Only the fastest feedback loop:

- lint / format / typecheck / static checks
- any ultra-cheap scenario proof explicitly required by `proof-map.md`
- any anti-monkey probe that is cheap enough to run now

### `full`

Run layers in this order:

1. Fast checks
2. Scenario-targeted smoke checks from `test-contract.md`
3. Required e2e / real-flow checks from `proof-map.md`
4. Broader regression suites and build/package checks

Important rules:

- **Do not jump straight to giant e2e by default.**
- **Verify the root solution, not just the absence of the old symptom.**
- Use `test-contract.md`, `proof-map.md`, and `query-contract.md` to decide which P0/P1 flows truly deserve smoke or e2e.
- Prefer **environment-state verification** when relevant (healthy port, correct bundle, correct endpoint behavior), not just proof that a start command was invoked.
- If `memory-recall.md`, `current-state.md`, or failure memory describes a repeated wrong-green trap, make sure the verify plan explicitly guards against it.
- A green command run is **not** enough if the proof map still has an unproven required scenario or if a direct ask is still uncovered.

## 3) Environment doctor (before smoke / e2e)

If smoke or e2e requires a local app/server:

- Reuse an already healthy server if safe
- Do **not** start another `yarn dev` / `npm run dev` on top of it
- Check port + health first
- Write a doctor report under `.xlfg/runs/<run-id>/doctor/<ts>/`

If the port is already in use but the configured healthcheck is unhealthy, stop and surface that as the first actionable failure.

## 4) Execute via verify runner

Run Task `xlfg-verify-runner` with:

- `DOCS_RUN_DIR`
- `DX_RUN_DIR`
- ordered layered commands
- any relevant notes from `env-plan.md`
- any repeated failure signatures from `memory-recall.md` or `current-state.md`
- any explicit proof obligations from `proof-map.md`
- the carry-forward anchor from `query-contract.md`

Runner responsibilities:

- create `DX_RUN_DIR/verify/<ts>/`
- write per-command logs + exit codes
- write `results.json`
- write `summary.md`

### Anti-hang rules

- prefer non-interactive execution
- for Node-based commands, set `CI=1` unless the repo forbids it
- do not run watch mode
- if a command appears to hang and `timeout` exists, use it
- if the same harness failure signature reappears, stop and classify it instead of looping blindly

## 5) Reduce via verify reducer

Run Task `xlfg-verify-reducer` with:

- `DOCS_RUN_DIR`
- `DX_RUN_DIR`
- the verify timestamp or results path

Reducer responsibilities:

- write `verification.md`
- update `scorecard.md`
- update `proof-map.md`
- update `workboard.md`
- if RED, write `verify-fix-plan.md`
- identify the **first actionable failure only**
- call out if the test contract is too weak to prove the chosen solution
- call out if a known repeated harness failure reappeared
- mark proof gaps explicitly when the commands were green but the requirement still is not honestly proven
- mark any uncovered direct asks or required implied asks explicitly

## 6) Gate rule

Verification is only GREEN when all are true:

- required commands passed for the selected mode
- required environment state was healthy when needed
- `scorecard.md` is green for required F2P / P2P items
- `proof-map.md` has no unresolved required proof gaps
- every direct ask in `query-contract.md` has evidence or an explicit user-approved deferral
- every non-negotiable implied ask in `query-contract.md` has evidence or an explicit user-approved deferral
- the evidence still matches `why.md` and the chosen root solution

If commands are green but the proof map still has a required gap, or the query contract is only partially covered, the run is RED.

## 7) If failing, iterate correctly

If verification is RED:

- fix the first actionable failure
- update `query-contract.md` if the failure changes the understanding of the request
- update `diagnosis.md` or `plan.md` if the failure changes the understanding of the problem
- update `harness-profile.md` if the proof requirement was underestimated
- re-run `/xlfg:verify`

Do not continue to review while verification is RED.

## 8) Finish verification phase

If GREEN:
- update `workboard.md` to `verify: DONE`
- set `review: NEXT`
- record the evidence location as the current next action
