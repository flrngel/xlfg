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

- first token: `run-id` (or `latest`)
- optional second token: `fast` or `full`

If no mode is supplied, use the recommended verify mode from `harness-profile.md`.

## 1) Select run

- If argument is `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat argument as the run id

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

Read first (if present):

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
- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/failure-memory.md`
- `docs/xlfg/knowledge/_views/harness-rules.md`
- `docs/xlfg/knowledge/_views/worktree.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/_views/agent-memory/env-doctor.md`
- `docs/xlfg/knowledge/_views/agent-memory/verify-reducer.md`

Before running commands, mark in `workboard.md`:
- `verify: IN_PROGRESS`
- current next action

## 2) Decide the layered verify plan

The verify plan must match **both** the selected harness profile and the `proof-map.md` obligations.

### `fast`

Only the fastest feedback loop:

- lint / format / typecheck / static checks
- any ultra-cheap scenario proof explicitly required by `proof-map.md`

### `full`

Run layers in this order:

1. fast checks
2. scenario-targeted smoke checks from `test-contract.md`
3. required e2e / real-flow checks from `proof-map.md`
4. broader regression suites and build/package checks

Important rules:

- do not jump straight to giant e2e by default
- verify the root solution, not just the absence of the old symptom
- use `test-contract.md` and `proof-map.md` to decide which P0/P1 flows truly deserve smoke or e2e
- prefer environment-state verification when relevant (healthy port, correct bundle, correct endpoint behavior), not just proof that a start command was invoked
- if `memory-recall.md`, `current-state.md`, failure-memory, or harness-rules describes a repeated wrong-green trap, make sure the verify plan explicitly guards against it
- a green command run is not enough if the proof map still has an unproven required scenario

## 3) Environment doctor (before smoke / e2e)

If smoke or e2e requires a local app/server:

- reuse an already healthy server if safe
- do not start another `yarn dev` / `npm run dev` on top of it
- check port + health first
- use `.xlfg/worktree.json` and `knowledge/_views/worktree.md` to keep branch/worktree context explicit
- write a doctor report under `.xlfg/runs/<run-id>/doctor/<ts>/`

If the port is already in use but the configured healthcheck is unhealthy, stop and surface that as the first actionable failure.

## 4) Execute via verify runner

Run Task `xlfg-verify-runner` with:

- `DOCS_RUN_DIR`
- `DX_RUN_DIR`
- ordered layered commands
- any relevant notes from `env-plan.md`
- repeated failure signatures from memory or current-state
- explicit proof obligations from `proof-map.md`

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
