---
name: xlfg:plan
description: Diagnose the real problem, reject shortcut fixes, and write the shared contracts before coding.
argument-hint: "[feature description, bugfix, or product request]"
---

# /xlfg:plan

Create a real implementation plan. Do **not** write production code in this command.

<input_request>#$ARGUMENTS</input_request>

If the request is empty, ask the user what they want to build or fix and stop until you have a clear request.

## Hard rules

1. **No coding in this command.** Planning only.
2. **No late-thinking shortcuts.** The goal is the root solution, not the fastest patch.
3. **Do not hide behind “run the full suite later.”** The test contract must be scenario-based and explicit.
4. **Ask the user only blocking questions.** If a safe default exists, record it and proceed.

## Phase 0 — Ensure scaffolding + create run

If `docs/xlfg/index.md` is missing, do the equivalent of `/xlfg:init` first.

Create a new `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>` and these paths:

- `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>/`
- `DX_RUN_DIR=.xlfg/runs/<RUN_ID>/`

Ensure the run contains at least:

- `context.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `env-plan.md`
- `scorecard.md`
- `tasks/`

Write the raw request and known constraints to `context.md`.

## Phase 1 — Map the repo and hidden requirements

Run these agents in parallel. Each agent must write to its owned file.

- `xlfg-repo-mapper` → `repo-map.md`
- `xlfg-context-adjacent-investigator` → `context/adjacent.md`
- `xlfg-context-constraints-investigator` → `context/constraints.md`
- `xlfg-context-unknowns-investigator` → `context/unknowns.md`
- `xlfg-brainstorm` → `brainstorm.md` only if the request is materially ambiguous
- `xlfg-researcher` → `research.md` only if the stack or domain is unfamiliar / high-risk

## Phase 2 — Diagnose before solutioning

Run these agents next:

- `xlfg-root-cause-analyst` → `diagnosis.md`
- `xlfg-spec-author` → `flow-spec.md`
- `xlfg-test-strategist` → `test-contract.md`
- `xlfg-env-doctor` → `env-plan.md`
- `xlfg-solution-architect` → `solution-decision.md`
- `xlfg-risk-assessor` → `risk.md` when auth, money, destructive data, or reliability risk is present

## Phase 3 — Reduce into canonical planning files

Write `spec.md` and `plan.md` yourself by reducing the agent outputs.

### `spec.md` must include

- the problem in plain language
- the actual root cause / missing capability
- the chosen solution
- rejected shortcut solutions and why they are not acceptable
- acceptance criteria
- non-goals
- rollout / rollback notes if relevant

### `plan.md` must include

Keep the plan coarse. Aim for **3–7 tasks**, not a task explosion.

For each task include:

- task ID (`T1`, `T2`, ...)
- scenario IDs covered
- goal
- allowed file scope
- targeted checks to run after the task
- invariants that must stay true
- stop conditions / blockers

The plan must align to `diagnosis.md`, `solution-decision.md`, and `flow-spec.md`.

### `scorecard.md` must include

- every required F2P scenario
- every relevant P2P regression guard
- the exact check or evidence source for each item
- initial status set to `UNASSESSED`

## Plan gate before implementation

Do **not** continue to implementation until all are true:

- `diagnosis.md` exists and identifies the real problem or capability gap
- `solution-decision.md` exists and records rejected shortcuts
- `flow-spec.md` is concrete enough to test from
- `test-contract.md` maps scenarios to explicit checks
- `env-plan.md` explains how local verification will avoid server/harness traps
- `plan.md` has bounded tasks with file scope and targeted checks

## Completion

Print:

- `RUN_ID`
- the run folder path
- any blocking user questions (if truly blocking)
- a one-paragraph planning summary
