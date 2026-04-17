---
name: xlfg
description: Autonomous xlfg SDLC run. Batches hidden recall, intent, context, plan, implement, verify, review, and compound skills end-to-end.
argument-hint: "[feature, bugfix, investigation, or delivery request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, WebSearch, WebFetch, TaskCreate, TaskUpdate, TaskList, Skill(xlfg-engineering:xlfg-recall-phase *), Skill(xlfg-engineering:xlfg-intent-phase *), Skill(xlfg-engineering:xlfg-context-phase *), Skill(xlfg-engineering:xlfg-plan-phase *), Skill(xlfg-engineering:xlfg-implement-phase *), Skill(xlfg-engineering:xlfg-verify-phase *), Skill(xlfg-engineering:xlfg-review-phase *), Skill(xlfg-engineering:xlfg-compound-phase *)
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
- for bundled or messy requests, split the work into stable objective groups (`O1`, `O2`, ...) before broad repo fan-out

## Startup

1. Sync scaffold if missing or stale: ensure `docs/xlfg/runs/`, `.xlfg/runs/`, `docs/xlfg/knowledge/`, and `.xlfg/` directories exist; create any missing ones. In the same shell step, run `rm -f .xlfg/phase-state.json` to clear any stale file left by a prior run — otherwise the fresh Write in "Phase-state tracking" below will fail with `File has not been read yet. Read it first before writing to it.` because Claude Code's Write tool refuses to overwrite an existing file the session has never read.
2. Create `RUN_ID` as `<YYYYMMDD>-<HHMMSS>-<slug>` where `<slug>` is a short kebab-case summary of `$ARGUMENTS`; write the lean core run directories and `spec.md` skeleton manually.
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
  "block_count": 0,
  "in_progress_phase": ""
}
```

After each phase skill returns successfully, add that phase name to `completed` and reset `block_count` to `0`. Write the file back immediately. A Stop hook reads this file to prevent the conductor from ending before all phases are done.

### `in_progress_phase` contract (v4.3.0+)

Before calling any phase `Skill`, set `in_progress_phase` to that phase name (`"recall"`, `"intent"`, ..., `"compound"`). After the Skill returns, clear it to `""` (empty string) before moving to the next phase. While `in_progress_phase` is non-empty, the Stop hook exits silently — a long foreground phase that parks the conversation waiting on a background task or a sub-packet notification does not accumulate blocks or trip the safety valve.

The hook never resets `completed`, `loopback_count`, or `in_progress_phase`. It only mutates `block_count` (and only when `in_progress_phase` is empty).

Then run `node ${CLAUDE_PLUGIN_ROOT}/scripts/render-workboard.mjs` to refresh the `## Phase status` block in `docs/xlfg/runs/<RUN_ID>/workboard.md` from the just-updated `phase-state.json`. Phase skills MUST NOT hand-write phase completion rows into `workboard.md` — the renderer owns that section, bounded by `<!-- BEGIN: rendered-phase-status -->` / `<!-- END: rendered-phase-status -->` markers. Phase skills still own the task, objective, and blocker sections of the same file.

## Harness task bridge

Immediately after writing the initial `phase-state.json`, emit one synthetic harness task per phase via `TaskCreate` so the Claude Code task pane reflects the same phase list as xlfg's file-based workboard. Use these exact subjects (matching the phase names):

- `xlfg: recall`
- `xlfg: intent`
- `xlfg: context`
- `xlfg: plan`
- `xlfg: implement`
- `xlfg: verify`
- `xlfg: review`
- `xlfg: compound`

As each phase completes (same moment you append to `completed` in `phase-state.json`), call `TaskUpdate` to mark the corresponding task `completed`. This keeps the harness's native task pane honest without phase skills double-writing phase state. Do not create harness tasks for specialists, sub-packets, or loopbacks — only the top-level phase list. The file-based `workboard.md` remains the authoritative per-phase artifact; the harness tasks are a thin bridge.

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

### Phase boundary timings

Bracket every phase Skill call with two `phase-tick` invocations so the post-mortem (`/xlfg-audit`) can compute per-phase wall time honestly, including loopbacks. Both ticks are best-effort — a write failure in `phase-tick.mjs` exits 0 and never blocks the conductor.

Before the Skill call:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/phase-tick.mjs" --run "<RUN_ID>" --phase <phase> --event start
```

After the Skill returns (whether DONE, BLOCKED, or FAILED):

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/phase-tick.mjs" --run "<RUN_ID>" --phase <phase> --event end
```

If a phase loops back, emit a fresh `start`/`end` pair for the re-run — the post-mortem sums across invocations.

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
ARTIFACT_KIND: planning-doc | source-file | config-file | test-file   # optional; default planning-doc
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only

CONTEXT_DIGEST:
- <quoted excerpt or bullet from spec.md / context.md / verification.md / prior phase output>

