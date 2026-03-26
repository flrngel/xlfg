# xlfg

This folder is the **file-based context** system-of-record for `/xlfg` work.

## Structure

Tracked durable knowledge:

- `knowledge/` — current state, patterns, decisions, testing knowledge, UX flows, harness rules, role-specific memories, and an append-only memory ledger (commit this)
- `meta.json` — scaffold version + migration state (commit this)
- `migrations/` — migration notes when the xlfg version changes (commit this)

Local run evidence (do not commit by default):

- `runs/` — one folder per run containing the lean run card, proof, status, and optional deep-dive docs only when they changed a decision
- `.xlfg/runs/` — raw command outputs, screenshots, traces, doctor reports

## Why `runs/` is local-only by default

Run folders are valuable as **episodic memory** and debugging evidence, but they create high-churn git noise, often include machine-local paths and transient failures, and are usually too verbose to serve as durable knowledge. xlfg therefore keeps:

- `docs/xlfg/runs/` — **local by default** (gitignored, except placeholders)
- `docs/xlfg/knowledge/` — **tracked** and curated
- `.xlfg/` — **ephemeral** and gitignored

Promote only the reusable lesson, not the entire run.

## Merge-friendly knowledge policy

To reduce PR conflicts across concurrent worktrees and branches:

- shared knowledge files are **append-only by default**
- xlfg scaffolds `.gitattributes` rules so append-only knowledge files use Git's **union** merge driver
- `current-state.md` is treated as a **stable tracked brief**, not a hot file for every feature branch
- when a non-default branch learns something branch-local, `/xlfg:compound` should write `current-state-candidate.md` inside the run folder instead of rewriting the tracked brief

This keeps retrieval simple: read the tracked brief first for repo-wide truths, then read the latest local candidate for the current branch if one exists.

## Core workflow contract

Normal `/xlfg` runs should auto-execute recall → intent → context → plan → implement → verify → review → compound in one invocation. Minimal scaffold sync may happen silently when needed.

The lean core run files are:

1. `context.md` — request and constraints snapshot
2. `memory-recall.md` — the smallest relevant prior knowledge slice
3. `spec.md` — the **single source of truth** for the intent contract, PM / UX / Engineering / QA / Release
4. `test-contract.md` — concise practical scenario contracts with fast proof + ship proof
5. `test-readiness.md` — READY / REVISE gate for whether those scenarios are honest enough to code against
6. `workboard.md` — run-level stage + task ledger

Optional deep-dive files such as `research.md`, `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, and `risk.md` should exist only when they reduce ambiguity or risk.

## Agent memory model

xlfg compounds in two layers:

1. **`current-state.md`** as the shortest tracked handoff for the next agent
2. **Shared memory** in `knowledge/` for repo-wide rules and patterns
3. **Role memory** in `knowledge/agent-memory/` for agents that repeatedly need the same lessons
4. **Memory ledger** in `knowledge/ledger.jsonl` for append-only, structured durable memory events

Keep `current-state.md` short and current. Role memory must stay small, typed, and admission-gated. Do not dump raw run summaries there. The ledger is append-only; corrections should supersede old entries rather than silently rewriting them.
