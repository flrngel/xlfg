---
name: xlfg
description: Autonomous xlfg SDLC run. Batches hidden recall, intent, context, plan, implement, verify, review, and compound skills end-to-end.
argument-hint: "[feature, bugfix, investigation, or delivery request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, WebSearch, WebFetch, Skill(xlfg-engineering:xlfg-recall-phase *), Skill(xlfg-engineering:xlfg-intent-phase *), Skill(xlfg-engineering:xlfg-context-phase *), Skill(xlfg-engineering:xlfg-plan-phase *), Skill(xlfg-engineering:xlfg-implement-phase *), Skill(xlfg-engineering:xlfg-verify-phase *), Skill(xlfg-engineering:xlfg-review-phase *), Skill(xlfg-engineering:xlfg-compound-phase *)
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

- keep `spec.md` as the single source of truth for intent, chosen solution, task map, proof status, and PM / UX / Engineering / QA / Release notes
- do **not** recreate a separate intent file; the intent contract now lives inside `spec.md`
- create optional docs only when they change a decision, proof obligation, or durable lesson
- do not stop for internal phase approvals
- treat designated specialists as lane owners whose artifacts should drive synthesis, not optional advisors the main agent can casually ignore
- ask the user only for true human-only blockers: missing secrets, destructive external approvals, or correctness-changing product ambiguity you cannot ground from the repo or current research
- prefer repo truth first, then targeted web research when freshness matters or the repo is insufficient
- prefer the local `xlfg` helper CLI when available
- for bundled or messy requests, split the work into stable objective groups (`O1`, `O2`, ...) before broad repo fan-out

## Startup

1. Quietly sync scaffold if missing or stale with `xlfg init` (or `xlfg prepare`) when the helper exists; otherwise perform the equivalent bootstrap manually.
2. Create `RUN_ID` with `xlfg start "$ARGUMENTS"` when the helper exists; otherwise create the lean core run manually.
3. Resolve `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>` and `DX_RUN_DIR=.xlfg/runs/<RUN_ID>`.

## Batch skill pipeline

Invoke these hidden skills in this exact order, always passing `RUN_ID`:

1. `xlfg-engineering:xlfg-recall-phase`
2. `xlfg-engineering:xlfg-intent-phase`
3. `xlfg-engineering:xlfg-context-phase`
4. `xlfg-engineering:xlfg-plan-phase`
5. `xlfg-engineering:xlfg-implement-phase`
6. `xlfg-engineering:xlfg-verify-phase`
7. `xlfg-engineering:xlfg-review-phase`
8. `xlfg-engineering:xlfg-compound-phase`

Use the `Skill` tool to load each phase just-in-time instead of carrying all phase instructions in the entrypoint.

## Specialist execution rule

- Keep xlfg specialists in the foreground; do not rely on background execution for phase-critical work. Recent platform issues have included sync problems, silent write failures, and broken background subagent transport.
- If a designated specialist returns only preparation notes or fails to produce its required artifact, treat that as incomplete work. Retry once or record the specialist failure before repairing the gap yourself.
- Prefer the specialist artifact over the main agent's first-pass reasoning for that lane, because the specialist exists to apply a stricter expert lens, not because the main agent is incapable.

## Internal loop rules

- Do **not** broad-scan the repo or spawn wide research until `xlfg-engineering:xlfg-intent-phase` has written the intent contract and objective groups in `spec.md`.
- If the intent phase marks `resolution: needs-user-answer`, stop and ask at most three concise numbered blocking questions. Do not continue to context, planning, or coding until the answer arrives.
- If `test-readiness.md` is not `READY` after planning, return to `xlfg-engineering:xlfg-context-phase` and `xlfg-engineering:xlfg-plan-phase` yourself until the plan is repaired or a true human-only blocker is explicit.
- If verification is RED with an actionable fix, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun `xlfg-engineering:xlfg-verify-phase`.
- If review finds a must-fix issue, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun verify and review.
- Do not hand this loop back to the user.

## Completion

Finish with a concise status summary that includes `RUN_ID`, what changed, proof status, residual risk, objective completion status, and follow-ups if any.
