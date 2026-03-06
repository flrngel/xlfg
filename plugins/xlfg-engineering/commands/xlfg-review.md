---
name: xlfg:review
description: Parallel multi-lens review using the shared diagnosis, recall, flow, test, and environment contract.
argument-hint: "[run-id | latest]"
---

# /xlfg:review

Run a multi-lens review and store results in the run folder.

<input>#$ARGUMENTS</input>

## 1) Select run

- If `latest` or empty: newest folder under `docs/xlfg/runs/`
- Otherwise: treat argument as run id

Set:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`

Ensure `DOCS_RUN_DIR/reviews/` exists.

## 2) Review doctrine

Review is a confirmation gate, not the main place where quality is created.
Reviewers should verify that recall, planning, and implementation already controlled risk.

## 3) Map phase: independent review agents

Always read first (if present):

- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `verification.md`
- `scorecard.md`
- `verify-fix-plan.md`
- `docs/xlfg/knowledge/current-state.md`

Run these review agents in parallel as relevant:

- `xlfg-security-reviewer` → `reviews/security.md`
- `xlfg-architecture-reviewer` → `reviews/architecture.md`
- `xlfg-performance-reviewer` → `reviews/performance.md` (if perf-sensitive area changed)
- `xlfg-ux-reviewer` → `reviews/ux.md` (if user-facing flow changed)

Each reviewer must explicitly separate:

- findings already covered by verification
- net-new review findings
- any evidence that the implementation drifted from the chosen root solution
- any evidence that a recall-derived warning was ignored

## 4) Reduce phase: synthesize and gate

Create `DOCS_RUN_DIR/review-summary.md`:

- record which reviewers ran vs were skipped and why
- merge duplicates
- keep one section for `Already covered by verification`
- keep one section for `Net-new findings`
- call out P0 blockers first

If any net-new P0 issues exist:

- do not ship
- fix them
- re-run verification
- re-run review

Only ship when P0 is empty and the verification scorecard is green.
