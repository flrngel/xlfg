---
name: xlfg:compound
description: Convert an xlfg run into durable knowledge (patterns/decisions).
argument-hint: "[run-id | latest]"
---

# /xlfg:compound

Turn a completed run into durable knowledge that improves future runs.

<input>#$ARGUMENTS</input>

## 1) Select run

- If `latest` or empty: newest folder under `docs/xlfg/runs/`.
- Otherwise: treat argument as run-id.

Paths:
- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `KB_DIR=docs/xlfg/knowledge`

Ensure `KB_DIR` exists. Create missing knowledge files as needed before appending.

## 2) Read run artifacts

Read (if present):
- `spec.md`
- `plan.md`
- `test-plan.md`
- `risk.md`
- `verification.md`
- `verify-fix-plan.md`
- `review-summary.md`
- PR or issue references

## 3) Extract compounding artifacts

Append or add entries to:

- `KB_DIR/patterns.md`
  - new patterns discovered
  - pitfalls to avoid
- `KB_DIR/decision-log.md`
  - durable architectural/product decisions
- `KB_DIR/testing.md`
  - escaped defects and missed assertions
  - reusable test patterns that prevented regressions
  - flaky signatures and stabilization tactics
  - command reliability/cost notes (fast vs full loop)
- `KB_DIR/quality-bar.md`
  - update checklists if a missing gate caused pain

Keep additions small, specific, and reusable.

## 4) Write run-level compounding summary

Write `DOCS_RUN_DIR/compound-summary.md` with:

- What was learned from verify + review overlap
- What changed in each knowledge file
- What testing knowledge was added/reused
- Any deliberate "no-op" sections where no new lessons were found

## 5) Write a run summary (if missing)

Ensure `DOCS_RUN_DIR/run-summary.md` exists with:

- What changed (high level)
- How to verify manually (smoke steps)
- Commands run (link to `.xlfg/` logs)
- Known risks / follow-ups

## 6) Completion

Print:
- What knowledge was added
- Where it was written
- Path to `DOCS_RUN_DIR/compound-summary.md`
