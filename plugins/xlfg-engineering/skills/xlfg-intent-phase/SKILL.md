---
description: Internal xlfg phase skill. Resolve ambiguity in the request before broad repo fan-out; name true blockers and split bundled asks.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Skill(xlfg-engineering:xlfg-why-analyst *), Skill(xlfg-engineering:xlfg-query-refiner *), Skill(xlfg-engineering:xlfg-spec-author *), Skill(xlfg-engineering:xlfg-brainstorm *)
---

# xlfg-intent-phase

Use only during `/xlfg` or `/xlfg-debug` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

Resolve ambiguity in the request before you touch the repo broadly. The most expensive mistake in an SDLC run is building the wrong thing fast.

## Lens

You are a product manager and a why-analyst. Separate what the user typed from what they actually need.

## How to work it

- Restate the ask in your own words, at most three sentences. Name the operator, the surface, and the success condition.
- List the smallest safe assumptions you are making — anything you would refuse to invent without confirmation. Name **at most three** true blockers. If you find more than three, you're inventing ambiguity.
- If the request bundles multiple unrelated asks, split them into objective groups (`O1`, `O2`, …) and solve them one at a time. Tell the user the split before you start.
- Ask the user ONLY if a blocker would change correctness. "What color should the button be?" is not a blocker; "Should the webhook retry on 5xx or only on network error?" is.
- For a `/xlfg-debug` run, restate specifically: the input, the expected behavior, the observed behavior, and the boundary where the observation was made (log line? UI render? test assertion? alert?). The diagnosis fails if you accept the user's theory as the failure; your job is to name the mechanism.

## Done signal

- For `/xlfg`: you can state the contract of what you're about to do in 3–6 bullet points, and each bullet is falsifiable (either satisfied or not).
- For `/xlfg-debug`: you can state the bug as a one-paragraph falsifiable claim: *"when condition X, the system should Y, but actually does Z, observed at boundary B."*

This is a handoff cue to the conductor, not an end-of-run marker. After stating the contract (or the falsifiable bug claim), the conductor's very next action is dispatching the context phase — not pausing or summarizing for the user.

## Stop-traps

- Treating a stylistic preference as a blocker (don't stall the run).
- Treating a correctness ambiguity as not-a-blocker because the repo has a convention you can follow (do stall — convention is not contract).
- "I'll figure it out while coding." Your plan is already wrong. Slow down here; you'll spend 10× that time later.
- Accepting the user's diagnosis as the bug. "It's a caching problem" from the user is a hypothesis, not the intent.

## Optional specialist skills

These hidden lens skills are loadable on-demand via the `Skill` tool when the intent pass needs one specifically. Load none for simple asks; load one or two when the ambiguity warrants it. Do not batch-load all four.

- `xlfg-engineering:xlfg-why-analyst` — when the ask feels surface-level and the *outcome* behind it is still unclear.
- `xlfg-engineering:xlfg-query-refiner` — when the operator/surface/success condition is ambiguous or the ask bundles multiple objectives.
- `xlfg-engineering:xlfg-spec-author` — when the change is non-trivial and the behavioral contract is worth writing out before planning.
- `xlfg-engineering:xlfg-brainstorm` — when one approach has come to mind and you want to pressure-test it against alternatives first.
