# xlfg architecture

## Command architecture

`/xlfg` is intentionally a **macro**. It should not hide the workflow in one giant prompt.

```text
/xlfg
  ├─ /xlfg:prepare
  ├─ /xlfg:recall
  ├─ /xlfg:plan
  ├─ /xlfg:implement
  ├─ /xlfg:verify
  ├─ /xlfg:review
  └─ /xlfg:compound
```

`/xlfg:init` remains available as a manual bootstrap / repair command, but the main workflow should prefer the fast prepare/migrate check.

This keeps the workflow debuggable, composable, and easy to re-run from any intermediate stage.

## Shared file protocol

Every serious run writes:

- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`

These files are the contract shared across planning, implementation, verification, review, and compounding.

## Harness profile model

The harness profile chooses the minimum honest intensity for the run:

- `quick`
- `standard`
- `deep`

The profile controls:

- max ordered tasks
- max checker loops per task
- max parallel subagents
- recommended verify mode
- required review lenses
- escalation triggers

This is xlfg’s lightweight answer to “execution modes” in larger harness systems.

## Memory split

- `docs/xlfg/knowledge/` → tracked durable knowledge
- `docs/xlfg/knowledge/agent-memory/` → tracked role-specific memory
- `docs/xlfg/runs/` → local episodic evidence
- `.xlfg/` → ephemeral raw logs

## Workboard and proof map

Two files became central in 2.0.5:

- `workboard.md` → stage / task truth for the run
- `proof-map.md` → requirement-to-evidence truth for the run

The workboard answers: *where are we and what is next?*

The proof map answers: *what would count as honest proof, and do we have it yet?*

## Quality placement

Quality is not deferred to the end.

- **Planning** prevents bad direction.
- **Implementation** prevents bad code from spreading.
- **Verification** proves the contract.
- **Review** confirms there are no blind spots.
- **Compounding** upgrades future runs.

## Progressive agent loading

Not every run needs every planner or reviewer.

The core planning agents always run:
- why analyst
- repo mapper
- root-cause analyst
- spec author
- test strategist
- env doctor
- solution architect
- harness profiler

Optional agents should load only when the diagnosis justifies them. This keeps context and runtime cost under control.

## Implementation loop

For each task:

1. `xlfg-test-implementer`
2. `xlfg-task-implementer`
3. targeted proof
4. `xlfg-task-checker`

If the checker rejects the task up to the profile budget without a new diagnosis, stop and update the plan.
