# xlfg 2.0.7: simple merge-friendly knowledge

## Problem

Concurrent worktrees and feature branches were fighting over the same tracked knowledge files, especially `docs/xlfg/knowledge/current-state.md` and the shared markdown rollups.

## Goal

Reduce merge conflicts **without** changing xlfg into a heavier event-sourced knowledge system and without making retrieval harder than v2.0.5.

## Solution

1. Shared knowledge files that are naturally append-only use Git's built-in `union` merge driver.
2. Shared knowledge files should be treated as append-only. New entries supersede old ones instead of rewriting them.
3. `current-state.md` stays the stable repo-wide brief.
4. Non-default branches/worktrees write `current-state-candidate.md` inside the run folder instead of touching the tracked brief.

## Why this is enough

- The biggest hot-file conflict came from rewriting the short tracked handoff on every branch.
- The remaining knowledge files mostly want append-only behavior anyway.
- Recall already searches local runs, so branch-local handoff remains retrievable without new retrieval infrastructure.

## Read order

1. `docs/xlfg/knowledge/current-state.md`
2. latest local `docs/xlfg/runs/*/current-state-candidate.md` if present
3. shared knowledge markdown files
4. role memory
5. `ledger.jsonl`
6. other local run artifacts

## What this intentionally does not add

- no branch-scoped cards
- no generated `_views/`
- no new event store layout
- no vector retrieval

## Operational rule

If a branch-local truth becomes the new repo-wide truth, promote it deliberately on the default branch by updating `current-state.md` in a later compounding step.
