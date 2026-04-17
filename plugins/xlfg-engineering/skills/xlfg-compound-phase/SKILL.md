---
description: Internal xlfg phase skill. Use only during /xlfg runs to promote verified durable lessons into knowledge without copying the entire run into memory.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write
---


# xlfg-compound-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Promote only verified, reusable lessons into durable knowledge and leave the next run a better starting point.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read the highest-signal artifacts from the run:
   - `spec.md`
   - `memory-recall.md`
   - `verification.md`
   - optional `review-summary.md`, `risk.md`, `run-summary.md`
   - `docs/xlfg/knowledge/current-state.md`
   - `docs/xlfg/knowledge/*.md`
   - `docs/xlfg/knowledge/ledger.jsonl`
3. Promote only verified durable lessons into the appropriate tracked files under `docs/xlfg/knowledge/`.
4. Use `current-state.md` for repo-wide durable handoff when appropriate; keep branch-local lessons in the run when they are not yet durable.
5. Append durable events to `ledger.jsonl`.
6. Write `compound-summary.md` and, when helpful, `run-summary.md`.
7. Update any residual task/blocker notes in `workboard.md`. The `## Phase status` block (including `compound: DONE`) is rendered by the conductor from `.xlfg/phase-state.json`.

## `current-state.md` size cap (v4.3.0+)

`current-state.md` is the shortest tracked handoff for the next agent. Each run may add at most **~200 words** to it. Longer narrative, per-run decision history, and repro steps belong in the run's own `compound-summary.md` (long-form home).

Apply this cap before writing:

1. Draft the durable carry-forward as if it were a one-paragraph entry (≤ ~200 words).
2. If the draft is longer, split: keep the ≤200-word essence in `current-state.md`; move the rest to `compound-summary.md` and reference it from the ledger.
3. If two consecutive runs' drafts collide on the same section of `current-state.md`, consolidate — do not append. An ever-growing wall is a smell that the file has stopped being a handoff.

Anything beyond ~200 words of a single run's entry in `current-state.md` should be read as a signal to move text to `compound-summary.md`, not as license to grow the handoff.

## Guardrails

- Do not copy the whole run into memory.
- Do not promote lessons that were not actually verified.
- Favor small, reusable truths over vague retrospective prose.
