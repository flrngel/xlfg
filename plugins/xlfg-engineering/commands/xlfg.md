---
name: xlfg
description: Ship production-ready code via file-based multi-agent SDLC + verification.
argument-hint: "[feature/bugfix request]"
---

# /xlfg

Run an **end-to-end software development lifecycle** (SDLC) workflow that produces **production-ready output** with **evidence**.

<input_request>#$ARGUMENTS</input_request>

## Reality check (how to keep this from taking 30+ minutes)

This workflow can be expensive because it intentionally uses multiple independent subagents plus verification.

To avoid wasting time, **pick a run tier** up front based on the request complexity:

- **Tier S (small):** 1–2 files, no new user-facing flows, low risk.
  - Skip Phase 2 (context expansion) unless unclear.
  - Skip the full multi-agent planning map; write a compact `spec.md` + `plan.md` directly.
  - Implementation can be a single scoped task (still requires verification).
- **Tier M (medium):** 3–10 files, normal feature/bugfix.
  - Skip Phase 2. Run Phase 3 partially (spec-author only).
  - Lead implements directly but MUST spawn checker, verify, and review agents.
  - Keep plan tasks **coarse** (aim <= 5 tasks) to avoid implementer/checker explosion.
- **Tier L (large):** >10 files, cross-cutting refactor, risky domains.
  - Full workflow as written.
  - Expect multiple verify/review iterations.

Default to **Tier M** if uncertain.

### Must-spawn agents per tier (non-negotiable)

Every tier has a **minimum set of agents that MUST be spawned via the Task tool**. The lead agent must NOT substitute itself for these — independent perspective is the point.

| Phase | Agent | Tier S | Tier M | Tier L |
|-------|-------|--------|--------|--------|
| P2 | `xlfg-context-*` investigators (×3) | skip | skip | **spawn** |
| P3 | `xlfg-repo-mapper` | skip | skip | **spawn** |
| P3 | `xlfg-spec-author` | skip | **spawn** | **spawn** |
| P3 | `xlfg-test-strategist` | skip | skip | **spawn** |
| P3 | `xlfg-risk-assessor` | skip | skip | **spawn** |
| P5 | `xlfg-task-implementer` | lead may implement directly | lead may implement directly | **spawn** |
| P5 | `xlfg-task-checker` | **spawn** | **spawn** | **spawn** |
| P6 | `xlfg-verify-runner` | lead may run inline | **spawn** | **spawn** |
| P6 | `xlfg-verify-reducer` | lead may write inline | **spawn** | **spawn** |
| P7 | `xlfg-security-reviewer` | skip | **spawn** | **spawn** |
| P7 | `xlfg-architecture-reviewer` | skip | **spawn** | **spawn** |
| P7 | `xlfg-performance-reviewer` | skip | conditional | conditional |
| P7 | `xlfg-ux-reviewer` | skip | conditional | conditional |

**Key rules:**
- **The checker agent is ALWAYS spawned.** The lead must NEVER write checker reports itself — self-review defeats the purpose of independent verification.
- "Lead may implement directly" means the lead can write code and the implementer report itself, but must still spawn the checker.
- "Lead may run/write inline" means the lead can run verification commands and write `verification.md` directly for trivial changes.
- "Conditional" means spawn only if the change touches the relevant area (performance-sensitive code, user-facing UI).

**Minimum Task agent spawns:** Tier S = 1 per task (checker), Tier M = 5–6 total, Tier L = 13+.

## Important limitation (why "compound" feels broken)

Claude Code slash commands are **not composable**: one command cannot truly "run" another command.

So when this workflow references `/xlfg:init`, `/xlfg:verify`, `/xlfg:review`, or `/xlfg:compound`, you must:

- either **perform the steps inline** in this same run, or
- explicitly tell the user to invoke the subcommand.

This command is written to be **self-contained**: perform the referenced steps inline by default.

## Core invariants (do not violate)

