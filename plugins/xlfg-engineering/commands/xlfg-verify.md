---
name: xlfg:verify
description: Run layered verification (fast, smoke, e2e, regression) and write evidence.
argument-hint: "[run-id | latest] [fast|full]"
---

# /xlfg:verify

Run verification commands and save evidence.

<input>#$ARGUMENTS</input>

## 0) Parse arguments

Treat arguments as:

- First token: `run-id` (or `latest`)
- Optional second token: `fast` or `full`

Default mode: `full`.

## 1) Select run

- If argument is `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat argument as the run id

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

Read first (if present):

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `scorecard.md`
- `run-summary.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/failure-memory.md`
- `docs/xlfg/knowledge/harness-rules.md`
- `docs/xlfg/knowledge/agent-memory/verify-reducer.md`

## 2) Decide the layered verify plan

### `fast`

Only the fastest feedback loop:

- lint / format / typecheck / static checks

### `full`

Run layers in this order:

1. Fast checks
2. Scenario-targeted smoke checks from `test-contract.md`
3. Required e2e / real-flow checks
4. Broader regression suites and build/package checks

Important rules:

- **Do not jump straight to giant e2e by default.**
- **Verify the root solution, not just the absence of the old symptom.**
- Use `test-contract.md` to decide which P0/P1 flows truly deserve smoke or e2e.
- Prefer **environment-state verification** when relevant (healthy port, correct bundle, correct endpoint behavior), not just proof that a start command was invoked.

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

## 5) Reduce via verify reducer

Run Task `xlfg-verify-reducer` with:

- `DOCS_RUN_DIR`
- `DX_RUN_DIR`
- the verify timestamp or results path

Reducer responsibilities:

- write `verification.md`
- update `scorecard.md`
- if RED, write `verify-fix-plan.md`
- identify the **first actionable failure only**
- call out if the test contract is too weak to prove the chosen solution

## 6) If failing, iterate correctly

If verification is RED:

- fix the first actionable failure
- update `diagnosis.md` or `plan.md` if the failure changes the understanding of the problem
- re-run `/xlfg:verify`

Do not continue to review while verification is RED.
