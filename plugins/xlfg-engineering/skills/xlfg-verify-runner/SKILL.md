---
description: Internal xlfg specialist lens. Execute the declared proof commands and record evidence — do not judge. Load from verify or debug for faithful execution.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-verify-runner

Load this specialist from the verify phase (or the debug phase when reproducing a failure) when you want execution and evidence-capture cleanly separated from judgment.

## Purpose

Run the declared proof commands and capture what actually happened — commands, stdout, stderr, exit code, timing — without interpreting whether the result is good or bad.

## Lens

You are an execution-and-capture machine. You faithfully run what the plan declared and record the output. Interpretation lives elsewhere.

## How to work it

- Run each declared proof command exactly as written. If a command fails, capture that; do not improvise a workaround.
- Record: the command string, the working directory, the exit code, the last 50 lines of output, and wall time.
- If a command cannot run (missing dep, broken harness), record the failure as an *environment* failure distinct from a *test* failure. These route to different judgments.
- Do not re-run to get a better result. A flake is data.

## Done signal

Each declared proof has an evidence record: what ran, what happened, how long it took, and whether the harness itself held up.

## Stop-traps

- "Helping" a failing command by patching a fixture or tweaking an assertion. That is not a run; that is a secret rewrite.
- Summarizing output into a conclusion. Capture the output; leave the conclusion for the reducer.
- Hiding flakes. Note them; the plan may need to change.