1. **File-based context is the system of record.** Plans/specs/decisions live in `docs/xlfg/`.
2. **Independent subagents, file-based handoffs.** Subagents write to files; they do not coordinate via chat.
3. **Evidence-first.** Never say “done” unless `/xlfg:verify` is green and logs exist.
4. **No silent scope creep.** Any new requirement must be written into the spec and re-approved.
5. **Safety gates.** High-risk changes (migrations, auth, payments, deletions) require explicit user confirmation + rollback notes.

## Phase 0 — Ensure scaffolding exists

If `docs/xlfg/index.md` does not exist, **bootstrap scaffolding inline** (equivalent to `/xlfg:init`) and continue:

- Create directories:
  - `docs/xlfg/knowledge/`
  - `docs/xlfg/runs/`
  - `.xlfg/runs/`
- Ensure `.xlfg/` is in the repo root `.gitignore` (append if missing).
- Create missing durable knowledge files (do not overwrite existing):
  - `docs/xlfg/index.md`
  - `docs/xlfg/knowledge/quality-bar.md`
  - `docs/xlfg/knowledge/decision-log.md`
  - `docs/xlfg/knowledge/patterns.md`
  - `docs/xlfg/knowledge/testing.md`

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

Tier rule:

- **Tier S:** skip this phase unless requirements/constraints are unclear.
- **Tier M:** skip this phase. The lead assesses context directly for normal features/bugfixes.
- **Tier L:** run as written (spawn all three investigators in parallel).

Run these **independent** investigation tasks in parallel (file handoffs only):

- Task `xlfg-context-adjacent-investigator` → write `DOCS_RUN_DIR/context/adjacent.md`
- Task `xlfg-context-constraints-investigator` → write `DOCS_RUN_DIR/context/constraints.md`
- Task `xlfg-context-unknowns-investigator` → write `DOCS_RUN_DIR/context/unknowns.md`

Lead reduce step:

- Merge findings into canonical `DOCS_RUN_DIR/context.md`.
- Add two explicit sections:
  - `Candidate scope expansions`
  - `Out-of-scope backlog`
- Default behavior: do not implement `Candidate scope expansions` unless already requested by the user.
- Move unapproved expansions to `Out-of-scope backlog` and continue.

## Phase 3 — Map (parallel planning subagents)

Tier rule:

- **Tier S:** skip the full map. Write a compact `spec.md` + `plan.md` directly from repo inspection.
- **Tier M:** spawn `xlfg-spec-author` only (independent spec ensures requirements are crisp). Lead writes `plan.md` directly from spec + repo inspection. Skip repo-mapper, test-strategist, risk-assessor.
- **Tier L:** run as written (spawn all four planning agents in parallel).

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

## Phase 4 — Reduce (spec + plan + auto-continue)

1. Read all map outputs.
2. Produce `DOCS_RUN_DIR/plan.md` with:

   - A short summary
   - **Ordered checklist** of tasks (checkboxes)
   - Explicit “definition of done” for this run
   - Verification commands to run (from repo-map + test-plan)
   - Rollback/mitigation notes for risky changes

3. Resolve non-blocking unknowns by writing explicit assumptions into `context.md` and `spec.md`.
4. Continue directly to implementation without waiting for plan approval.
5. Ask the user only when both are true:
   - A decision is truly blocking correctness or safety
   - No safe default assumption exists

## Phase 5 — Implement (lead-orchestrated, mandatory pair mode)

Lead agent owns implementation orchestration and completion.

**CRITICAL: The lead must NEVER write `checker-report.md` files itself.** Checker reports must always come from a spawned `xlfg-task-checker` agent. Writing your own checker report is self-review, not independent verification — it defeats the core value of the pair loop. If you catch yourself about to write a checker report, stop and spawn the agent instead.

Tier rules for implementation:

- **Tier S/M:** The lead MAY implement code directly and write the `implementer-report.md` itself (skip `xlfg-task-implementer`). This is acceptable because the implementer is just doing the work — the independent value comes from the checker.
- **Tier L:** Spawn `xlfg-task-implementer` for each task to keep the lead focused on orchestration.
- **All tiers:** MUST spawn `xlfg-task-checker` for every task. No exceptions.

Mandatory pair loop (per task in `plan.md`):

