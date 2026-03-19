---
name: xlfg:plan
description: Build an executable SDLC plan with optional research, explicit ownership, and proof defined before code.
argument-hint: "[feature description, bugfix, research task, or product request]"
---

# /xlfg:plan

Create a real plan the agent can execute. Do **not** write production code in this command.

<input_request>#$ARGUMENTS</input_request>

If the request is empty, ask the user what they want built, fixed, or researched and stop.

## Hard rules

1. **No coding here.** Planning only.
2. **Claude Code stays the lead.** `/xlfg` supplies structure, not bureaucracy.
3. **Recall is mandatory before broad fan-out.**
4. **Research is part of SDLC, but only when needed.** Do not create a fake research phase for repo-local work.
5. **Planning is lead-owned.** Subagents sharpen hard parts; they do not replace coherent planning.
6. **Default specialist budget is tiny.** More agents are not automatically better.
7. **Do not front-load optional docs.** If scaffold seeds extra templates, leave them untouched unless the run actually needs them.
8. **The agent owns the work by default.** Only secrets, destructive approvals, or correctness-changing product ambiguity belong to the human.
9. **Tests and proof come before implementation.**
10. **Pick the minimum honest harness profile.**
11. **Keep the user request separate from the guessed solution.**
12. **Disconfirm yourself.** Record what would prove the plan wrong.
13. **Reject monkey-fix planning.** If a shallow patch could pass the visible check while the real problem survives, the plan is not ready.

## Phase 0 — Minimal bootstrap and run creation

If scaffold/meta is missing or stale, do the smallest silent sync needed and continue.

Create:

- `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>`
- `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>/`
- `DX_RUN_DIR=.xlfg/runs/<RUN_ID>/`

Write the raw request and known constraints to `context.md`.

### Always write these core artifacts

These are the minimum contracts before coding:

- `context.md`
- `query-contract.md`
- `memory-recall.md`
- `why.md`
- `harness-profile.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`
- `proof-map.md`

### Optional artifacts — only when the run needs them

Create or fill these **only if they add decision value**:

- `diagnosis.md` — non-obvious failure, bugfix, or root-cause uncertainty
- `solution-decision.md` — multiple credible approaches or architectural trade-offs
- `flow-spec.md` — user flow / API contract / multi-state behavior changes
- `env-plan.md` — local server, migration, seed, or environment risk
- `research.md` — external standards, unfamiliar framework behavior, recent advisories, or explicit user request for research
- `repo-map.md` — unfamiliar or large codebase where minimal mapping is needed
- `risk.md` — known workaround, follow-up, or ship-risk record
- `scorecard.md` — fill early only when it clarifies readiness; otherwise update during verify/review
- `tasks/` — create task briefs during implementation, not as planning theater

## Phase 1 — Mandatory recall

Before broad repo scanning:

1. Read `docs/xlfg/knowledge/current-state.md` if present.
2. Reuse the preceding `/xlfg:recall` result when available.
3. If recall has not already happened, run it now.
4. Do one request-shaped recall, then one focused follow-up only if the request clearly touches repeated harness, UX, environment, or testing risk.

`memory-recall.md` must record:

- what was queried
- strong matches
- rules carried forward
- rejected near-matches
- explicit no-hit when nothing relevant matched

Do not proceed until `memory-recall.md` is non-placeholder.

## Phase 2 — Lead-owned requirement shaping

Write `query-contract.md` yourself unless the request is genuinely ambiguous enough that `xlfg-query-refiner` will materially help.

Make these concrete:

- work kind: `build` | `bugfix` | `research` | `multi`
- objective groups (`O1`, `O2`, ...)
- direct asks (`Q1`, `Q2`, ...)
- implied asks (`I1`, `I2`, ...)
- requirements (`R1`, `R2`, ...)
- acceptance criteria (`A1`, `A2`, ...)
- constraints the user actually asked for
- reproduction / baseline notes when relevant
- non-goals
- prohibited shallow fixes
- semantic commitments that must survive the run
- carry-forward anchor

If the request is still too ambiguous after one serious pass, ask a blocking question instead of pretending it is clear.

