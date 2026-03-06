---
name: xlfg:compound
description: Convert an xlfg run into durable knowledge, role memory, and the next-agent handoff.
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

## 2) Read run artifacts

Read (if present):

- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `env-plan.md`
- `risk.md`
- `verification.md`
- `scorecard.md`
- `verify-fix-plan.md`
- `review-summary.md`
- `run-summary.md`
- `docs/xlfg/knowledge/current-state.md`

## 3) Extract only reusable, verified lessons

Append small, specific entries to the right knowledge files, and append structured durable events to `ledger.jsonl`:

Shared memory:
- `current-state.md` — short tracked handoff for the next agent
- `patterns.md` — durable implementation or design patterns
- `decision-log.md` — durable decisions and rejected shortcuts worth remembering
- `testing.md` — scenario-level testing lessons
- `ux-flows.md` — durable UX / keyboard / failure-path expectations
- `failure-memory.md` — repeated unexpected failures and proven fixes
- `harness-rules.md` — dev-server, watch-mode, port, readiness, cleanup rules
- `quality-bar.md` — missing gate discovered by this run

Role memory (only when role-specific and compact):
- `agent-memory/root-cause-analyst.md`
- `agent-memory/solution-architect.md`
- `agent-memory/test-strategist.md`
- `agent-memory/env-doctor.md`
- `agent-memory/test-implementer.md`
- `agent-memory/task-implementer.md`
- `agent-memory/task-checker.md`
- `agent-memory/verify-reducer.md`
- `agent-memory/ux-reviewer.md`
- `agent-memory/architecture-reviewer.md`
- `agent-memory/security-reviewer.md`
- `agent-memory/performance-reviewer.md`

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

- tied to a concrete symptom, decision, or contract gap
- backed by verification, review, or a repeated real failure
- likely to help the next run directly
- small enough that the role can retrieve them without prompt bloat

Prefer shared memory unless the lesson is clearly role-specific.

## 4) Refresh `current-state.md`

Update `docs/xlfg/knowledge/current-state.md` so the next agent has one tracked document to read first.

Keep it short and current. It should contain only the highest-signal truths that remain useful after this run, such as:

- the current service / product context if it materially changed
- the most important UX / behavior contracts now in force
- the harness / verification rules that should shape the next run immediately
- repeated failure signatures and the proven first response
- open risks / debts worth carrying forward
- one or two strong starting recall queries

Do not paste the whole run into `current-state.md`.

## 5) Write run-level compounding summary

Write `DOCS_RUN_DIR/compound-summary.md` with:

- what was learned
- what was added to each knowledge file
- what was appended to `ledger.jsonl`
- what was added to role memory and why
- how `current-state.md` changed
- what shortcuts were rejected and why
- what was intentionally not added and why
- what the next similar run should do first

## 6) Completion

Print:

- what knowledge was added
- where it was written
- path to `current-state.md`
- path to `compound-summary.md`
