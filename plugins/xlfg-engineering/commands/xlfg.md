---
name: xlfg
description: Query-first, why-first production harness workflow with bounded planning, honest proof, and compounding.
argument-hint: "[feature description, bugfix, or product request]"
disable-model-invocation: true
---

Run these slash commands in order. Do not invent a shortcut workflow.

## Workflow

1. `/xlfg:prepare`
2. `/xlfg:recall $ARGUMENTS`
3. `/xlfg:plan $ARGUMENTS`
4. Capture the `RUN_ID` printed by `/xlfg:plan`.
5. Read `docs/xlfg/runs/<RUN_ID>/harness-profile.md` and note the recommended verify mode.
6. `/xlfg:implement <RUN_ID>`
7. `/xlfg:verify <RUN_ID> <mode-from-harness-profile.md>`
8. `/xlfg:review <RUN_ID>`
9. `/xlfg:compound <RUN_ID>`

## Rules

- `/xlfg:prepare` should be fast. If the scaffold is current, it should effectively no-op.
- `/xlfg:recall` is mandatory. Even a useful **no-hit** is valuable because it prevents fake memory reuse.
- `/xlfg:plan` must write `query-contract.md` before broad repo fan-out.
- `query-contract.md` must keep direct asks, implied asks, developer/product intention, and prohibited shallow fixes visible for the whole run.
- `/xlfg:plan` must preserve the strongest recall hits or an explicit no-hit result in `memory-recall.md` before broad repo fan-out begins.
- `/xlfg:plan` must produce `query-contract.md`, `why.md`, `diagnosis.md`, `solution-decision.md`, `harness-profile.md`, `flow-spec.md`, `test-contract.md`, `env-plan.md`, `workboard.md`, and `proof-map.md`.
- `harness-profile.md` chooses the minimum harness intensity that still gives honest proof. Do not blindly run the deepest workflow for every task.
- `workboard.md` is the run-truth ledger. Keep it current.
- `proof-map.md` is the proof contract. A green command run is not enough if the proof map still has a gap or if a direct ask is still uncovered.
- Re-read the **carry-forward anchor** in `query-contract.md` at the start of implementation, verification, review, and every task handoff.
- Do not start coding before `/xlfg:plan` finishes.
- If `/xlfg:implement` invalidates the diagnosis, return to planning instead of pushing forward with a patch.
- Finish with a concise final summary that includes:
  - `RUN_ID`
  - query / intent summary
  - why summary
  - recall summary (`strong hit` or `no relevant prior memory`)
  - chosen harness profile
  - verification result
  - run artifact path
  - whether shared knowledge was promoted or kept branch-local (`current-state-candidate.md`)
  - unresolved risks or uncovered implied asks (or `none`)

Start with step 1 now.
