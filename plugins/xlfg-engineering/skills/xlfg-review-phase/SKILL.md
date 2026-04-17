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
   - standard: 1 lens
   - deep / high risk: up to 2 lenses
4. Use the specialized review agents as lane owners for the chosen lenses:
   - `xlfg-architecture-reviewer`
   - `xlfg-security-reviewer`
   - `xlfg-performance-reviewer`
   - `xlfg-ux-reviewer`
5. Before dispatch, shrink each review assignment to one change cluster plus one review lens. If a single lens would otherwise cover multiple unrelated fixes, split it into review packets (for example `architecture-R1.md`, `architecture-R2.md`) so each reviewer still gets one clear input and one clear output.
6. Keep them foregrounded, short-lived, and leaf-only. Preseed each review artifact before dispatch. Each chosen reviewer must write its own artifact under `DOCS_RUN_DIR/reviews/` before the conductor synthesizes `review-summary.md`. If a reviewer returns only a chat summary or setup note, use `SendMessage` with the returned agent ID to resume the same reviewer once instead of accepting the lane. If no agent ID is available, re-dispatch the exact same packet once.
7. Synthesize `review-summary.md` from the reviewer artifacts. Do not treat an empty or missing reviewer artifact as a clean review.
8. Write `review-summary.md` only when there are real findings or non-trivial residual risks.
9. Update `spec.md` and `workboard.md` with must-fix findings or accepted residual risk.

## Delegation packet rules

- Preseed the target artifact before dispatch. The parent conductor should create the file named in `PRIMARY_ARTIFACT` with YAML frontmatter `status: IN_PROGRESS`, the scoped mission, and a short checklist so the specialist is resuming a concrete work item instead of starting from an empty chat turn.
- Every specialist packet must begin with machine-readable headers:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only

OWNERSHIP_BOUNDARY:
- Own: one review lens on one change cluster, limited to net-new findings or residual risk
- Do not redo: verification failures, task-checker findings, prior review-lens findings, or planning-phase risk notes unless implementation evidence contradicts them
- Consume: `spec.md`, `verification.md`, changed file list, and prior review artifacts listed below

CONTEXT_DIGEST:
- The relevant objective(s) and false-success trap from `spec.md`
- The verdict and key findings from `verification.md`
- The changed file list from implementation

PRIOR_SIBLINGS:
- <path/to/reviews/<other-lens>-review.md>: <one-line summary of what it already flagged, or `none`>
```

- `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, and `PRIOR_SIBLINGS` are mandatory. See `agents/_shared/output-template.md` for the canonical shape. The digest saves the reviewer 3–5 turns of re-reading files the conductor already loaded. The siblings list is how a second reviewer (e.g., security after architecture) avoids re-flagging findings the first reviewer already raised — net-new findings only.
- Review ownership boundaries:
  - Every reviewer must fill "Already covered by verification" before "Net-new findings".
  - Architecture owns structural drift and boundaries, not security, performance, or UX unless those are the structural cause.
  - Security owns auth/data/secret/injection risks, not generic maintainability or harness speed.
  - Performance owns runtime and harness cost traps, not broad architecture preference.
  - UX owns user-flow and accessibility critique not already covered by `ui-verification.md` or checker DA results.
- Pass objective context, not just a naked query. Include the exact ask, nearby constraints, and why the artifact matters to the next phase.
- Only the phase conductor may delegate. Never ask a reviewer to spawn nested subagents or split its own review lane.
- Default to **sequential** dispatch for artifact-producing planning/context work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Verdicts

- `APPROVE` — ship.
- `APPROVE-WITH-NOTES` — ship; findings recorded as accepted residual risk.
- `APPROVE-WITH-NOTES-FIXED` — reviewer flagged a P1 concern with an explicit fix-in-place disposition (e.g. "add a one-line comment", "rename this parameter"), the conductor applied the fix immediately, and the deterministic proof subset was re-run green. Record the fix in `review-summary.md` under "Fixed in-run" with the before/after one-liner. This verdict does **not** consume a loopback — it is cheaper than a full `implement → verify → review` round trip and the review already named the exact change.
- `MUST-FIX` — do not ship. Send the run back through `implement → verify → review`. This DOES consume a loopback.

Use `APPROVE-WITH-NOTES-FIXED` only when all three are true: (1) reviewer explicitly labeled the finding "fix in place" or equivalent, (2) the fix is a ≤ a few-line local edit, (3) the deterministic proof subset re-ran green after the fix. Anything bigger is `MUST-FIX`.

## Guardrails

- Review is not the first place to discover that verification never happened.
- Capture only net-new findings and real residual risk. One clear input and one clear output are the rule for review packets too.
- If review finds a must-fix issue, send the run back through implement → verify → review yourself.
