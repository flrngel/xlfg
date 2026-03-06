---
name: xlfg:compound
description: Convert an xlfg run into durable knowledge (tests, failures, harness rules, patterns, and role-specific memory).
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

## 3) Extract only reusable, verified lessons

Append small, specific entries to the right knowledge files, and append structured durable events to `ledger.jsonl`:

Shared memory:
- `patterns.md` — durable implementation or design patterns
- `decision-log.md` — durable decisions and rejected shortcuts worth remembering
- `testing.md` — scenario-level testing lessons
- `ux-flows.md` — durable UX / keyboard / failure-path expectations
- `failure-memory.md` — repeated unexpected failures and proven fixes
- `harness-rules.md` — dev-server, watch-mode, port, readiness, cleanup rules
- `quality-bar.md` — missing gate discovered by this run

Role memory (only when role-specific and compact):
- `agent-memory/root-cause-analyst.md`
- `agent-memory/test-strategist.md`
- `agent-memory/env-doctor.md`
- `agent-memory/task-implementer.md`
- `agent-memory/verify-reducer.md`
- `agent-memory/ux-reviewer.md`

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

## 4) Write run-level compounding summary

Write `DOCS_RUN_DIR/compound-summary.md` with:

- what was learned
- what was added to each knowledge file
- what was appended to `ledger.jsonl`
- what was added to role memory and why
- what shortcuts were rejected and why
- what was intentionally not added and why
- what the next similar run should do first

## 5) Completion

Print:

- what knowledge was added
- where it was written
- path to `compound-summary.md`
