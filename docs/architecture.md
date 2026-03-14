# xlfg architecture

## Command architecture

`/xlfg` is intentionally a **macro**.

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

`/xlfg:init` remains a manual bootstrap / repair command.

## Shared run protocol

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

It controls fan-out, checker-loop budget, verify depth, and required review lenses.

## Knowledge architecture (2.0.6)

### Write model (tracked)

- `knowledge/service-context.md`
- `knowledge/write-model.md`
- `knowledge/commands.json`
- `knowledge/cards/<kind>/<branch-slug>/...`
- `knowledge/events/<branch-slug>/...json`
- `knowledge/agent-memory/<role>/cards/<branch-slug>/...`

### Read model (local generated)

- `knowledge/_views/current-state.md`
- `knowledge/_views/<kind>.md`
- `knowledge/_views/agent-memory/<role>.md`
- `knowledge/_views/ledger.jsonl`
- `knowledge/_views/worktree.md`

### Evidence

- `docs/xlfg/runs/` → local episodic evidence
- `.xlfg/` → ephemeral raw logs

The main rule is: **write immutable tracked units, read generated local rollups**.

## Workboard and proof map

Two files are central to honest execution:

- `workboard.md` → stage / task truth
- `proof-map.md` → requirement-to-evidence truth

The workboard answers: *where are we and what is next?*

The proof map answers: *what exactly would count as proof?*

## Quality placement

Quality is not deferred to the end.

- planning prevents bad direction
- implementation prevents bad code from spreading
- verification proves the contract
- review confirms there are no blind spots
- compounding improves the next run

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

Optional agents load only when the diagnosis justifies them.

## Implementation loop

For each task:

1. `xlfg-test-implementer`
2. `xlfg-task-implementer`
3. targeted proof
4. `xlfg-task-checker`

If the checker keeps rejecting within the profile budget and the diagnosis changes, go back to planning.
