---
description: Read-only summary of the current xlfg run's state. Safe mid-run — emits RUN_ID, current phase, latest artifact, loopback count, and next action without modifying any files.
argument-hint: "[no arguments]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash
effort: low
---

# xlfg status

Use this to orient yourself in the middle of a long `/xlfg` run — for example when a scheduled wakeup lands stale, when you're resuming a run after a context compaction, or when you just want to see where things are without re-reading every artifact.

This command is **read-only**. It reads no state it doesn't already own, writes no files, and does not mutate `.xlfg/` or `docs/xlfg/runs/`.

## What to emit

Read (in this order, skipping any that are missing) and emit a 5–8 line summary:

1. `.xlfg/phase-state.json` — `run_id`, `completed`, `phases`, `loopback_count`, `max_loopbacks`, `block_count`, `in_progress_phase`.
2. `docs/xlfg/runs/<run_id>/workboard.md` — the rendered `## Phase status` block, if present (read-only).
3. `docs/xlfg/runs/<run_id>/spec.md` — the `resolution` field and the `## Task map` if present.
4. `docs/xlfg/runs/<run_id>/verification.md` — the verdict line (GREEN / RED / none), if present.
5. The most recently modified artifact under `docs/xlfg/runs/<run_id>/` (by mtime) for "latest artifact".

## Output format

Emit exactly this shape, filling each line:

```text
RUN_ID: <run_id>
Phase: <in_progress or next incomplete phase> (loopback <loopback_count>/<max_loopbacks>)
Completed: <N>/<total> phases [<comma-separated names>]
Latest artifact: <relative path> (<mtime>)
Verification: <GREEN | RED | none>
Blocking: <blocker summary or "none">
Next action: <one concrete next step>
```

Do not re-read every phase artifact. Do not run tests. Do not modify any file. If `.xlfg/phase-state.json` does not exist, emit `no active xlfg run`.

## Staleness note

If the invoker mentions the output came from a `ScheduleWakeup` prompt, remind them that wakeup prompts are stale-by-default — the state above is authoritative; the prompt's named task IDs or diagnosis may already be superseded.
