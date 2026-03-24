---
description: Autonomous SDLC run for serious feature, bugfix, investigation, or delivery work. Executes recall, planning, implementation, verification, review, and compounding in one invocation.
argument-hint: "[feature, bugfix, investigation, or delivery request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, TodoWrite, Task
effort: high
hooks:
  PermissionRequest:
    - matcher: "ExitPlanMode"
      hooks:
        - type: command
          command: >
            echo '{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}'
---

Use this when the user wants a serious engineering run with PM, UX, Engineering, QA, and release discipline.

INPUT: `$ARGUMENTS`

Treat this invocation as **one autonomous run**.

Non-negotiable behavior:

- do the full SDLC here: recall → context → plan → implement → verify → review → compound
- do **not** ask the user to run phase subcommands or sequence the workflow for you
- do **not** pause for internal phase approvals
- ask the user only for true human-only blockers: missing secrets, destructive external approvals, or correctness-changing product ambiguity you cannot ground from the repo or research
- keep `spec.md` as the single source of truth for request truth, chosen solution, task map, proof summary, and PM / UX / Engineering / QA / Release notes
- do not create duplicated planning files unless they change a decision

## Prefer deterministic xlfg helpers when available

If the local helper CLI exists, use it to reduce prompt drift and file-creation mistakes:

1. `xlfg init` (or `xlfg prepare`) to sync scaffold if needed
2. `xlfg start "$ARGUMENTS"` to create the run and capture `RUN_ID`
3. `xlfg recall ...` when deterministic memory lookup would help
4. `xlfg detect` or `xlfg doctor --run <RUN_ID>` when the harness or dev server is unclear
5. `xlfg verify --run <RUN_ID> --mode <auto|fast|full>` for final proof

If the helper is unavailable, perform the equivalent steps manually.

## Run model

Create or capture `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>` and use:

- `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>`
- `DX_RUN_DIR=.xlfg/runs/<RUN_ID>`

Up-front core files only:

- `context.md`
- `memory-recall.md`
- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`

Create optional files only when they materially reduce risk or ambiguity:

- `research.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`
- `proof-map.md`
- `risk.md`
- `review-summary.md`
- `run-summary.md`
- `compound-summary.md`

`verification.md` should be created or updated during verification.

## Spec contract

`spec.md` must stay lean but complete enough that implementation, verification, review, and handoff can all start there. It must cover:

- direct asks, implied asks, and explicit non-goals
- the user outcome and the false-success trap
- repo findings and external findings (`repo-only` if none)
- harness profile and intended verify mode
- chosen solution and rejected shortcuts
- concrete task map
- proof summary and current status
- PM / UX / Engineering / QA / Release notes

## Execution recipe

1. Sync scaffold quietly if missing or stale.
2. Recall the smallest relevant prior knowledge and record strong hits or an explicit no-hit in `memory-recall.md`.
3. Explore repo-local truth first. Use external research only when repo truth is insufficient or the user explicitly asked for research.
4. Write or update `context.md`, `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`.
5. If `test-readiness.md` is not `READY`, repair the plan yourself. Do not hand phase management back to the user.
6. Implement with one owner by default. Use extra subagents only for hard read-only exploration or a specific review lens.
7. Verify honestly. Prefer the helper verifier when present. If verification fails, fix the first actionable failure and rerun.
8. Review proportional to risk. Create `review-summary.md` only when there are real findings or non-trivial residual risk.
9. Compound only verified durable lessons. Promote reusable truth to `docs/xlfg/knowledge/current-state.md`; keep branch-local or run-local lessons in the run when they are not yet durable.
10. Finish with a concise status summary that includes `RUN_ID`, what changed, proof status, residual risk, and next actions if any.

## Hard rules

- This command is the entrypoint. Do not rely on manual `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, or `/xlfg:compound` choreography.
- No duplicated markdown state unless it changes a decision.
- Do not create placeholder docs because a template exists.
- Do not claim GREEN unless changed behavior was actually proven.
- Fix the first actionable failure, not the loudest symptom.
- Prefer repo truth over assumption, and deterministic helpers over prompt-only file ceremony when both are available.
