# Research notes behind xlfg 2.0.6

This patch is about one concrete failure mode: concurrent branches were fighting over shared knowledge files.

## 1) A harness needs a write model and a read model

The old xlfg knowledge shape was convenient for reading but bad for concurrent writing. The new shape separates:

- immutable tracked write units (cards and events)
- generated local read models (`_views/`)

That makes compounding safer under multiple worktrees.

## 2) Memory should align to the actual unit of work

Large, episode-level memory blobs are too coarse for long software workflows. xlfg keeps:

- shared cards by knowledge kind
- role-specific cards by specialist
- immutable event files with structured evidence
- local generated views for fast reading

## 3) Verification must stay linked to the requirement

`proof-map.md` still exists for the same reason as before: command success does not automatically prove the requirement.

## 4) Capability loading should stay progressive

Optional agents still load only when the diagnosis justifies them. This keeps context and runtime cost under control.

## 5) Deterministic recall stays the default

This repo still intentionally avoids vector search, HyDE, and LLM query expansion in the core path. The priority is auditability, exact provenance, and a knowledge model that stays reviewable under git.
