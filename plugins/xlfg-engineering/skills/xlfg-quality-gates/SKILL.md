---
name: xlfg-quality-gates
description: Apply production readiness gates (contracts, verification, UX, security, ops) before shipping /xlfg work.
---

# xlfg-quality-gates

Use these gates to make `/xlfg` output actually production-ready.

## Definition of done

A run is only “done” when all apply.

### Contract & scope

- `flow-spec.md` exists and matches shipped behavior
- `test-contract.md` exists and the run followed it honestly
- `env-plan.md` explains how the harness was controlled
- non-goals are explicit
- no unapproved scope creep

### Tests & verification

- new behavior has F2P proof
- existing behavior has P2P protection
- at least one real interaction / integration check exists when the flow crosses boundaries
- lint / typecheck / build pass when applicable
- evidence is written to `verification.md`
- raw logs exist under `.xlfg/`
- `scorecard.md` reflects the required scenario status
- every plan task has implementer + checker reports with `Verdict: ACCEPT`

### UX

- happy path is obvious
- alternate interaction paths are checked when relevant
- failure path is humane and actionable
- empty / loading states are reasonable
- keyboard / accessibility is checked for UI work

### Security & privacy

- no secrets in code or logs
- input validation at boundaries
- authn / authz checked for user-facing or privileged flows
- sensitive data not logged

### Operations

- monitoring / validation plan exists
- rollback plan exists for risky changes
- repeated harness failures are compounded into `failure-memory.md` or `harness-rules.md`

## Sanity check before calling a task “done”

Ask:

1. What really fires when the flow runs?
2. Do tests exercise the real chain or only mocks?
3. Can failure leave stale or orphaned state?
4. What other interfaces expose the same behavior?
5. Can the harness produce a fake green result?

## Evidence capture

- prefer captured logs
- record exit codes
- summarize the first actionable failure
- do not bury environment problems under code churn

## Final pre-ship checklist

- [ ] contracts written first
- [ ] plan complete
- [ ] every task has ACCEPTed checker report
- [ ] verification green
- [ ] review has no P0 findings
- [ ] scorecard green for required scenarios
- [ ] run summary exists
- [ ] compound summary exists
