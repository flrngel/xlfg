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

## 2) Read run artifacts

Read (if present):
- `spec.md`
- `plan.md`
- `risk.md`
- `verification.md`
- `review-summary.md`
- PR or issue references

## 3) Extract compounding artifacts

Append or add entries to:

- `KB_DIR/patterns.md`
  - new patterns discovered
  - pitfalls to avoid
- `KB_DIR/decision-log.md`
  - durable architectural/product decisions
- `KB_DIR/quality-bar.md`
  - update checklists if a missing gate caused pain

Keep additions small, specific, and reusable.

## 4) Write a run summary (if missing)

Ensure `DOCS_RUN_DIR/run-summary.md` exists with:

- What changed (high level)
- How to verify manually (smoke steps)
- Commands run (link to `.xlfg/` logs)
- Known risks / follow-ups

## 5) Completion

Print:
- What knowledge was added
- Where it was written
