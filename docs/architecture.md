# xlfg architecture (2.0.10)

`/xlfg` is now intentionally simple at the top level:

```text
/xlfg
  ├─ /xlfg:recall
  ├─ /xlfg:plan
  ├─ /xlfg:implement
  ├─ /xlfg:verify
  ├─ /xlfg:review
  └─ /xlfg:compound
```

`/xlfg:prepare` and `/xlfg:init` still exist, but they are **manual maintenance commands**. They are not the product workflow.

## The real harness model

### 1) Semantic state
Keep the request and root problem stable:
- `query-contract.md`
- `why.md`
- `diagnosis.md`

### 2) Structural state
Keep the repo-facing solution stable:
- `repo-map.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`

### 3) Execution state
Keep task/proof truth stable:
- `plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`

This split is the core architectural change in 2.0.10. It reduces drift by keeping request truth, codebase truth, and execution/proof truth separate.

## Planning model

Planning is a **lead-agent synthesis pass** with a small specialist budget.

Default planning specialist order:
1. query refiner
2. repo mapper (only if needed)
3. root-cause analyst
4. spec author
5. test strategist
6. solution architect (only if needed)

The lead planner owns:
- `why.md`
- `harness-profile.md`
- `test-readiness.md`
- `spec.md`
- `plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`

## Execution ownership

By default, the **agent** owns:
- implementation
- repo-local config changes needed for correctness
- tests and test harness updates
- dev-server orchestration
- major local verification

Only escalate to the user for:
- missing secrets / credentials
- destructive external or production actions
- unresolved product decisions that change correctness

## Verification model

Verification compiles from the predeclared scenario contract first, then adds supplemental repo checks.

A run is only green when:
- the promised scenario-targeted proofs actually ran
- proof-map rows are covered
- direct asks and non-negotiable implied asks have evidence or explicit approved deferral
- the evidence still matches the why and root solution
