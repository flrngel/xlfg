---
name: xlfg:review
description: Run risk-shaped review as confirmation, not ceremony, and keep the review fan-out proportional to the task.
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

## 2) Read the shortest useful brief

Always read these first:

- `spec.md`
- `verification.md`
- `proof-map.md`
- `workboard.md`
- `harness-profile.md`

Read these only if a chosen lens needs them:

- `query-contract.md`
- `why.md`
- `solution-decision.md`
- `test-contract.md`
- `flow-spec.md`
- `run-summary.md`
- `docs/xlfg/knowledge/current-state.md`

Mark `review: IN_PROGRESS` in `workboard.md`.

## 3) Review doctrine

Review is a confirmation gate, not where quality is manufactured.

Pick review lenses based on risk and changed surface:

- `xlfg-security-reviewer` — auth, secrets, permissions, network boundaries, data exposure
- `xlfg-performance-reviewer` — latency, large data, render loops, N+1, hot paths
- `xlfg-ux-reviewer` — user-facing flows, messaging, accessibility, interaction states
- `xlfg-architecture-reviewer` — public interfaces, broad coupling, boundary changes, maintainability risk

### Default review budget

- `quick`: 0–1 lens
- `standard`: 1–2 lenses
- `deep`: as required, up to 4 lenses

Do **not** run every reviewer by default.

## 4) Review summary

Create `review-summary.md` with:

- which lenses ran and why
- which lenses were skipped and why
- findings already covered by verification
- net-new findings
- query / why / root-solution drift
- proof-map honesty issues
- scenario-contract quality issues
- PM / Engineering / QA / Release notes

## 5) Gate rule

Only pass review when:

- verification is green
- required lenses for the profile were satisfied or credibly skipped
- no net-new P0 issue remains
- `proof-map.md` does not overclaim
- no serious drift from `spec.md` remains

If review finds a real ship blocker, fix it, re-run verify, then re-run review.

## 6) Finish review

If review passes:

- update `workboard.md` to `review: DONE`
- set `compound: NEXT`
- record the current next action
