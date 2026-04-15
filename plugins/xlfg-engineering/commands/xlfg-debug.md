---
name: xlfg-debug
description: Autonomous xlfg diagnosis run. Batches hidden recall, intent, context, and debug skills to find the deep root problem without changing source code.
argument-hint: "[bug report, prompt failure, misleading behavior, or diagnosis request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, WebSearch, WebFetch, Skill(xlfg-engineering:xlfg-recall-phase *), Skill(xlfg-engineering:xlfg-intent-phase *), Skill(xlfg-engineering:xlfg-context-phase *), Skill(xlfg-engineering:xlfg-debug-phase *)
effort: high
hooks:
  PermissionRequest:
    - matcher: "ExitPlanMode"
      hooks:
        - type: command
          command: >
            echo '{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}'
---

Use this when the user wants a serious debugging run that finds the **deep root problem** without editing the product.

INPUT: `$ARGUMENTS`

Treat this invocation as **one autonomous run**.

`/xlfg-debug` is the conductor for a **batch of hidden phase skills**. Load only the current phase skill, execute it, then move to the next one. Do not inline the whole workflow from memory and do not ask the user to run internal skills or phase commands.

## Run contract

- diagnose before repair; explain the mechanism before suggesting the likely repair surface
- keep `spec.md` as the **single source of truth** for intent, why, diagnosis, likely repair surface, proof status, and open questions
- do **not** change original source code, tests, fixtures, migrations, or configs that affect product behavior; only write run artifacts, evidence logs, or scratch notes under `docs/xlfg/runs/<RUN_ID>` and `.xlfg/runs/<RUN_ID>`
- reject gimmicks and shallow wins: muting errors, widening retries or timeouts, changing tests to green, hand-waving “env issue”, special-casing one prompt example, or declaring success from one happy path while the causal chain is still unknown
- prefer the **smallest honest reproduction**, then simplify, compare passing vs failing cases, trace the first wrong state, and keep a falsifiable hypothesis log
- for prompt or agent debugging, treat the prompt, tool contract, context inputs, evaluation bar, and false-success trap as part of the system under test
- prefer repo truth first, then targeted web research when freshness matters or the repo is insufficient
- for bundled or messy debug asks, split the work into stable objective groups (`O1`, `O2`, ...) before broad repo fan-out

## Startup

1. Sync scaffold if missing or stale: ensure `docs/xlfg/runs/`, `.xlfg/runs/`, `docs/xlfg/knowledge/`, and `.xlfg/` directories exist; create any missing ones.
2. Create `RUN_ID` as `<YYYYMMDD>-<HHMMSS>-<slug>` where `<slug>` is a short kebab-case summary of `$ARGUMENTS`; write the lean core run directories and `spec.md` skeleton manually.
3. Resolve `DOCS_RUN_DIR=docs/xlfg/runs/<RUN_ID>` and `DX_RUN_DIR=.xlfg/runs/<RUN_ID>`.

## Phase-state tracking

After startup, write `.xlfg/phase-state.json` with this initial state:

```json
{
  "run_id": "<RUN_ID>",
  "phases": ["recall","intent","context","debug"],
  "completed": [],
  "loopback_count": 0,
  "max_loopbacks": 1,
  "block_count": 0
}
```

After each phase skill returns successfully, add that phase name to `completed` and reset `block_count` to `0`. Write the file back immediately. A Stop hook reads this file to prevent the conductor from ending before all phases are done.

## Batch skill pipeline

Invoke these hidden skills in this exact order, always passing `RUN_ID`:

1. `xlfg-engineering:xlfg-recall-phase`
2. `xlfg-engineering:xlfg-intent-phase`
3. `xlfg-engineering:xlfg-context-phase`
4. `xlfg-engineering:xlfg-debug-phase`

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

- Preseed the artifact at `PRIMARY_ARTIFACT` with YAML frontmatter `status: IN_PROGRESS`, the mission, and a short remaining checklist **before** the specialist starts broad reading.
- Never wait on a specialist without a preseeded `PRIMARY_ARTIFACT` and explicit `RETURN_CONTRACT`; file-backed artifact progress is the only accepted basis for waiting.
- Pass objective context, not just the literal query. Include the exact ask, why it matters, and any nearby constraints that change correctness.
- Default to sequential specialist dispatch for artifact-producing diagnosis lanes. Parallelize only when packets are truly independent, small, and read-mostly.

## Specialist completion barrier

- Every specialist dispatch must be an **atomic packet** with one mission, one primary output artifact, one file scope, and one honest done check.
- Do not accept chat-only progress updates as completion. “I'm going to …”, “here is my plan …”, or “I prepared the context …” all count as **INCOMPLETE** until the promised artifact exists and the scoped work is actually done.
- A specialist lane is complete only when the required artifact exists, carries YAML frontmatter `status: DONE`, `status: BLOCKED`, or `status: FAILED`, and contains concrete edits, findings, checks, logs, or cited facts.
- If a specialist returns early without the artifact or only with setup notes, resume the **same specialist** with `SendMessage` using its returned agent ID so it continues from prior state instead of starting over. If no agent ID is available or resume is unavailable, re-dispatch the exact same packet once.
- Only after a second incomplete return should you mark the specialist lane failed, re-split the task, or repair the gap yourself. Do not bypass the specialist after the first incomplete return.
- If a task packet spans multiple unrelated outputs, split it before delegation rather than hoping one specialist will self-scope perfectly.

## Internal loop rules

- Do **not** broad-scan the repo or spawn wide research until `xlfg-engineering:xlfg-intent-phase` has written the intent contract and objective groups in `spec.md`.
- If the intent phase marks `resolution: needs-user-answer`, stop and ask at most three concise numbered blocking questions. Do not continue to context or debugging until the answer arrives.
- If the debug phase lands on a promising explanation but the evidence is still too weak because a smaller reproducer, cleaner log slice, or tighter repo boundary is missing, return to `xlfg-engineering:xlfg-context-phase`, then rerun `xlfg-engineering:xlfg-debug-phase`. Increment `loopback_count` in `.xlfg/phase-state.json` each time. **Max 1 loopback** — after 1 re-context cycle, stop and surface the exact missing evidence.
- Do not move into code changes inside `/xlfg-debug`. When repair ideas appear, capture them only as the **likely repair surface**.

## Completion

Finish with a concise status summary that includes `RUN_ID`, the deep root problem, strongest evidence, likely repair surface, fake fixes rejected, the no-code-change guarantee, residual unknowns, and the next safest proof step.
