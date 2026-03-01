---
name: xlfg
description: Ship production-ready code via contracts, layered verification, and compounding.
argument-hint: "[feature/bugfix request]"
---

# /xlfg

Run an end-to-end software development workflow that produces **real, verifiable output**.

<input_request>#$ARGUMENTS</input_request>

## Core shift in this version

This workflow is **not**:

> define loosely → implement → ask late if it works

This workflow **is**:

> define the user flow → define the shared test contract → define the environment contract → implement against that contract → verify in layers → compound real failures

## Core invariants

1. **Do not code until `flow-spec.md`, `test-contract.md`, and `env-plan.md` exist.**
2. **Implementation and verification share the same contract.**
3. **Evidence-first:** never claim done without green verification and logs.
4. **Environment discipline:** do not blindly start duplicate dev servers.
5. **Compounding must be concrete and verified.**

## Runtime discipline (so this does not waste hackathon time)

Choose a tier up front:

- **Tier S** — 1–2 files, low risk, no meaningful new user flow
- **Tier M** — normal feature / bugfix, a few files, at least one changed scenario
- **Tier L** — cross-cutting, risky, multiple surfaces, or major UX flow change

Default to **Tier M**.

### Minimum fan-out by tier

| Phase | Tier S | Tier M | Tier L |
|---|---:|---:|---:|
| Flow contract | lead may write directly | spawn `xlfg-spec-author` | spawn `xlfg-spec-author` |
| Test contract | lead may write directly | spawn `xlfg-test-strategist` | spawn `xlfg-test-strategist` |
| Env plan | lead may write directly | spawn `xlfg-env-doctor` | spawn `xlfg-env-doctor` |
| Risk | optional | spawn if risky | spawn `xlfg-risk-assessor` |
| Implementation checker | **always spawn** | **always spawn** | **always spawn** |
| Verify | lead may run inline | spawn verify runner + reducer | spawn verify runner + reducer |
| Review | optional | security + architecture | full set |

## Important limitation

Claude Code slash commands are not truly composable. This command is therefore written to be **self-contained**: perform init / verify / review / compound steps inline unless you explicitly want to invoke subcommands yourself.

## Phase 0 — Ensure scaffolding exists

If `docs/xlfg/index.md` does not exist, bootstrap scaffolding inline (equivalent to `/xlfg:init`) and continue.

## Phase 1 — Create a run folder

1. Generate `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>`
2. Create:
   - `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>/`
   - `DX_RUN_DIR=.xlfg/runs/<RUN_ID>/`
3. Ensure the run contains at least:
   - `context.md`
   - `flow-spec.md`
   - `spec.md`
   - `plan.md`
   - `test-contract.md`
   - `env-plan.md`
   - `scorecard.md`
   - `tasks/`

Record the raw user request and known constraints in `context.md`.

## Phase 2 — Define **what to build**

Before planning HOW, define the shared behavior contract.

### Required output

Create or update `DOCS_RUN_DIR/flow-spec.md` with explicit scenarios.

For every meaningful user-facing or system-facing behavior, include:

- scenario ID (`P0-1`, `P1-2`, etc.)
- actor / preconditions
- exact steps
- alternate steps when relevant
- failure / empty / loading states
- assertions
- keyboard / accessibility notes when UI is involved
- telemetry / observability notes if relevant

Example shape:

- user focuses input by click
- user focuses input by keyboard / tab
- user submits by Enter
- user submits by button click
- error state is shown when invalid
- same flow remains keyboard-usable

### How to generate it

- **Tier S:** lead may write the contract directly
- **Tier M/L:** spawn `xlfg-spec-author` to write `flow-spec.md`
- If the request is ambiguous, optionally run `xlfg-brainstorm` first

Also update `spec.md` with a short summary + acceptance criteria + non-goals.

## Phase 3 — Define **what to test** and **how the environment must behave**

### 3A) Test contract

Create `DOCS_RUN_DIR/test-contract.md`.

This file must map the flow contract to verification:

