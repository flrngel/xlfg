---
name: xlfg
description: Full autonomous engineering workflow with diagnosis-first planning and contract-shared verification.
argument-hint: "[feature description, bugfix, or product request]"
disable-model-invocation: true
---

Run these slash commands in order. Do not invent a shortcut workflow.

## Workflow

1. `/xlfg:prepare`
2. `/xlfg:plan $ARGUMENTS`
3. Capture the `RUN_ID` printed by `/xlfg:plan`.
4. `/xlfg:implement <RUN_ID>`
5. `/xlfg:verify <RUN_ID> full`
6. `/xlfg:review <RUN_ID>`
7. `/xlfg:compound <RUN_ID>`

## Rules

- `/xlfg:prepare` should be fast. If the scaffold is current, it should effectively no-op.
- Do not start coding before `/xlfg:plan` finishes.
- `/xlfg:plan` must produce `memory-recall.md`, `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `test-contract.md`, `env-plan.md`, and `plan.md`.
- If `/xlfg:plan` surfaces blocking clarification, stop, ask the question, update the plan, and only then continue.
- If `/xlfg:implement` invalidates the diagnosis, return to planning instead of pushing forward with a patch.
- Finish with a concise final summary that includes:
  - `RUN_ID`
  - verification result
  - run artifact path
  - unresolved risks (or `none`)

Start with step 1 now.
