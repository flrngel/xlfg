---
name: xlfg
description: Ship production-ready code via file-based multi-agent SDLC + verification.
argument-hint: "[feature/bugfix request]"
---

# /xlfg

Run an **end-to-end software development lifecycle** (SDLC) workflow that produces **production-ready output** with **evidence**.

<input_request>#$ARGUMENTS</input_request>

## Core invariants (do not violate)

1. **File-based context is the system of record.** Plans/specs/decisions live in `docs/xlfg/`.
2. **Independent subagents, file-based handoffs.** Subagents write to files; they do not coordinate via chat.
3. **Evidence-first.** Never say “done” unless `/xlfg:verify` is green and logs exist.
4. **No silent scope creep.** Any new requirement must be written into the spec and re-approved.
5. **Safety gates.** High-risk changes (migrations, auth, payments, deletions) require explicit user confirmation + rollback notes.

## Phase 0 — Ensure scaffolding exists

If `docs/xlfg/index.md` does not exist, run `/xlfg:init` first, then resume.

## Phase 1 — Create a run folder

1. Generate a `RUN_ID`:
   - Format: `<YYYYMMDD-HHMMSS>-<short-slug>`
2. Create:
   - `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>/`
   - `DX_RUN_DIR=.xlfg/runs/<RUN_ID>/`
   - `DOCS_RUN_DIR/context/`
   - `DOCS_RUN_DIR/tasks/`
3. In `DOCS_RUN_DIR/context.md`, record:
   - The raw user request
   - Assumptions
   - Constraints (env, OS, perf, security, UX)

## Phase 2 — Expand context (parallel investigation subagents)

Before planning, proactively surface adjacent requirements and hidden constraints.

Run these **independent** investigation tasks in parallel (file handoffs only):

- Task `xlfg-context-adjacent-investigator` → write `DOCS_RUN_DIR/context/adjacent.md`
- Task `xlfg-context-constraints-investigator` → write `DOCS_RUN_DIR/context/constraints.md`
- Task `xlfg-context-unknowns-investigator` → write `DOCS_RUN_DIR/context/unknowns.md`

Lead reduce step:

- Merge findings into canonical `DOCS_RUN_DIR/context.md`.
- Add two explicit sections:
  - `Candidate scope expansions`
  - `Out-of-scope backlog`
- Any expansion beyond the raw request must be explicitly approved by the user before implementation.

## Phase 3 — Map (parallel planning subagents)

Launch **independent** planning subagents in parallel. Each agent must:

- Read `DOCS_RUN_DIR/context.md`
- Inspect the repository as needed
- Write output to the specified file
- Keep output structured and actionable

Run these in parallel with Task tool:

- Task `xlfg-repo-mapper` → write `DOCS_RUN_DIR/repo-map.md`
- Task `xlfg-spec-author` → write `DOCS_RUN_DIR/spec.md`
- Task `xlfg-test-strategist` → write `DOCS_RUN_DIR/test-plan.md`
- Task `xlfg-risk-assessor` → write `DOCS_RUN_DIR/risk.md`

(If UI is involved, also run Task `xlfg-ux-reviewer` early to propose UX acceptance criteria.)

## Phase 4 — Reduce (spec + plan + user checkpoint)

1. Read all map outputs.
2. Produce `DOCS_RUN_DIR/plan.md` with:

   - A short summary
   - **Ordered checklist** of tasks (checkboxes)
   - Explicit “definition of done” for this run
   - Verification commands to run (from repo-map + test-plan)
   - Rollback/mitigation notes for risky changes

3. Ask the user **only the minimum clarifying questions** required to avoid building the wrong thing.
4. Get explicit approval to proceed.

## Phase 5 — Implement (lead-orchestrated, mandatory pair mode)

Lead agent owns implementation orchestration and completion.

Mandatory pair loop (per task in `plan.md`):

1. Spawn Task `xlfg-task-implementer` with:
   - `DOCS_RUN_DIR`
   - task id + acceptance criteria
   - allowed file scope
   - implementer output path: `DOCS_RUN_DIR/tasks/<task-id>/implementer-report.md`
2. Spawn Task `xlfg-task-checker` with:
   - the same task contract
   - checker output path: `DOCS_RUN_DIR/tasks/<task-id>/checker-report.md`
3. Checker validates against `spec.md`, `test-plan.md`, `risk.md`, and changed files.
4. Lead decides:
   - If accepted: mark task done in `plan.md`
   - If changes required: run another implementer pass
5. Hard cap: max 3 checker loops per task, then lead resolves manually.

Conflict-control rules:

- Implementer and checker do not coordinate via chat.
- Checker writes findings to file; by default checker does not edit production code.
- Keep ownership conflict-free by constraining task scope.
- All handoffs happen through `DOCS_RUN_DIR/`.

General implementation rules still apply:

- Follow existing repo conventions and patterns.
- Prefer small, reviewable increments.
- Write tests alongside changes.
- Update `plan.md` checkboxes as tasks complete.
- Record notable decisions in `docs/xlfg/knowledge/decision-log.md` (or link from the run).

## Phase 6 — Verify (hard gate)

Run `/xlfg:verify <RUN_ID>`.

If verification fails:

- Fix the *first* actionable failure
- Re-run `/xlfg:verify`
- Repeat until green

## Phase 7 — Review (hard gate)

Run `/xlfg:review <RUN_ID>`.

If any P0 blockers exist:

- Fix them
- Re-run `/xlfg:verify`
- Re-run `/xlfg:review`

## Phase 8 — Ship

1. Ensure `DOCS_RUN_DIR/run-summary.md` exists with:
   - What changed
   - How to test / smoke steps
   - Verification commands run + log paths
   - Post-deploy monitoring & rollback notes

2. Create the final commit(s) and PR (if applicable).

## Phase 9 — Compound

After shipping, run `/xlfg:compound <RUN_ID>` to convert learnings into durable knowledge.

## Completion criteria

Only declare success when:

- `DOCS_RUN_DIR/spec.md` exists and matches what was built
- `DOCS_RUN_DIR/plan.md` checkboxes are complete
- Every task in `plan.md` has:
  - `DOCS_RUN_DIR/tasks/<task-id>/implementer-report.md`
  - `DOCS_RUN_DIR/tasks/<task-id>/checker-report.md` with `Verdict: ACCEPT`
- `/xlfg:verify` is green with logs saved
- `/xlfg:review` has no P0 issues
- `DOCS_RUN_DIR/run-summary.md` exists
