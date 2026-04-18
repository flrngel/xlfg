---
description: Internal xlfg phase skill. Resolve ambiguity in the request before broad repo fan-out; name true blockers and split bundled asks.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
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

## Stop-traps

- Treating a stylistic preference as a blocker (don't stall the run).
- Treating a correctness ambiguity as not-a-blocker because the repo has a convention you can follow (do stall — convention is not contract).
- "I'll figure it out while coding." Your plan is already wrong. Slow down here; you'll spend 10× that time later.
- Accepting the user's diagnosis as the bug. "It's a caching problem" from the user is a hypothesis, not the intent.
