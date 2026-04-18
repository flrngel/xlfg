---
description: Internal xlfg specialist lens. Characterize the project's test harness — runner, commands, fixture patterns, rough cost. Load from context before declaring fast/smoke/ship proof.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-harness-profiler

Load this specialist from the context phase when you don't yet know the exact proof commands you'll run, or when the repo has more than one test runner and you need to pick the right lane.

## Purpose

Know precisely how proof is produced in this repo: which command, how long, what skips by default, where fixtures live.

## Lens

You are the engineer who has to declare `fast_check`, `smoke_check`, and `ship_check` honestly — and to do that, you need numbers, not adjectives.

## How to work it

- Find the canonical test command. `package.json` scripts, `pytest.ini`, `Makefile`, CI workflow. If two places disagree, CI is usually the ground truth.
- Distinguish the tiers that exist: unit vs. integration vs. e2e; fast vs. full; sandboxed vs. hits-network.
- Time one run of the smallest unit suite if practical. Seconds matter for `fast_check`.
- Note what's *missing* from the harness: no e2e at all? no CI lint? That changes which tier a given claim needs.
- Record the exact commands the plan phase will cite verbatim.

## Done signal

You can name the three proof commands (`fast_check`, `smoke_check`, `ship_check`) as strings the plan phase can paste into its test contract, with a ballpark runtime for each.

## Stop-traps

- "We'll figure out the test command during verify." No — verify needs a declared contract to test against.
- Picking the slowest command as the default. Fast lane first, broader lanes only when the change surface requires.
- Ignoring what the harness cannot test. If there's no integration lane and you need one, the plan must say so, not pretend.
