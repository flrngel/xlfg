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
3. In `DOCS_RUN_DIR/context.md`, record:
   - The raw user request
   - Assumptions
   - Constraints (env, OS, perf, security, UX)

## Phase 2 — Map (parallel planning subagents)

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

## Phase 3 — Reduce (spec + plan + user checkpoint)

1. Read all map outputs.
2. Produce `DOCS_RUN_DIR/plan.md` with:

   - A short summary
   - **Ordered checklist** of tasks (checkboxes)
   - Explicit “definition of done” for this run
   - Verification commands to run (from repo-map + test-plan)
   - Rollback/mitigation notes for risky changes

3. Ask the user **only the minimum clarifying questions** required to avoid building the wrong thing.
4. Get explicit approval to proceed.

## Phase 4 — Implement (single-lead by default)

Default mode: **one lead implementer** does all code edits.

Parallelism is allowed for:

- Research (docs, codebase search)
- Test planning
- Reviews

If the user requested swarm mode, use an agent team but keep work conflict-free:

- Each teammate owns separate files/components
- All handoffs happen through `DOCS_RUN_DIR/`

Implementation loop:

- Follow existing repo conventions and patterns.
- Prefer small, reviewable increments.
- Write tests alongside changes.
- Update `plan.md` checkboxes as tasks complete.
- Record notable decisions in `docs/xlfg/knowledge/decision-log.md` (or link from the run).

## Phase 5 — Verify (hard gate)

Run `/xlfg:verify <RUN_ID>`.

If verification fails:

- Fix the *first* actionable failure
- Re-run `/xlfg:verify`
- Repeat until green

## Phase 6 — Review (hard gate)

Run `/xlfg:review <RUN_ID>`.

If any P0 blockers exist:

- Fix them
- Re-run `/xlfg:verify`
- Re-run `/xlfg:review`

## Phase 7 — Ship

1. Ensure `DOCS_RUN_DIR/run-summary.md` exists with:
   - What changed
   - How to test / smoke steps
   - Verification commands run + log paths
   - Post-deploy monitoring & rollback notes

2. Create the final commit(s) and PR (if applicable).

## Phase 8 — Compound

After shipping, run `/xlfg:compound <RUN_ID>` to convert learnings into durable knowledge.

## Completion criteria

Only declare success when:

- `DOCS_RUN_DIR/spec.md` exists and matches what was built
- `DOCS_RUN_DIR/plan.md` checkboxes are complete
- `/xlfg:verify` is green with logs saved
- `/xlfg:review` has no P0 issues
- `DOCS_RUN_DIR/run-summary.md` exists
