---
name: xlfg:plan
description: Recall first, diagnose the real problem, reject shortcut fixes, and write the shared contracts before coding.
argument-hint: "[feature description, bugfix, or product request]"
---

# /xlfg:plan

Create a real implementation plan. Do **not** write production code in this command.

<input_request>#$ARGUMENTS</input_request>

If the request is empty, ask the user what they want to build or fix and stop until you have a clear request.

## Hard rules

1. **No coding in this command.** Planning only.
2. **Recall is mandatory.** Do not broad-scan the repo until `memory-recall.md` exists.
3. **No late-thinking shortcuts.** The goal is the root solution, not the fastest patch.
4. **Do not hide behind “run the full suite later.”** The test contract must be scenario-based and explicit.
5. **Ask the user only blocking questions.** If a safe default exists, record it and proceed.
6. **Disconfirm yourself.** Every chosen solution must record what evidence would prove it wrong.

## Phase 0 — Fast scaffold check + create run

If `docs/xlfg/meta.json` is missing or stale, do the equivalent of `/xlfg:prepare` first.

Create a new `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>` and these paths:

- `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>/`
- `DX_RUN_DIR=.xlfg/runs/<RUN_ID>/`

Ensure the run contains at least:

- `context.md`
- `memory-recall.md`
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

## Phase 1 — Mandatory recall before you fan out

Before scanning the repo widely, load the smallest relevant slice of prior memory.

### 1A) Read the tracked handoff first

Read `docs/xlfg/knowledge/current-state.md` if present.

### 1B) Use the immediately preceding `/xlfg:recall` result if available

If `/xlfg` already ran `/xlfg:recall`, reuse its best findings.

### 1C) If recall has not already been done, do it now

Run deterministic recall yourself using `/xlfg:recall` or the equivalent manual lexical search discipline.

### 1D) Do one request-shaped recall, then one focused follow-up if needed

Minimum recall:
- one broad recall shaped by the raw request

Add a focused typed query if the request touches repeated harness / UX / testing / flow / environment risk.

Good example:

```bash
xlfg recall $'lex: "port already in use" yarn dev healthcheck\nstage: verify\nkind: failure harness-rule\nrole: env-doctor\nscope: memory runs'
```

Write `memory-recall.md` with all of these sections filled:
- queries / sources used
- strong matches
- rules carried into this run
- rejected near-matches / why they do not apply
- explicit no-hit statement when nothing relevant matched

You may not proceed to repo fan-out until `memory-recall.md` is non-placeholder.

## Phase 2 — Map the repo and hidden requirements

Run these agents in parallel. Each agent must write to its owned file.

- `xlfg-repo-mapper` → `repo-map.md`
- `xlfg-context-adjacent-investigator` → `context/adjacent.md`
- `xlfg-context-constraints-investigator` → `context/constraints.md`
- `xlfg-context-unknowns-investigator` → `context/unknowns.md`
- `xlfg-brainstorm` → `brainstorm.md` only if the request is materially ambiguous
- `xlfg-researcher` → `research.md` only if the stack or domain is unfamiliar / high-risk

## Phase 3 — Diagnose before solutioning

Run these agents next:

- `xlfg-root-cause-analyst` → `diagnosis.md`
- `xlfg-spec-author` → `flow-spec.md`
- `xlfg-test-strategist` → `test-contract.md`
- `xlfg-env-doctor` → `env-plan.md`
- `xlfg-solution-architect` → `solution-decision.md`
- `xlfg-risk-assessor` → `risk.md` when auth, money, destructive data, or reliability risk is present

Every specialist should prefer `current-state.md`, `memory-recall.md`, and exact role memory over broad vague recollection.

## Phase 4 — Reduce into canonical planning files

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
- one **disproof probe** or stop condition that would force diagnosis review
- stop conditions / blockers
- any recall-derived rule that must not be violated

The plan must align to `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, and `memory-recall.md`.

### `scorecard.md` must include

- every required F2P scenario
- every relevant P2P regression guard
- the exact check or evidence source for each item
- initial status set to `UNASSESSED`

## Plan gate before implementation

Do **not** continue to implementation until all are true:

- `memory-recall.md` exists and is specific
- `diagnosis.md` exists and identifies the real problem or capability gap
- `solution-decision.md` exists and records rejected shortcuts
- `flow-spec.md` is concrete enough to test from
- `test-contract.md` maps scenarios to explicit checks
- `env-plan.md` explains how local verification will avoid server/harness traps
- `plan.md` has bounded tasks with file scope and targeted checks
- at least one disconfirming probe exists in `solution-decision.md` or `plan.md`

## Completion

Print:

- `RUN_ID`
- the run folder path
- any blocking user questions (if truly blocking)
- a one-paragraph planning summary