- **F2P** — new / changed behavior to prove
- **P2P** — existing behavior to preserve
- fastest relevant check for each scenario
- required smoke / e2e checks
- broader regression suites
- manual smoke checklist if needed

Rules:

- do not say only "run the full test suite"
- do not treat all flows as e2e-worthy
- prefer the fastest targeted check that proves the scenario

### 3B) Environment plan

Create `DOCS_RUN_DIR/env-plan.md`.

This file must define:

- install command(s)
- dev server command
- port / healthcheck
- reuse-if-healthy policy
- startup timeout
- cleanup rule
- anti-hang rule (watch mode off, `CI=1`, etc.)
- known environment traps from prior runs

### 3C) Risk

If risky, write `DOCS_RUN_DIR/risk.md`.

### How to generate these

- **Tier S:** lead may write directly
- **Tier M/L:** spawn `xlfg-test-strategist` and `xlfg-env-doctor`
- spawn `xlfg-risk-assessor` when the domain is risky or unfamiliar

## Phase 4 — Reduce into the implementation plan

Write `DOCS_RUN_DIR/plan.md`.

Rules for the plan:

- tasks must align to scenario IDs from `flow-spec.md`
- keep tasks coarse enough to avoid subagent thrash
- include the targeted check to run after each task
- define the ship gate clearly

Update `scorecard.md` with the scenarios that must eventually be GREEN.

## Phase 5 — Implement against the contract

For every plan task:

1. Scope the task to files + scenario IDs
2. Implement the code and required tests
3. Write `tasks/<task-id>/implementer-report.md`
4. Spawn `xlfg-task-checker`
5. Checker writes `tasks/<task-id>/checker-report.md`
6. Only mark the task done when checker verdict is `ACCEPT`

### Crucial rule

After each task, run the **fastest targeted check from `test-contract.md`**.

Do **not** jump to full e2e after every small change unless the contract says that task cannot be trusted without it.

### Anti-loop rule

If the same command or same failure repeats twice without a new hypothesis:

- stop the blind rerun loop
- write the blocker into the run
- treat it as a harness / environment / diagnosis problem

## Phase 6 — Verify (hard gate)

Perform verification inline (equivalent to `/xlfg:verify <RUN_ID>`).

Required order:

1. fast checks
2. scenario-targeted smoke
3. required e2e / real-flow checks
4. broader regression suites and build

Before smoke or e2e, run the environment doctor.

Outputs required:

- `.xlfg/runs/<RUN_ID>/verify/<ts>/...`
- `verification.md`
- `scorecard.md`
- `verify-fix-plan.md` if RED

If verification fails:

- fix the first actionable failure
- re-run verification
- do not continue shipping while RED

## Phase 7 — Review (hard gate)

Perform review inline (equivalent to `/xlfg:review <RUN_ID>`).

- Tier S: brief lead review is acceptable only for trivial low-risk changes
- Tier M: security + architecture reviewers required; UX/perf when relevant
- Tier L: all review lenses required

Reviewers must use the flow / test / environment contract when evaluating coverage gaps.

## Phase 8 — Ship artifacts

Ensure `run-summary.md` exists with:

- what changed
- how to test manually
- verification commands and log paths
- post-deploy monitoring or explicit reason none is needed
- rollback plan

## Phase 9 — Compound and evolve

Perform compounding inline (equivalent to `/xlfg:compound <RUN_ID>`).

Update durable knowledge when the run teaches something concrete:

- `testing.md`
- `ux-flows.md`
- `failure-memory.md`
- `harness-rules.md`
- `patterns.md`
- `decision-log.md`
- `quality-bar.md`

Only compound lessons that are real, specific, and reusable.

## Completion criteria

Only declare success when:

- `flow-spec.md` exists and matches what was built
- `test-contract.md` exists and matches what was verified
- `env-plan.md` exists and explains the harness used
- `plan.md` checkboxes are complete
- every task has implementer + checker reports, and checker says `ACCEPT`
- verification is green and logs exist
- review has no P0 blockers
- `scorecard.md` reflects green required scenarios
- `run-summary.md` exists
- `compound-summary.md` exists
