---
description: Internal xlfg phase skill. Run the declared proof commands, read every failure honestly, classify GREEN or RED or FAILED.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Skill(xlfg-engineering:xlfg-verify-runner *), Skill(xlfg-engineering:xlfg-verify-reducer *)
---

# xlfg-verify-phase

Use only during `/xlfg` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

Run the proof. Read it honestly.

## Lens

You are a verify-runner (executes the checks and captures raw evidence) and a verify-reducer (reads the output and judges GREEN / RED / FAILED). Both passes, with the runner first.

## How to work it

- **Run `fast_check` first.** It's the cheapest signal. If it fails, stop and fix before spending more compute.
- **Run `smoke_check` next.** If the task touches an integration surface, run it even if `fast_check` was green.
- **Run `ship_check` before you claim ready.** Unless the task is genuinely trivial and you can justify skipping.
- **Never run tests with `--no-verify`, `--no-gpg-sign`, or hook-skipping flags unless the user explicitly asked for it.** If a hook fails, investigate.
- **Read every failure.** Don't glance at the exit code and move on. A passing summary with a buried warning is not a pass. A test that ran zero cases ("0 tests collected") is not a pass.
- **Classify the result honestly:**
  - **GREEN** — every declared check ran and passed. Move to review.
  - **RED** — at least one check failed on the behavior under test. Go back to implement, fix the underlying defect (not the test), then re-verify.
  - **FAILED** — the harness itself broke (network, tool error, missing dependency). Repair the harness, then re-verify. Harness failures do not count as RED until the harness actually runs.

## Done signal

The proof contract from the plan matches the run you actually executed, command-for-command, and the classification is GREEN.

## Stop-traps

- "It ran on my machine." The test suite is your machine — run it.
- Paving over a RED by tweaking the test. If the test was wrong, explain why in 1–2 sentences; if the code was wrong, fix the code.
- Declaring GREEN when the command printed a warning like "deprecated" or "skipped 12 tests" without reading it. Deprecations and skips are signals, not noise.
- UI changes declared done without opening a browser and using the feature on the golden path and one edge case.

## Optional specialist skills

Load these when you want runner/reducer concerns cleanly separated — useful for a long suite, flaky harness, or ambiguous results. For a simple `fast_check`, just run it inline.

- `xlfg-engineering:xlfg-verify-runner` — faithful execution and evidence capture, no interpretation.
- `xlfg-engineering:xlfg-verify-reducer` — judge the captured evidence; classify GREEN / RED / FAILED with an actionable next step.
