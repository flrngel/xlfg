---
description: Internal xlfg phase skill. Gather the repo and runtime facts needed for the task. Bounded reads, not whole-repo scan.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, WebSearch, WebFetch
---

# xlfg-context-phase

Use only during `/xlfg` or `/xlfg-debug` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

Gather the repo and runtime facts you actually need for the task at hand. No more, no less.

## Lens

You are a repo cartographer, a harness profiler, an environment doctor, and an adjacent-requirements hunter. Each of those is a separate mental pass, not a separate file.

## How to work it

- **Structural pass.** `LS`, `Glob`, and `Grep` to locate the surfaces you'll touch. Read entry points, then the specific files the plan will change. Do not read the whole repo.
- **Harness pass.** How are tests run here? What's in `package.json` / `pyproject.toml` / `Makefile` / `CONTEXT.md` / `CONTRIBUTING.md`? Is there a dev server? A CI config? Record the exact commands you'll use for proof later.
- **Environment pass.** What runtimes, ports, secrets, and external services does this touch? Is the dev server already running? Can you invoke it without a user on the terminal?
- **Adjacent-requirement pass.** Look for the feature you're about to copy from. If a sibling flow exists, what does it handle that the user didn't ask about — errors, edge cases, telemetry, access control? Those are implied requirements.
- **Constraint pass.** What *must* hold that isn't in the request — performance budgets, backwards compatibility, security posture, licensing, data retention? These become hard constraints on the plan.
- **Research pass (only if needed).** External docs, changelogs, or RFCs when the repo is silent and correctness depends on freshness.

## Debug-specific emphasis

For a `/xlfg-debug` run: you need the exact path from input to wrong output, not the whole module. Find the smallest reproduction that still fails, and know which files and which lines are in the suspect path. Is the repro deterministic, or is there a timing / concurrency / data-dependence dimension?

## Done signal

- For `/xlfg`: you can list the files you will read, edit, or run, and you know the exact commands that will prove the change works.
- For `/xlfg-debug`: you have the smallest reproduction that still fails, and you know exactly which files and which lines of those files are in the suspect path.

## Stop-traps

- Reading the whole repo "for context." Context has a cost; unbounded context is self-defeating. Read the surfaces your plan says you'll touch, plus one layer of callers and callees.
- Treating a README as the ground truth when the code has diverged. Always cross-check docs against code.
- Skipping the harness pass because "I'll find the test command later." If you can't state the proof command now, your plan is not real.
- For debug: reading too broadly. Context for debugging is narrower than context for building.
