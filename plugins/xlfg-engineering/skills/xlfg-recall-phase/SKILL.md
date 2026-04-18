---
description: Internal xlfg phase skill. Deterministic recall over git history, the xlfg durable archive, and lexical repo scan — before broad fan-out.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-recall-phase

Use only during `/xlfg` or `/xlfg-debug` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

Before you scan the repo broadly, ask: *has this problem, or something adjacent, been solved before — in this repo's history, in prior xlfg runs, or in the project's distilled memory?*

## Lens

You are a librarian. Git history, existing code, and the project's tracked `docs/xlfg/` layer are your index.

## How to work it

- **xlfg durable memory first.** If `docs/xlfg/current-state.md` exists, read it first. It's the prior authors' distilled load-bearing truths about this project — what it is, active constraints, known traps. This is short by design; read it in full.
- **Prior runs.** List `docs/xlfg/runs/` (if present) and read the 2–3 most recent `run-summary.md` or `diagnosis.md` files that touch the surface you're about to work on. A run summary from last week that names your exact surface is gold; ignore unrelated ones.
- **Git history.** If the user's request names a specific surface, `git log -- <path>` and `git log --grep=<term>` for recent related commits. Read their messages, not their diffs yet.
- **Lexical repo recall.** `Grep` the codebase for the domain terms in the request — not code, but concepts ("rate limit", "webhook retry", "migration rollback"). Existing patterns are better than new inventions.
- **Root-level orientation.** If there is a CLAUDE.md, AGENTS.md, or README at the repo root, read it. Those exist for you.

## Done signal

You can name, in one sentence, the closest prior work to what's being asked and whether it's a pattern to extend or a trap to avoid. You also know whether `current-state.md` exists; if it does, every assumption you make in later phases should be consistent with it (or consciously supersede it).

## Stop-traps

- Skipping to code because "I already know how this works." You don't. The repo has opinions you haven't loaded yet.
- Treating prior work as authoritative without checking whether the code under it has moved since. If the last commit on the target surface is newer than the pattern you're about to reuse, the pattern may be stale.
- Reading 10 prior run summaries "to be thorough." Read the 2–3 that match your surface and stop.
