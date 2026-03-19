---
name: xlfg
description: Adaptive research-to-release SDLC harness: clarify intent, research only when needed, plan, implement, prove, review, compound.
argument-hint: "[feature, bugfix, investigation, or multi-part delivery]"
disable-model-invocation: true
---

`/xlfg` is a **thin SDLC macro**. Claude Code remains the orchestrator. Use xlfg to add disciplined recall, research, planning, proof, review, and compounding **without turning every task into ceremony**.

## Workflow

1. `/xlfg:recall $ARGUMENTS`
2. `/xlfg:plan $ARGUMENTS`
3. Capture the `RUN_ID` printed by `/xlfg:plan`.
4. Confirm `docs/xlfg/runs/<RUN_ID>/test-readiness.md` says `READY`.
5. Read `docs/xlfg/runs/<RUN_ID>/harness-profile.md` and note the `mode-from-harness-profile.md` guidance for verification.
6. `/xlfg:implement <RUN_ID>`
7. `/xlfg:verify <RUN_ID> <mode-from-harness-profile.md>`
8. `/xlfg:review <RUN_ID>`
9. `/xlfg:compound <RUN_ID>`

## Operating rules

- Default to the **lightest honest path**. `/xlfg` should feel like an SDLC exoskeleton, not a workflow bureaucracy.
- Claude Code stays the primary agent. Do **not** replace it with a swarm just because subagents exist.
- Recall is mandatory. A useful no-hit is still useful.
- Planning is lead-owned. Use specialists only when they clearly improve the plan.
- Research is first-class but **conditional**. Create `research.md` only when repo-local truth is insufficient or the user explicitly asks for research.
- `spec.md` is the **run card**. Keep it concise enough that implementation, verification, and review can all start there.
- `workboard.md` is the PM/status ledger.
- `proof-map.md` is the QA/evidence ledger.
- `test-readiness.md` is the gate before code.
- Default to **one implementation agent**. Add test/checker/review agents only when the harness profile or risk justifies them.
- Never assume the user will do core implementation, repo-local verification, or harness coordination for you.
- If a direct ask, implied ask, proof obligation, or diagnosis changes, update the run artifacts instead of silently drifting.
- Finish with a concise summary that includes:
  - `RUN_ID`
  - work kind
  - research mode (`none` | `light` | `heavy`)
  - harness profile
  - test-readiness verdict
  - verification result
  - PM / Engineering / QA status
  - unresolved risks or `none`

Start with step 1 now.
