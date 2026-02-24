---
name: xlfg-quality-gates
description: Apply production readiness gates (tests, UX, security, ops). Use before shipping /xlfg work.
---

# xlfg-quality-gates

Use these gates to make `/xlfg` output **indisputably production-ready**.

## Definition of done

A run is only “done” when all apply:

### Spec & scope

- `spec.md` exists and matches shipped behavior
- Acceptance criteria are testable and satisfied
- Non-goals are explicit
- No unapproved scope creep
- Context expansion outputs were triaged before implementation
- Any unapproved expansions were deferred to backlog

### Tests & verification

- New behavior has tests (Fail→Pass)
- Regression suite passes (Pass→Pass)
- At least one integration-style test exists for cross-layer behavior
- Lint/typecheck/build pass when applicable
- Evidence is written to `verification.md` and raw logs exist under `.xlfg/`
- Every plan task has:
  - `tasks/<task-id>/implementer-report.md`
  - `tasks/<task-id>/checker-report.md` with `Verdict: ACCEPT`
- Review findings focus on net-new issues not already covered by verification

### UX

- Happy path is obvious
- Failure path is humane and actionable
- Empty/loading states are reasonable
- Accessibility is checked (keyboard flow, labels) when UI is involved
- Screenshots exist for UI changes (store in `.xlfg/runs/<run-id>/screenshots/`)

### Security & privacy

- No secrets in code or logs
- Input validation at boundaries
- Authn/authz checked for user-facing endpoints
- Sensitive data not logged

### Operations

- Monitoring/validation plan exists (what to watch, for how long, rollback triggers)
- Rollback plan exists for risky changes (migrations, data transforms)

## System-wide test sanity check (run before calling a task “done”)

Ask:

1. **What fires when this runs?** callbacks, middleware, event handlers (trace 2 levels)
2. **Do tests exercise the real chain?** avoid 100% mocks for integration boundaries
3. **Can failure leave orphaned state?** verify idempotency/cleanup on retries
4. **What other interfaces expose this?** duplicate entrypoints need parity
5. **Do error strategies align across layers?** retries + fallbacks + framework handlers

## Evidence capture

- Prefer `tee` logs into `.xlfg/`.
- Record exit codes.
- Summarize first actionable failure (avoid cascades).

## Risk gates

Require explicit user confirmation for:

- DB migrations / backfills
- Auth / permissions changes
- Payment / billing logic
- Destructive actions (delete, purge, irreversible transforms)
- Security-sensitive areas (tokens, crypto, secrets)

## Final pre-ship checklist

- [ ] `plan.md` checkboxes complete
- [ ] Every plan task has implementer + checker reports with `ACCEPT` verdict
- [ ] `/xlfg:verify` green
- [ ] `/xlfg:review` has no P0 findings
- [ ] `run-summary.md` exists with smoke steps
- [ ] `/xlfg:compound` executed and `compound-summary.md` exists
