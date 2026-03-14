---
name: xlfg-quality-gates
description: Apply production readiness gates (why, diagnosis, proof, UX, security, ops) before shipping /xlfg work.
---

# xlfg-quality-gates

Use these gates to make `/xlfg` output actually production-ready.

## Definition of done

A run is only “done” when all apply.

### Why, diagnosis, and scope

- `memory-recall.md` exists and captures the strongest prior relevant lessons or an explicit no-hit
- `why.md` exists and makes false success explicit
- `diagnosis.md` exists and identifies the real problem or capability gap
- `solution-decision.md` exists and records rejected shortcuts
- `harness-profile.md` exists and is appropriate for the risk
- `flow-spec.md` exists and matches shipped behavior
- `test-contract.md` exists and the run followed it honestly
- `env-plan.md` explains how the harness was controlled
- `workboard.md` reflects the current stage / task truth
- `proof-map.md` names the exact evidence required for each important scenario
- non-goals are explicit
- no unapproved scope creep

### Implementation quality

- every task has a `task-brief.md`
- every task has `test-report.md`, `implementer-report.md`, and `checker-report.md`
- every task has `Verdict: ACCEPT`
- no task is accepted via symptom-hiding patch unless explicitly documented as a bounded workaround
- the implementation still serves `why.md`

### Tests, proof, and verification

- new behavior has F2P proof
- existing behavior has P2P protection
- at least one real interaction / integration check exists when the flow crosses boundaries
- lint / typecheck / build pass when applicable
- evidence is written to `verification.md`
- raw logs exist under `.xlfg/`
- `scorecard.md` reflects the required scenario status
- `proof-map.md` has no unresolved required proof gap
- verification proves actual environment state when required (not just that a command was invoked)
- green commands do not overrule missing proof

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
- repeated harness failures are compounded into `failure-memory.md`, `harness-rules.md`, or the relevant role memory file
- `docs/xlfg/knowledge/current-state.md` is refreshed when the run changes what the next agent should know first

## Sanity check before calling a task or run “done”

Ask:

1. Why does this work matter to the user or operator?
2. What really fires when the flow runs?
3. Do tests exercise the real chain or only mocks?
4. Can failure leave stale or orphaned state?
5. What other interfaces expose the same behavior?
6. Can the harness produce a fake green result?
7. Did we fix the real problem or only hide the symptom?
8. Did the proof map honestly prove the requirement?
