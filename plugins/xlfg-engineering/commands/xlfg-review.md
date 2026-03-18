---
name: xlfg:review
description: Run profile-aware multi-lens review as confirmation against the request contract, why, proof, and the chosen root solution.
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

Before running reviewers:
- read `query-contract.md`
- read `harness-profile.md`
- extract the required review lenses
- mark `review: IN_PROGRESS` in `workboard.md`
- note that the carry-forward anchor was re-read

## 3) Map phase: independent review agents

Always read first (if present):

- `query-contract.md`
- `memory-recall.md`
- `why.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `proof-map.md`
- `verification.md`
- `scorecard.md`
- `verify-fix-plan.md`
- `workboard.md`
- `docs/xlfg/knowledge/current-state.md`

Run these review agents based on the required lenses in `harness-profile.md` and actual changed surface:

- `xlfg-security-reviewer` → `reviews/security.md`
- `xlfg-architecture-reviewer` → `reviews/architecture.md`
- `xlfg-performance-reviewer` → `reviews/performance.md`
- `xlfg-ux-reviewer` → `reviews/ux.md`

Each reviewer must explicitly separate:

- findings already covered by verification
- net-new review findings
- any evidence that the implementation drifted from `query-contract.md`
- any evidence that the implementation drifted from `why.md`
- any evidence that the implementation drifted from the chosen root solution
- any evidence that a recall-derived warning was ignored
- any evidence that the proof map still overclaims what was proven

Do **not** run every possible reviewer by default if the harness profile does not justify it.

## 4) Reduce phase: synthesize and gate

Create `DOCS_RUN_DIR/review-summary.md`:

- record which reviewers ran vs were skipped and why
- record the active harness profile and required lenses
- merge duplicates
- keep one section for `Already covered by verification`
- keep one section for `Net-new findings`
- keep one section for `Query / why / root-solution drift`
- keep one section for `Proof-map honesty`
- call out P0 blockers first
- list any uncovered direct asks or non-negotiable implied asks

## 5) Gate rule

Only pass review when all are true:

- verification is green
- required review lenses from `harness-profile.md` were satisfied or explicitly skipped with a credible reason
- no net-new P0 issues remain
- no proof-map overclaim remains
- no uncovered direct asks remain
- no serious drift from `query-contract.md`, `why.md`, or `solution-decision.md` remains

If any net-new P0 issues exist:

- do not ship
- fix them
- re-run verification
- re-run review

If review reveals a shallow workaround posing as the final solution, return to planning or implementation instead of papering it over in the review summary.

## 6) Finish review phase

If review passes:
- update `workboard.md` to `review: DONE`
- set `compound: NEXT`
- record the current next action
