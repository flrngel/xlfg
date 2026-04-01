---
description: Internal xlfg phase skill. Use only during /xlfg runs to resolve messy user intent into a compact contract inside spec.md before broad repo fan-out.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, WebSearch, WebFetch, Agent, SendMessage
---

# xlfg-intent-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Resolve the user's request into a compact intent contract inside `spec.md` before broad repo fan-out.

This phase exists because users often provide:
- incomplete context
- multiple asks in one message
- hidden acceptance criteria
- stale or mistaken assumptions
- overloaded "and also" requests

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read only:
   - `context.md`
   - `memory-recall.md`
   - `spec.md`
   - `workboard.md`
   - `docs/xlfg/knowledge/current-state.md`
3. Use lightweight repo reads first. Use targeted web research only when:
   - a term is unfamiliar or likely stale
   - the request depends on current external facts
   - freshness changes the meaning of the request
4. Invoke `xlfg-query-refiner` explicitly and treat it as the lane owner for messy-intent resolution. Give it one atomic mission: resolve the intent contract in `spec.md` and nothing else. Use no other specialists unless they materially reduce a blocking ambiguity.
5. Do not run xlfg specialists in background for this workflow. Keep them foregrounded, short-lived, and leaf-only so artifact writes, stop events, and workboard state stay synchronized.
6. Require the specialist to materially update `spec.md`. If it returns without updating the intent contract, or returns only with setup notes, use `SendMessage` with the returned agent ID to resume the same specialist once with the same mission packet; if no agent ID is available, re-dispatch the same packet once. Only after the second incomplete return may you record the specialist failure and repair the contract yourself before continuing.
7. Update `spec.md` so the top `Intent contract` and `Objective groups` sections are concrete:
   - `resolution`: `proceed` | `proceed-with-assumptions` | `needs-user-answer`
   - stable IDs for direct asks (`Q1`, `Q2`, ...)
   - stable IDs for implied asks (`I1`, `I2`, ...)
   - stable IDs for acceptance criteria (`A1`, `A2`, ...)
   - non-goals, requested constraints, assumptions, blocking ambiguities, and the carry-forward anchor
   - objective groups (`O1`, `O2`, ...) with covers / depends_on / completion notes
8. Update `workboard.md` so the objective ledger reflects the same objective groups and the next action is visible.

## Resolution rule

- Default to `proceed` when the request is clear enough to act.
- Use `proceed-with-assumptions` when the request is implementable and the assumptions are low-risk, explicit, and reversible.
- Use `needs-user-answer` only when correctness would materially change and repo truth plus current research cannot ground a safe default.

## Blocking-question rule

If `resolution` is `needs-user-answer`:
- ask at most **three** concise numbered blocking questions
- state the smallest safe assumptions you refused to make
- stop the batch after surfacing the blocker

## Delegation packet rules

- Preseed the target artifact before dispatch. The parent conductor should create the file named in `PRIMARY_ARTIFACT` with `Status: IN_PROGRESS`, the scoped mission, and a short checklist so the specialist is resuming a concrete work item instead of starting from an empty chat turn.
- Every specialist packet must begin with machine-readable headers:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only
```

- Pass objective context, not just a naked query. Include the exact ask, nearby constraints, and why the artifact matters to the next phase.
- Only the phase conductor may delegate. Never ask a specialist to spawn nested subagents or fan out further from inside the lane.
- Default to **sequential** dispatch for artifact-producing planning/context work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Guardrails

- Do not recreate a separate intent file.
- Do not broad-scan the repo until the intent contract exists. One clear input and one clear output are the rule for this lane.
- When the query bundles multiple asks, split them into the smallest stable objective groups instead of collapsing them into one muddy goal.
- Keep the carry-forward anchor short enough that later phases can reread it quickly.
