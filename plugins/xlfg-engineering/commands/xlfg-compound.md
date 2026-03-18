---
name: xlfg:compound
description: Convert an xlfg run into durable knowledge, role memory, and a next-agent handoff that captures request understanding, why, proof, and harness lessons.
argument-hint: "[run-id | latest]"
---

# /xlfg:compound

Turn a completed run into durable knowledge that improves future runs.

<input>#$ARGUMENTS</input>

## 1) Select run

- If `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat argument as run id

Paths:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `KB_DIR=docs/xlfg/knowledge`
- `AGENT_MEMORY_DIR=docs/xlfg/knowledge/agent-memory`
- `LEDGER=docs/xlfg/knowledge/ledger.jsonl`

Ensure all knowledge paths exist.

## 1.5) Apply the merge-friendly knowledge rule

Before writing tracked knowledge, detect the current branch:

- `git rev-parse --abbrev-ref HEAD`
- treat `main`, `master`, and `trunk` as default branches unless the repo clearly uses a different default

Write policy:

- shared tracked knowledge files are **append-only**
- do **not** rewrite old entries in shared knowledge files; add a new dated entry that supersedes older advice when needed
- `current-state.md` is the stable repo-wide brief, not a hot file for every feature branch
- on a non-default branch or worktree, write `DOCS_RUN_DIR/current-state-candidate.md` instead of editing `docs/xlfg/knowledge/current-state.md`, unless the user explicitly asked to promote repo-wide shared knowledge now

This keeps merge behavior simple while preserving branch-local handoff.

## 2) Read run artifacts

Read (if present):

- `query-contract.md`
- `memory-recall.md`
- `why.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `test-readiness.md`
- `env-plan.md`
- `workboard.md`
- `proof-map.md`
- `risk.md`
- `verification.md`
- `scorecard.md`
- `verify-fix-plan.md`
- `review-summary.md`
- `run-summary.md`
- `current-state-candidate.md` (if already present for this branch/worktree)
- `docs/xlfg/knowledge/current-state.md`

## 3) Extract only reusable, verified lessons

Append small, specific entries to the right knowledge files, and append structured durable events to `ledger.jsonl`.

Append at the end of the file. Do not rewrite or reflow old shared entries during this step.

Shared memory:
- `current-state.md` — short tracked handoff for the next agent
- `patterns.md` — durable implementation or design patterns
- `decision-log.md` — durable decisions and rejected shortcuts worth remembering
- `testing.md` — scenario-level testing lessons and anti-monkey probes
- `ux-flows.md` — durable UX / keyboard / failure-path expectations
- `failure-memory.md` — repeated unexpected failures and proven fixes
- `harness-rules.md` — dev-server, watch-mode, port, readiness, cleanup rules
- `quality-bar.md` — missing gate discovered by this run

Role memory (only when role-specific and compact):
- `agent-memory/query-refiner.md`
- `agent-memory/why-analyst.md`
- `agent-memory/root-cause-analyst.md`
- `agent-memory/harness-profiler.md`
- `agent-memory/solution-architect.md`
- `agent-memory/test-strategist.md`
- `agent-memory/test-readiness-checker.md`
- `agent-memory/env-doctor.md`
- `agent-memory/test-implementer.md`
- `agent-memory/task-implementer.md`
- `agent-memory/task-checker.md`
- `agent-memory/verify-reducer.md`
- `agent-memory/ux-reviewer.md`
- `agent-memory/architecture-reviewer.md`
- `agent-memory/security-reviewer.md`
- `agent-memory/performance-reviewer.md`

### What to prefer

Prefer lessons that answer one of these:

- how this class of request should be interpreted before coding starts
- which implied asks were easy to drop and how to keep them visible
- why this class of request matters and what false success looks like
- which harness profile was actually honest for this problem shape
- which UX flow or proof obligation repeatedly matters
- which harness failure signature should be detected first next time
- which shortcut should be rejected immediately next time

### Ledger event rule

For each lesson that survives the admission gate, append **one JSON object per line** to `ledger.jsonl`.
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

Do not rewrite old ledger lines in place. If a memory is superseded, append a new event explaining that.

### Admission rule

Do **not** compound vague summaries.

Only write entries that are:

- tied to a concrete symptom, decision, proof gap, contract gap, or request-understanding lesson
- backed by verification, review, or a repeated real failure
- likely to help the next run directly
- small enough that the role can retrieve them without prompt bloat

Prefer shared memory unless the lesson is clearly role-specific.

## 4) Refresh the right handoff file

If the current branch is the default branch (`main`, `master`, or `trunk`) **or** the user explicitly asked to promote a repo-wide handoff now:

- update `docs/xlfg/knowledge/current-state.md`

Otherwise:

- leave `docs/xlfg/knowledge/current-state.md` untouched
- write `DOCS_RUN_DIR/current-state-candidate.md` for this branch/worktree instead

The handoff content should stay short and current. Include only the highest-signal truths that remain useful after this run, such as:

- the current service / product context if it materially changed
- the most important request-shaping / quality-bar truths now in force
- the most important UX / behavior contracts now in force
- the harness profile rules that should shape the next similar run immediately
- repeated failure signatures and the proven first response
- open risks / debts worth carrying forward
- one or two strong starting recall queries

Do not paste the whole run into the handoff file.

## 5) Write run-level compounding summary

Write `DOCS_RUN_DIR/compound-summary.md` with:

- what was learned
- what was added to each knowledge file
- what was appended to `ledger.jsonl`
- what was added to role memory and why
- whether the pre-implementation test contract proved strong enough in practice
- whether `current-state.md` changed or a `current-state-candidate.md` was written instead
- how the query contract, why, proof, and harness profile shaped the final lessons
- what shortcuts were rejected and why
- what was intentionally not added and why
- what the next similar run should do first

## 6) Update the workboard

Mark in `workboard.md`:
- `compound: DONE`
- current next action: `none` or the real follow-up debt

## 7) Completion

Print:

- what knowledge was added
- where it was written
- path to the handoff file (`current-state.md` or `current-state-candidate.md`)
- path to `compound-summary.md`
