---
name: xlfg:compound
description: Convert an xlfg run into immutable durable knowledge, role memory, and rebuilt local read models.
argument-hint: "[run-id | latest]"
---

# /xlfg:compound

Turn a completed run into durable knowledge that improves future runs **without forcing branches to edit the same shared rollup files**.

<input>#$ARGUMENTS</input>

## 1) Select run

- if `latest` or empty: newest folder under `docs/xlfg/runs/`
- otherwise: treat argument as run id

Paths:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `KB_ROOT=docs/xlfg/knowledge`
- `KB_CARDS=docs/xlfg/knowledge/cards`
- `KB_EVENTS=docs/xlfg/knowledge/events`
- `KB_VIEWS=docs/xlfg/knowledge/_views`
- `AGENT_MEMORY=docs/xlfg/knowledge/agent-memory`
- `WORKTREE_CTX=.xlfg/worktree.json`

Ensure the scaffold exists. If `WORKTREE_CTX` is missing, regenerate or infer the current git/worktree context before writing durable memory.

## 2) Read run artifacts and knowledge context

Read from the run if present:

- `memory-recall.md`
- `why.md`
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
- `risk.md`
- `verification.md`
- `scorecard.md`
- `verify-fix-plan.md`
- `review-summary.md`
- `run-summary.md`

Also read if present:

- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/failure-memory.md`
- `docs/xlfg/knowledge/_views/harness-rules.md`
- `docs/xlfg/knowledge/_views/worktree.md`
- relevant role-memory views under `docs/xlfg/knowledge/_views/agent-memory/`

## 3) Choose the write namespace

Use the current git/worktree context to choose the namespace:

- `branch-slug`
- `worktree name`
- `default branch`
- `knowledge write namespace`

Every durable lesson written by this run must go into a **new immutable file** under the active branch slug. Do not edit an existing card unless you are intentionally repairing a mistaken file from the same branch and run.

## 4) Admission rule

Do **not** compound vague summaries.

Only admit lessons that are:

- tied to a concrete symptom, decision, proof gap, or contract gap
- backed by verification, review, or a repeated real failure
- likely to help the next run directly
- small enough that the role can retrieve them without prompt bloat

Prefer shared memory unless the lesson is clearly role-specific.

## 5) Write immutable shared cards

For each admitted shared lesson, write one markdown card under the matching kind:

- `cards/current-state/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `cards/patterns/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `cards/decision-log/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `cards/testing/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `cards/ux-flows/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `cards/failure-memory/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `cards/harness-rules/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `cards/quality-bar/<branch-slug>/<timestamp>--<run-id>--<slug>.md`

Card guidance:

- one lesson per card
- include a clear heading
- include the run id
- include the concrete symptom / rule / proof / rejection
- keep it small and specific

## 6) Write immutable role-memory cards

Only when a lesson is clearly specialist-specific, write one markdown card under:

- `agent-memory/<role>/cards/<branch-slug>/<timestamp>--<run-id>--<slug>.md`

Roles that may receive cards:

- `why-analyst`
- `root-cause-analyst`
- `harness-profiler`
- `solution-architect`
- `test-strategist`
- `env-doctor`
- `test-implementer`
- `task-implementer`
- `task-checker`
- `verify-reducer`
- `ux-reviewer`
- `architecture-reviewer`
- `security-reviewer`
- `performance-reviewer`

## 7) Write immutable event files

For each admitted lesson, also write one structured event JSON file under:

- `events/<branch-slug>/<timestamp>--<run-id>--<slug>.json`

Prefer `event: "memory.added"`.

Required fields:
- `id`
- `event`
- `created_at`
- `run_id`
- `kind`
- `stage`
- `title`
- `summary`
- `lex`
- `evidence`

Optional but recommended:
- `role`
- `symptom`
- `root_cause`
- `action`
- `prevention`
- `tags`
- `status`

Do not rewrite old events in place. If a memory is superseded, write a new event that says so.

## 8) Rebuild local views

After cards/events are written, rebuild the local read models.

Preferred path if the helper CLI is available:

```bash
xlfg knowledge rebuild
```

If the helper CLI is not available, regenerate the `_views/` files with the same rules:

- `current-state.md` is a concise local handoff synthesized from service-context plus the highest-priority cards
- `<kind>.md` views roll up tracked cards
- `agent-memory/<role>.md` views roll up tracked role cards
- `ledger.jsonl` is generated from immutable event files
- `worktree.md` reflects the active git/worktree context

Never hand-edit the generated `_views/` files as the durable source of truth.

## 9) Write run-level compounding summary

Write `DOCS_RUN_DIR/compound-summary.md` with:

- what was learned
- which cards were written
- which event files were written
- which role-memory cards were written and why
- whether views were rebuilt
- how the worktree namespace shaped the writes
- what shortcuts were rejected and why
- what was intentionally not added and why
- what the next similar run should do first

## 10) Update the workboard

Mark in `workboard.md`:
- `compound: DONE`
- current next action: `none` or the real follow-up debt

## 11) Completion

Print:

- what knowledge was added
- which tracked card/event paths were written
- whether local views were rebuilt
- path to `docs/xlfg/knowledge/_views/current-state.md`
- path to `DOCS_RUN_DIR/compound-summary.md`