PRIOR_SIBLINGS:
- <path/to/sibling-artifact.md>: <one-line summary of what it already covered>
```

- `ARTIFACT_KIND` is optional. Omit it for markdown planning docs (the default). Set it explicitly when `PRIMARY_ARTIFACT` points at application source, config, or tests — prepending YAML frontmatter to those file types breaks them at parse time.
- `CONTEXT_DIGEST` and `PRIOR_SIBLINGS` are **mandatory**. They exist to stop sibling specialists from re-reading the same canonical files and re-deriving the same findings. See `agents/_shared/output-template.md` for the canonical shape and rules. Use `CONTEXT_DIGEST: see PRIMARY_ARTIFACT preseed` and `PRIOR_SIBLINGS: none` only when literally true.
- Preseed **planning-doc** artifacts at `PRIMARY_ARTIFACT` with YAML frontmatter `status: IN_PROGRESS`, the mission, and a short remaining checklist **before** the specialist starts broad reading.
- For **source-file / config-file / test-file** artifacts, do not preseed with YAML frontmatter. Either leave the target file as it is on disk (the specialist edits in place) or create it with a valid empty shape in the target language. The specialist reports lifecycle through the `RETURN_CONTRACT` line only.
- Never wait on a specialist without a preseeded `PRIMARY_ARTIFACT` and explicit `RETURN_CONTRACT`; file-backed artifact progress is the only accepted basis for waiting.
- Pass objective context, not just the literal query. Include the exact ask, why it matters, and any nearby constraints that change correctness.
- Default to sequential specialist dispatch for artifact-producing planning/context lanes. Parallelize only when packets are truly independent, small, and read-mostly.

## Specialist completion barrier

- Every specialist dispatch must be an **atomic packet** with one mission, one primary output artifact, one file scope, and one honest done check.
- Do not accept chat-only progress updates as completion. “I'm going to …”, “here is my plan …”, or “I prepared the context …” all count as **INCOMPLETE** until the promised artifact exists and the scoped work is actually done.
- A specialist lane is complete only when the required artifact exists, carries YAML frontmatter `status: DONE`, `status: BLOCKED`, or `status: FAILED`, and contains concrete edits, findings, checks, logs, or cited facts.
- If a specialist returns early without the artifact or only with setup notes, resume the **same specialist** with `SendMessage` using its returned agent ID so it continues from prior state instead of starting over. If no agent ID is available or resume is unavailable, re-dispatch the exact same packet once.
- Only after a second incomplete return should you mark the specialist lane failed, re-split the task, or repair the gap yourself. Do not bypass the specialist after the first incomplete return.
- If a task packet spans multiple unrelated outputs, split it before delegation rather than hoping one specialist will self-scope perfectly.

## Internal loop rules

- Do **not** broad-scan the repo or spawn wide research until `xlfg-engineering:xlfg-intent-phase` has written the intent contract and objective groups in `spec.md`.
- If the intent phase marks `resolution: needs-user-answer`, stop and ask at most three concise numbered blocking questions. Do not continue to context, planning, or coding until the answer arrives.
- If `test-readiness.md` is not `READY` after planning, return to `xlfg-engineering:xlfg-context-phase` and `xlfg-engineering:xlfg-plan-phase` yourself until the plan is repaired or a true human-only blocker is explicit.
- If verification is RED with an actionable fix, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun `xlfg-engineering:xlfg-verify-phase`. Increment `loopback_count` in `.xlfg/phase-state.json` each time. **Max 2 loopbacks** — after 2 loopbacks, stop and escalate to the user with a summary of what failed and why.
- If review finds a must-fix issue, go back to `xlfg-engineering:xlfg-implement-phase`, then rerun verify and review. This also counts toward the loopback limit.
- Do not hand this loop back to the user unless the loopback cap is reached.

### `loopback_count` arithmetic (v4.3.0+)

`loopback_count` counts `{verify|review} → implement` round trips that require a fresh implement pass. Explicit rules:

- **Counts as +1**: verify RED → implement → verify. A fresh implement pass was required.
- **Counts as +1**: review MUST-FIX → implement → verify → review. Same shape; the trigger is review, not verify.
- **Counts as +1 (single)**: verify exposes a fundamentally different diagnosis that requires `verify → plan → implement → verify`. This is one loopback (the replan happens inside the cycle, not a separate one), but it is real — do not free-ride the replan.
- **Does NOT count**: plan-phase repair after `test-readiness.md` returns `REVISE`. The conductor repairs the plan in place; no implement pass ran yet. Repairs are unlimited within the plan phase.
- **Does NOT count**: `APPROVE-WITH-NOTES-FIXED` review disposition (see `xlfg-review-phase`). A ~10-second inline fix with a re-run of the deterministic proof subset does not consume a loopback.
- **Does NOT count**: verify-phase internal retries when a harness failure (e.g. network, tool error) is classified FAILED (not RED). Retry the harness before counting.

When in doubt, count it. Under-counting hides run-away replanning under a polite name; over-counting just escalates earlier, which is the safer failure mode.

## Completion

Finish with a concise status summary that includes `RUN_ID`, what changed, proof status, residual risk, objective completion status, and follow-ups if any.
