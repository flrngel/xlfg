---
name: xlfg:review
description: Parallel multi-lens review into docs/xlfg run files.
argument-hint: "[run-id | latest]"
---

# /xlfg:review

Run a parallel, multi-lens review and store results in the run folder.

<input>#$ARGUMENTS</input>

## 1) Select run

- If `latest` or empty: newest folder under `docs/xlfg/runs/`.
- Otherwise: treat argument as run-id.

Set:
- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`

Ensure `DOCS_RUN_DIR/reviews/` exists.

## 2) Map phase: independent review agents

Launch these in parallel with Task tool (each agent writes to a file and does NOT coordinate via chat):

- Task `xlfg-security-reviewer` → `DOCS_RUN_DIR/reviews/security.md`
- Task `xlfg-performance-reviewer` → `DOCS_RUN_DIR/reviews/performance.md`
- Task `xlfg-ux-reviewer` → `DOCS_RUN_DIR/reviews/ux.md`
- Task `xlfg-architecture-reviewer` → `DOCS_RUN_DIR/reviews/architecture.md`

Each agent must:

- Read `DOCS_RUN_DIR/spec.md` and `DOCS_RUN_DIR/plan.md` if present
- Review the git diff / touched files
- Output findings with severity: P0 (blocker), P1 (important), P2 (nice)
- Include concrete fixes and file/line pointers where possible

## 3) Reduce phase: synthesize and gate

Create `DOCS_RUN_DIR/review-summary.md`:

- Merge duplicates
- Call out P0 blockers first
- For P0/P1: create a fix checklist

If any P0 issues exist:

- Do not ship
- Fix them
- Re-run `/xlfg:verify`
- Re-run `/xlfg:review`

Only ship when P0 is empty and verification is green.
