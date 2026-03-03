# xlfg architecture

## Command architecture

`/xlfg` is intentionally a **macro**. It should not hide the workflow in one giant prompt.

```text
/xlfg
  ├─ /xlfg:init
  ├─ /xlfg:plan
  ├─ /xlfg:implement
  ├─ /xlfg:verify
  ├─ /xlfg:review
  └─ /xlfg:compound
```

This keeps the workflow debuggable, composable, and easy to re-run from any intermediate stage.

## Shared file protocol

Every serious run writes:

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `plan.md`
- `scorecard.md`

These files are the contract shared across planning, implementation, verification, review, and compounding.

## Quality placement

Quality is not deferred to the end.

- **Planning** prevents bad direction.
- **Implementation** prevents bad code from spreading.
- **Verification** proves the contract.
- **Review** confirms there are no blind spots.
- **Compounding** upgrades future runs.

## Implementation loop

For each task:

1. `xlfg-test-implementer`
2. `xlfg-task-implementer`
3. targeted proof
4. `xlfg-task-checker`

If the checker rejects the task twice without a new diagnosis, stop and update the plan.