## Phase 3 — Why, ownership, and harness choice

Write `why.md` yourself.

Decide:

- who is affected
- what failure / friction / missed capability matters now
- what false success would still disappoint the user
- the non-negotiable quality bar
- non-goals
- execution ownership

Write `harness-profile.md` with:

- selected profile: `quick` | `standard` | `deep`
- research mode: `none` | `light` | `heavy`
- why the profile fits
- specialist budget
- max checker loops per task
- recommended verify mode
- required review lenses
- escalation triggers

### Default specialist budget

- `quick`: 0–1 specialist total
- `standard`: up to 2 specialists total
- `deep`: up to 4 specialists total

No planning specialist is mandatory. The lead planner may do the entire plan alone.

## Phase 4 — Minimal repo scan

Do the smallest repo scan that makes the work legible.

Only map enough to answer:

- where the changed behavior likely lives
- what interfaces / flows / configs matter
- how the repo is tested and run locally
- what nearby files constrain the change

Use `xlfg-repo-mapper` only when the codebase is broad enough that a small read-only mapping pass will save real time.

## Phase 5 — Research lane (first-class, conditional)

Research is part of the SDLC when the run needs external truth.

Create `research.md` only if **any** of these are true:

- the user explicitly asked for research
- the repo alone cannot answer the correct behavior
- framework / library / API behavior may have changed
- security / privacy / compliance / accessibility standards matter
- the task depends on recent best practices or external constraints

If research is needed:

- keep it scoped
- prefer primary docs and authoritative sources
- distill findings into concrete design / testing / rollout implications
- record what changed because of research versus what came from the repo

## Phase 6 — Diagnosis and solution (only when needed)

Use these artifacts adaptively:

- `diagnosis.md` for bugfixes, flaky behavior, or unclear failure chains
- `solution-decision.md` when multiple approaches are plausible
- `flow-spec.md` when behavior spans states, paths, or user interactions
- `env-plan.md` when verification depends on local environment orchestration

If the change is small and obvious, keep these light or skip them. The goal is better decisions, not more markdown.

## Phase 7 — Write `spec.md` as the run card

`spec.md` is the single-sheet PM / Engineering / QA brief for the run. It should be short enough to re-read often.

It must include:

- work kind and objective coverage
- request truth (direct + implied asks)
- why and user outcome
- research summary (`repo-only` if none)
- diagnosis / key risk summary
- chosen solution
- acceptance criteria
- task map and owners
- test / proof strategy
- PM / UX / Engineering / QA / Release notes
- open questions, deferrals, and rollback notes

## Phase 8 — Plan the delivery and proof

Write `plan.md` as a 3–6 task delivery plan.

For each task include:

- task ID
- objectives / query IDs / scenario IDs covered
- goal
- allowed file scope
- targeted checks
- invariants
- disproof probe
- anti-monkey-fix warning
- owner (`agent` unless truly human-only)

Also include:

- `## Execution ownership`
- `## SDLC lanes` covering Research, Product/UX, Engineering, QA, and Release/Follow-up
- definition of done

Write `test-contract.md` with 1–5 required scenario cards total.

Write `test-readiness.md` with a hard verdict:

- `READY` — the checks are practical enough to code against now
- `REVISE` — the proof contract is too vague, too expensive, or too weak

Write `workboard.md` as the PM/status ledger.

Write `proof-map.md` as the scenario-to-evidence ledger.

## Phase 9 — Planning gate

Implementation may start only when all are true:

- `query-contract.md` is concrete
- `memory-recall.md` is honest
- `why.md` is specific
- `spec.md` reads like a coherent run card, not stitched-together fragments
- `plan.md` has bounded tasks
- `test-contract.md` names practical proofs
- `test-readiness.md` says `READY`
- `workboard.md` and `proof-map.md` are initialized

## Finish this command

Return a concise summary with:

- `RUN_ID`
- work kind
- harness profile
- research mode
- specialists used (or `lead-only`)
- `test-readiness` verdict
- core artifacts written
- optional artifacts written
- blockers or `none`
