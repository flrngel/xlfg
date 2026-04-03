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

- divide specialist work into atomic task packets: one clear mission in, one required artifact out
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

## Phase-state tracking

After startup, write `.xlfg/phase-state.json` with this initial state:

```json
{
  "run_id": "<RUN_ID>",
  "phases": ["recall","intent","context","plan","implement","verify","review","compound"],
  "completed": [],
  "loopback_count": 0,
  "max_loopbacks": 2,
  "block_count": 0
}
```

After each phase skill returns successfully, add that phase name to `completed` and reset `block_count` to `0`. Write the file back immediately. A Stop hook reads this file to prevent the conductor from ending before all phases are done.

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
- Keep phase-critical specialists short-lived. If a lane needs materially more time, broader scope, or multiple outputs, re-split it into smaller packets instead of letting one specialist drift.
- xlfg specialists are leaf workers. Do not ask a specialist to spawn more specialists or nested subagents; only the conductor may delegate.
- Keep fan-out small. Prefer one active specialist lane at a time for artifact-producing work; widen only for truly independent, read-mostly packets.
- Prefer the specialist artifact over the main agent's first-pass reasoning for that lane, because the specialist exists to apply a stricter expert lens, not because the main agent is incapable.

## Atomic packet format

Before dispatching any xlfg specialist, preseed the required artifact yourself and use a packet that starts with these machine-readable lines:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only
```

- Preseed the artifact at `PRIMARY_ARTIFACT` with `Status: IN_PROGRESS`, the mission, and a short remaining checklist **before** the specialist starts broad reading.
- Never wait on a specialist without a preseeded `PRIMARY_ARTIFACT` and explicit `RETURN_CONTRACT`; file-backed artifact progress is the only accepted basis for waiting.
- Pass objective context, not just the literal query. Include the exact ask, why it matters, and any nearby constraints that change correctness.
- Default to sequential specialist dispatch for artifact-producing planning/context lanes. Parallelize only when packets are truly independent, small, and read-mostly.

## Specialist completion barrier

- Every specialist dispatch must be an **atomic packet** with one mission, one primary output artifact, one file scope, and one honest done check.
- Do not accept chat-only progress updates as completion. “I'm going to …”, “here is my plan …”, or “I prepared the context …” all count as **INCOMPLETE** until the promised artifact exists and the scoped work is actually done.
- A specialist lane is complete only when the required artifact exists, starts with `Status: DONE` or `Status: BLOCKED` or `Status: FAILED`, and contains concrete edits, findings, checks, logs, or cited facts.
- If a specialist returns early without the artifact or only with setup notes, resume the **same specialist** with `SendMessage` using its returned agent ID so it continues from prior state instead of starting over. If no agent ID is available or resume is unavailable, re-dispatch the exact same packet once.
- Only after a second incomplete return should you mark the specialist lane failed, re-split the task, or repair the gap yourself. Do not bypass the specialist after the first incomplete return.
- If a task packet spans multiple unrelated outputs, split it before delegation rather than hoping one specialist will self-scope perfectly.

## Internal loop rules

- Do **not** broad-scan the repo or spawn wide research until `xlfg-engineering:xlfg-intent-phase` has written the intent contract and objective groups in `spec.md`.
- If the intent phase marks `resolution: needs-user-answer`, stop and ask at most three concise numbered blocking questions. Do not continue to context, planning, or coding until the answer arrives.
- If `test-readiness.md` is not `READY` after planning, return to `xlfg-engineering:xlfg-context-phase` and `xlfg-engineering:xlfg-plan-phase` yourself until the plan is repaired or a true human-only blocker is explicit.
- If verification is RED with an actionable fix, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun `xlfg-engineering:xlfg-verify-phase`. Increment `loopback_count` in `.xlfg/phase-state.json` each time. **Max 2 loopbacks** — after 2 verify-fix cycles, stop and escalate to the user with a summary of what failed and why.
- If review finds a must-fix issue, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun verify and review. This also counts toward the loopback limit.
- Do not hand this loop back to the user unless the loopback cap is reached.

## Completion

Finish with a concise status summary that includes `RUN_ID`, what changed, proof status, residual risk, objective completion status, and follow-ups if any.
