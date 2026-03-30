---
description: Internal xlfg phase skill. Use only during /xlfg runs to run proportional multi-lens review and capture only net-new findings or residual risk.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write, Agent, SendMessage
---

# xlfg-review-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Run proportional review after verification, not cleanup theater before it.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read:
   - `spec.md`
   - `verification.md`
   - `workboard.md`
   - optional `risk.md`, `review-summary.md`, `proof-map.md`
   - `docs/xlfg/knowledge/current-state.md`
3. Choose review fan-out by risk:
   - quick / low risk: 0–1 lens
   - standard: 1–2 lenses
   - deep / high risk: up to 4 lenses
4. Use the specialized review agents as lane owners for the chosen lenses:
   - `xlfg-architecture-reviewer`
   - `xlfg-security-reviewer`
   - `xlfg-performance-reviewer`
   - `xlfg-ux-reviewer`
5. Before dispatch, shrink each review assignment to one change cluster plus one review lens. If a single lens would otherwise cover multiple unrelated fixes, split it into review packets (for example `architecture-R1.md`, `architecture-R2.md`) so each reviewer still gets one clear input and one clear output.
6. Keep them foregrounded. Each chosen reviewer must write its own artifact under `DOCS_RUN_DIR/reviews/` before the conductor synthesizes `review-summary.md`. If a reviewer returns only a chat summary or setup note, use `SendMessage` with the returned agent ID to resume the same reviewer once instead of accepting the lane. If no agent ID is available, re-dispatch the exact same packet once.
7. Synthesize `review-summary.md` from the reviewer artifacts. Do not treat an empty or missing reviewer artifact as a clean review.
8. Write `review-summary.md` only when there are real findings or non-trivial residual risks.
9. Update `spec.md` and `workboard.md` with must-fix findings or accepted residual risk.

## Guardrails

- Review is not the first place to discover that verification never happened.
- Capture only net-new findings and real residual risk. One clear input and one clear output are the rule for review packets too.
- If review finds a must-fix issue, send the run back through implement → verify → review yourself.
