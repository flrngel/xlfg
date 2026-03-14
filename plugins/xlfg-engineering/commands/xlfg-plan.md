---
name: xlfg:plan
description: Start from why, load the right memory, diagnose the root problem, pick the minimum honest harness profile, and write the shared contracts before coding.
argument-hint: "[feature description, bugfix, or product request]"
---

# /xlfg:plan

Create a real implementation plan. Do **not** write production code in this command.

<input_request>#$ARGUMENTS</input_request>

If the request is empty, ask the user what they want to build or fix and stop until you have a clear request.

## Hard rules

1. **No coding in this command.** Planning only.
2. **Recall is mandatory.** Do not broad-scan the repo until `memory-recall.md` exists.
3. **Start with why.** If `why.md` is weak, every later artifact becomes shallow.
4. **No late-thinking shortcuts.** The goal is the root solution, not the fastest patch.
5. **Do not hide behind “run the full suite later.”** The test contract must be scenario-based and explicit.
6. **Pick the minimum honest harness profile.** Do not over-fan-out by default.
7. **Ask the user only blocking questions.** If a safe default exists, record it and proceed.
8. **Disconfirm yourself.** Every chosen solution must record what evidence would prove it wrong.

## Phase 0 — Fast scaffold check + create run

If `docs/xlfg/meta.json` is missing or stale, do the equivalent of `/xlfg:prepare` first.

Create a new `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>` and these paths:

- `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>/`
- `DX_RUN_DIR=.xlfg/runs/<RUN_ID>/`

Ensure the run contains at least:

- `context.md`
- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `env-plan.md`
- `workboard.md`
- `proof-map.md`
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

## Phase 2 — Write the why before the what

Run `xlfg-why-analyst` → `why.md`

`why.md` must make these concrete:
- who is affected
- what failure / friction / missed capability matters now
- what false success would look like
- the non-negotiable quality bar for this run
- non-goals

If the why is still mushy after one pass, stop and ask a blocking question instead of pretending the goal is clear.

## Phase 3 — Minimum mapping and core diagnosis

Do the smallest repo fan-out that can support an honest diagnosis.

### Required core agents

Run these agents. Each agent must write to its owned file.

- `xlfg-repo-mapper` → `repo-map.md`
- `xlfg-root-cause-analyst` → `diagnosis.md`
- `xlfg-spec-author` → `flow-spec.md`
- `xlfg-test-strategist` → `test-contract.md`
- `xlfg-env-doctor` → `env-plan.md`
- `xlfg-solution-architect` → `solution-decision.md`
- `xlfg-harness-profiler` → `harness-profile.md`

### Optional agents — only when triggered

Run optional agents **only** if the core diagnosis shows a real need:

- `xlfg-context-adjacent-investigator` → `context/adjacent.md` when nearby systems or sibling flows materially affect the change
- `xlfg-context-constraints-investigator` → `context/constraints.md` when infra / policy / API / deployment constraints meaningfully shape the solution
- `xlfg-context-unknowns-investigator` → `context/unknowns.md` when unknowns are blocking or high-risk
- `xlfg-brainstorm` → `brainstorm.md` only if the request is materially ambiguous after `why.md`
- `xlfg-researcher` → `research.md` only if the stack or domain is unfamiliar / high-risk
- `xlfg-risk-assessor` → `risk.md` when auth, money, destructive data, or reliability risk is present

Do **not** fan out to optional agents just because they exist.

## Phase 4 — Choose the harness profile

`harness-profile.md` must choose the smallest honest profile:

- `quick` — tight bugfix / local change / low risk / limited scope
- `standard` — normal product work with moderate scope or one user-facing flow
- `deep` — auth, money, destructive data, migrations, high reliability risk, or large unknowns

The profile must define:
- max ordered tasks
- max checker loops per task
- max parallel subagents
- recommended verify mode (`fast` or `full`)
- required review lenses
- escalation triggers that force stepping up to a deeper profile

If the request is risky but the profile stays `quick`, explain why that is still honest. Otherwise escalate.

## Phase 5 — Reduce into canonical planning files

Write `spec.md` and `plan.md` yourself by reducing the agent outputs.

### `spec.md` must include

- the problem in plain language
- the why behind the work
- the actual root cause / missing capability
- the chosen solution
- rejected shortcut solutions and why they are not acceptable
- acceptance criteria
- non-goals
- rollout / rollback notes if relevant

### `plan.md` must include

Keep the plan coarse. Aim for **3–6 tasks**, not a task explosion.

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

The plan must align to `why.md`, `diagnosis.md`, `solution-decision.md`, `harness-profile.md`, `flow-spec.md`, and `memory-recall.md`.

### `workboard.md` must include

- stage status for recall / plan / implement / verify / review / compound
- one row per planned task with status, owner, scenario IDs, checks, and notes
- current next action
- blockers / escalations

### `proof-map.md` must include

- every required F2P scenario
- every relevant P2P regression guard
- the planned proof type for each item
- the exact command / artifact / log expected when verification runs
- initial status set to `UNASSESSED`

### `scorecard.md` must include

- every required F2P scenario
- every relevant P2P regression guard
- the exact check or evidence source for each item
- initial status set to `UNASSESSED`

## Plan gate before implementation

Do **not** continue to implementation until all are true:

- `memory-recall.md` exists and is specific
- `why.md` exists and explains the real value of the work
- `diagnosis.md` exists and identifies the real problem or capability gap
- `solution-decision.md` exists and records rejected shortcuts
- `harness-profile.md` exists and is justified
- `flow-spec.md` is concrete enough to test from
- `test-contract.md` maps scenarios to explicit checks
- `env-plan.md` explains how local verification will avoid server / harness traps
- `workboard.md` reflects the chosen tasks and current next action
- `proof-map.md` names the proof expected for each required scenario
- `plan.md` has bounded tasks with file scope and targeted checks
- at least one disconfirming probe exists in `solution-decision.md` or `plan.md`

## Completion

Print:

- `RUN_ID`
- the run folder path
- the selected harness profile
- the recommended verify mode
- any blocking user questions (if truly blocking)
- a one-paragraph planning summary
