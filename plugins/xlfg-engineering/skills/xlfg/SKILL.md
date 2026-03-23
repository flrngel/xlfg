---
name: xlfg
description: Autonomous SDLC operator: understand intent, research only when needed, write a lean run card, implement, verify, review, and compound in one invocation.
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

Use this when the user wants a serious feature, bugfix, investigation, or delivery run with PM / Engineering / QA discipline.

INPUT: `$ARGUMENTS`

Treat `/xlfg` as **one autonomous run**. Do **not** ask the user to invoke `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, or `/xlfg:compound`. Do **not** stop for internal phase approvals. Ask the user only for:

- missing secrets or credentials
- destructive external actions or production-side approvals
- correctness-changing product ambiguity you cannot ground from the repo or research

## Current Claude Code alignment

- Skills are the primary format. Legacy commands are escape hatches, not the main UX.
- Keep context small. `spec.md` is the single source of truth.
- Use built-in Explore or a small read-only subagent only when it materially reduces risk.
- Use external research only when repo-local truth is insufficient or the user explicitly asked for research.
- Prefer one owner and one main line of execution. Extra agents are opt-in, not default.

## Run model

If scaffold is missing or stale, quietly sync it and continue.

Create `RUN_ID=<YYYYMMDD-HHMMSS>-<slug>` and use:

- `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>`
- `DX_RUN_DIR=.xlfg/runs/<RUN_ID>`

Create only these **core files** up front:

- `context.md`
- `memory-recall.md`
- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`

Create **optional files only if they clearly reduce risk or ambiguity**:

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

## Spec contract

`spec.md` absorbs the duplicated state that older xlfg revisions spread across many files. It must cover:

- direct asks, implied asks, and non-goals
- user outcome and false-success warning
- repo findings and external findings (`repo-only` when none)
- harness profile and verify mode
- chosen solution and rejected shortcuts
- task map
- proof summary
- PM / UX / Engineering / QA / Release notes

## Execution

1. Recall the smallest relevant prior knowledge and record honest hits or no-hits in `memory-recall.md`.
2. Explore repo-local context first. Use external research only when needed.
3. Write a lean `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`.
4. If `test-readiness.md` is not `READY`, fix the plan yourself. Do not hand phase management back to the user.
5. Implement the solution. Default to one execution owner. Use extra subagents only for hard read-only exploration or a specific review lens.
6. Run verification. Use the verify mode from `spec.md` when present; otherwise choose the lightest honest proof. Write `verification.md`.
7. Run review proportional to risk. Write `review-summary.md` only when there are real findings or non-trivial risk.
8. Compound durable lessons and update repo knowledge.
9. End with a concise status summary.

## Hard rules

- No duplicated markdown state unless it changes a decision. `spec.md` is the run card.
- Do not create placeholder docs just because a template exists.
- Do not ask the user to sequence subcommands or carry the run state for you.
- Do not claim GREEN unless changed behavior was actually proven.
- Fix the first actionable failure, not the loudest symptom.