1. Implement the task (lead directly for Tier S/M, or spawn Task `xlfg-task-implementer` for Tier L):
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
- Do not pause for implementation permission after Phase 4.
- If a safety-gated high-risk change is required, request explicit confirmation once right before execution.

## Phase 6 — Verify (hard gate)

Perform verification **inline** (equivalent to `/xlfg:verify <RUN_ID>`):

Tier rules:

- **Tier S:** The lead MAY run verification commands directly (via Bash) and write `DOCS_RUN_DIR/verification.md` itself. Still must record commands run, exit codes, and GREEN/RED status.
- **Tier M/L:** MUST spawn `xlfg-verify-runner` then `xlfg-verify-reducer`. Structured logs in `.xlfg/` are required.

For Tier M/L:

1. Decide canonical commands (prefer repo-native `make`, `package.json` scripts, or README/CONTRIBUTING).
2. Run Task `xlfg-verify-runner` to execute commands and write logs to `.xlfg/runs/<RUN_ID>/verify/<ts>/...`.
   - Prefer **non-interactive** modes (avoid watchers): set `CI=1` when running Node-based tests.
   - If a command appears to hang, add a timeout wrapper if available (e.g., `timeout 20m <cmd>`).
3. Run Task `xlfg-verify-reducer` to write `DOCS_RUN_DIR/verification.md` (and `verify-fix-plan.md` if RED).

If verification fails:

- Fix the *first* actionable failure
- Repeat this verification phase (or ask the user to run `/xlfg:verify <run-id>`)
- Repeat until green

## Phase 7 — Review (hard gate)

Perform review **inline** (equivalent to `/xlfg:review <RUN_ID>`):

Tier rules:

- **Tier S:** The lead MAY skip review agents and write a brief `DOCS_RUN_DIR/review-summary.md` directly (acceptable for trivial, low-risk changes to 1–2 files).
- **Tier M:** MUST spawn `xlfg-security-reviewer` + `xlfg-architecture-reviewer`. Spawn `xlfg-performance-reviewer` and `xlfg-ux-reviewer` conditionally (if relevant areas changed).
- **Tier L:** MUST spawn all four review agents.

For Tier M/L:

- Ensure `DOCS_RUN_DIR/reviews/` exists.
- Run the review agents (security + architecture always; perf/ux conditionally) writing into `DOCS_RUN_DIR/reviews/`.
- Reduce into `DOCS_RUN_DIR/review-summary.md` and block on net-new P0 issues.

If any P0 blockers exist:

- Fix them
- Repeat verification (or ask the user to run `/xlfg:verify <run-id>`)
- Repeat review (or ask the user to run `/xlfg:review <run-id>`)

## Phase 8 — Prepare ship artifacts

1. Ensure `DOCS_RUN_DIR/run-summary.md` exists with:
   - What changed
   - How to test / smoke steps
   - Verification commands run + log paths
   - Post-deploy monitoring & rollback notes

## Phase 9 — Ship

Create the final implementation commit(s) and PR (if applicable).

## Phase 10 — Compound (hard gate, last phase)

Perform compounding **inline** (equivalent to `/xlfg:compound <RUN_ID>`):

1. Ensure `KB_DIR=docs/xlfg/knowledge/` exists.
2. Read run artifacts (if present): `spec.md`, `plan.md`, `test-plan.md`, `risk.md`, `verification.md`, `review-summary.md`, `run-summary.md`.
3. Write `DOCS_RUN_DIR/compound-summary.md` with:
   - What was learned (especially from verify + review overlap)
   - What should be reused next time
   - What to avoid
4. If there are clear durable lessons, append **small, specific** entries to:
   - `KB_DIR/patterns.md`
   - `KB_DIR/decision-log.md`
   - `KB_DIR/testing.md`
   - `KB_DIR/quality-bar.md`
   Keep this tight—do not rewrite the entire files.
5. If `DOCS_RUN_DIR/run-summary.md` is missing, create it.

If compounding adds tracked updates, include them in a follow-up commit/PR update before declaring completion.

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
- `DOCS_RUN_DIR/compound-summary.md` exists
