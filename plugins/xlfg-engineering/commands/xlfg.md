---
name: xlfg
description: Recall-first autonomous engineering workflow with diagnosis, contracts, verification, and compounding.
argument-hint: "[feature description, bugfix, or product request]"
disable-model-invocation: true
---

Run these slash commands in order. Do not invent a shortcut workflow.

## Workflow

1. `/xlfg:prepare`
2. `/xlfg:recall $ARGUMENTS`
3. `/xlfg:plan $ARGUMENTS`
4. Capture the `RUN_ID` printed by `/xlfg:plan`.
5. `/xlfg:implement <RUN_ID>`
6. `/xlfg:verify <RUN_ID> full`
7. `/xlfg:review <RUN_ID>`
8. `/xlfg:compound <RUN_ID>`

## Rules

- `/xlfg:prepare` should be fast. If the scaffold is current, it should effectively no-op.
- `/xlfg:recall` is mandatory. Even a useful **no-hit** is valuable because it prevents fake memory reuse.
- `/xlfg:plan` must preserve the strongest recall hits or an explicit no-hit result in `memory-recall.md` before broad repo fan-out begins.
- Do not start coding before `/xlfg:plan` finishes.
- `/xlfg:plan` must produce `memory-recall.md`, `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `test-contract.md`, `env-plan.md`, and `plan.md`.
- If `/xlfg:plan` surfaces blocking clarification, stop, ask the question, update the plan, and only then continue.
- If `/xlfg:implement` invalidates the diagnosis, return to planning instead of pushing forward with a patch.
- Finish with a concise final summary that includes:
  - `RUN_ID`
  - recall summary (`strong hit` or `no relevant prior memory`)
  - verification result
  - run artifact path
  - unresolved risks (or `none`)

Start with step 1 now.
