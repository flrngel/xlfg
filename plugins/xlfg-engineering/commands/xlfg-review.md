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

First, classify review scope from touched files + `risk.md`:

- Always run:
  - Task `xlfg-security-reviewer` → `DOCS_RUN_DIR/reviews/security.md`
  - Task `xlfg-architecture-reviewer` → `DOCS_RUN_DIR/reviews/architecture.md`
- Run `xlfg-performance-reviewer` only if:
  - backend/hot-path/db/query/index/concurrency areas changed, or
  - `risk.md` flags performance risk
- Run `xlfg-ux-reviewer` only if:
  - user-facing UI/copy/a11y flow changed, or
  - `risk.md` flags UX risk

Each agent must:

- Read `DOCS_RUN_DIR/spec.md`, `DOCS_RUN_DIR/plan.md`, and `DOCS_RUN_DIR/verification.md` if present
- Read `DOCS_RUN_DIR/verify-fix-plan.md` if present
- Review the git diff / touched files
- Explicitly separate:
  - findings already covered by verification
  - net-new review findings
- Output net-new findings with severity: P0 (blocker), P1 (important), P2 (nice)
- For each net-new finding, explain why verification did not catch it
- Include concrete fixes and file/line pointers where possible

## 3) Reduce phase: synthesize and gate

Create `DOCS_RUN_DIR/review-summary.md`:

- Record which reviewers ran vs were skipped and why
- Merge duplicates by `(file, line/area, issue class)`
- Keep one canonical finding and merge source references
- Keep a short section: `Already covered by verification`
- Keep a short section: `Net-new findings`
- Call out net-new P0 blockers first
- For net-new P0/P1: create a fix checklist

If any net-new P0 issues exist:

- Do not ship
- Fix them
- Re-run `/xlfg:verify`
- Re-run `/xlfg:review`

Only ship when P0 is empty and verification is green.
