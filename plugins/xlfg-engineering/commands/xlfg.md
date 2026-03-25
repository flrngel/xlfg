---
name: xlfg
description: Autonomous xlfg SDLC run. Batches hidden recall, context, plan, implement, verify, review, and compound skills end-to-end.
argument-hint: "[feature, bugfix, investigation, or delivery request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, WebSearch, WebFetch, Skill(xlfg-engineering:xlfg-recall-phase *), Skill(xlfg-engineering:xlfg-context-phase *), Skill(xlfg-engineering:xlfg-plan-phase *), Skill(xlfg-engineering:xlfg-implement-phase *), Skill(xlfg-engineering:xlfg-verify-phase *), Skill(xlfg-engineering:xlfg-review-phase *), Skill(xlfg-engineering:xlfg-compound-phase *)
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

`/xlfg` is the conductor for a **batch of hidden phase skills**. Load only the current phase skill, execute it, then move to the next one. Do not inline the whole workflow from memory and do not ask the user to run internal skills or phase commands.

## Run contract

- keep `spec.md` as the single source of truth for request truth, chosen solution, task map, proof status, and PM / UX / Engineering / QA / Release notes
- create optional docs only when they change a decision, proof obligation, or durable lesson
- do not stop for internal phase approvals
- ask the user only for true human-only blockers: missing secrets, destructive external approvals, or correctness-changing product ambiguity you cannot ground from the repo or current research
- prefer repo truth first, then targeted web research when freshness matters or the repo is insufficient
- prefer the local `xlfg` helper CLI when available

## Startup

1. Quietly sync scaffold if missing or stale with `xlfg init` (or `xlfg prepare`) when the helper exists; otherwise perform the equivalent bootstrap manually.
2. Create `RUN_ID` with `xlfg start "$ARGUMENTS"` when the helper exists; otherwise create the lean core run manually.
3. Resolve `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>` and `DX_RUN_DIR=.xlfg/runs/<RUN_ID>`.

## Batch skill pipeline

Invoke these hidden skills in this exact order, always passing `RUN_ID`:

1. `xlfg-engineering:xlfg-recall-phase`
2. `xlfg-engineering:xlfg-context-phase`
3. `xlfg-engineering:xlfg-plan-phase`
4. `xlfg-engineering:xlfg-implement-phase`
5. `xlfg-engineering:xlfg-verify-phase`
6. `xlfg-engineering:xlfg-review-phase`
7. `xlfg-engineering:xlfg-compound-phase`

Use the `Skill` tool to load each phase just-in-time instead of carrying all phase instructions in the entrypoint.

## Internal loop rules

- If `test-readiness.md` is not `READY` after planning, return to `xlfg-engineering:xlfg-context-phase` and `xlfg-engineering:xlfg-plan-phase` yourself until the plan is repaired or a true human-only blocker is explicit.
- If verification is RED with an actionable fix, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun `xlfg-engineering:xlfg-verify-phase`.
- If review finds a must-fix issue, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun verify and review.
- Do not hand this loop back to the user.

## Completion

Finish with a concise status summary that includes `RUN_ID`, what changed, proof status, residual risk, and follow-ups if any.
