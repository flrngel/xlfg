---
description: Apply production-readiness gates to an xlfg run without recreating duplicated planning state.
user-invocable: false
---

# xlfg-quality-gates

Use these gates to keep an xlfg run production-ready.

## Definition of done

A run is only done when all relevant gates apply.

### Run-card quality

- `memory-recall.md` exists and captures strong prior lessons or an explicit no-hit
- `spec.md` is the single source of truth for request truth, why, harness choice, solution, task map, and proof summary
- `spec.md` makes false success explicit
- optional docs exist only when they changed a decision (`research.md`, `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, `risk.md`)
- `test-contract.md` exists, stays concise, and the run followed it honestly
- `test-readiness.md` was `READY` before implementation or the run explicitly returned to planning
- `workboard.md` reflects stage and task truth
- no unapproved scope creep

### Implementation quality

- changed tasks have bounded scope and targeted checks
- no task is accepted via a symptom-hiding patch unless explicitly documented as a bounded workaround
- the implementation still serves the user outcome captured in `spec.md`

### Tests, proof, and verification

- new behavior has F2P proof from scenario-targeted checks declared before coding
- existing behavior has P2P protection when relevant
- verification ran at least one scenario-targeted proof when changed scenarios existed
- evidence is written to `verification.md`
- green commands do not overrule missing proof
- uncovered direct asks or non-negotiable implied asks keep the run RED

### Review and release

- review fan-out stayed proportional to the risk
- no net-new P0 issue remains after review
- rollback or follow-up notes exist for risky changes
- durable lessons were compounded only when verified and reusable

## Sanity check before calling a run done

Ask:

1. Does `spec.md` still describe the shipped change?
2. Did we prove the real behavior, not just a nearby static check?
3. Did we fix the root cause instead of hiding the symptom?
4. Did we avoid spawning extra docs and agents that bought no confidence?
