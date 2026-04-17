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
8. Update the objective-ledger and next-action sections of `workboard.md`. The `## Phase status` block is rendered by the conductor from `.xlfg/phase-state.json` after the phase returns.

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

Follow `agents/_shared/dispatch-rules.md` for the full delegation contract (packet-size ladder, preseed rule, machine-readable headers with `PRIMARY_ARTIFACT` / `DONE_CHECK` / `RETURN_CONTRACT` / `OWNERSHIP_BOUNDARY` / `CONTEXT_DIGEST` / `PRIOR_SIBLINGS` / `Do not redo` / `Consume:`, micro-packet budget, proof budget, compaction, sequential-dispatch default, resume-same-specialist-before-fallback). Only the phase conductor may delegate.

Every intent-phase packet MUST begin with the machine-readable headers from `_shared/dispatch-rules.md §3`. Intent rarely has prior siblings (it is the first delegating phase), so `PRIOR_SIBLINGS: none` is the common case here — but the field must still be present so downstream phases inherit a consistent contract.

The intent specialist owns request decomposition only (`Intent contract` and `Objective groups` sections in `spec.md`). Later context or planning specialists may propose a gap note if evidence contradicts the contract, but they must not silently rewrite intent while doing repo mapping, design, proof, or implementation work.

Compact returned artifacts before updating `spec.md`: carry forward only resolution, objective groups, blockers, and direct/implied ask IDs; do not paste the full specialist report into the run card.

## Guardrails

- Do not recreate a separate intent file.
- Do not broad-scan the repo until the intent contract exists. One clear input and one clear output are the rule for this lane.
- When the query bundles multiple asks, split them into the smallest stable objective groups instead of collapsing them into one muddy goal.
- Keep the carry-forward anchor short enough that later phases can reread it quickly.
