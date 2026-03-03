---
name: xlfg:compound
description: Convert an xlfg run into durable knowledge (tests, failures, harness rules, patterns, and root-solution learnings).
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

Ensure `KB_DIR` exists.

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

Append small, specific entries to the right knowledge files:

- `patterns.md` — durable implementation or design patterns
- `decision-log.md` — durable decisions and rejected shortcuts worth remembering
- `testing.md` — scenario-level testing lessons
- `ux-flows.md` — durable UX / keyboard / failure-path expectations
- `failure-memory.md` — repeated unexpected failures and proven fixes
- `harness-rules.md` — dev-server, watch-mode, port, readiness, cleanup rules
- `quality-bar.md` — missing gate discovered by this run

### Admission rule

Do **not** compound vague summaries.

Only write entries that are:

- tied to a concrete symptom, decision, or contract gap
- backed by verification, review, or a repeated real failure
- likely to help the next run directly

## 4) Write run-level compounding summary

Write `DOCS_RUN_DIR/compound-summary.md` with:

- what was learned
- what was added to each knowledge file
- what shortcuts were rejected and why
- what was intentionally not added and why
- what the next similar run should do first

## 5) Completion

Print:

- what knowledge was added
- where it was written
- path to `compound-summary.md`
