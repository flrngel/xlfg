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
7. Update `workboard.md` so `compound` is `DONE`.

## Guardrails

- Do not copy the whole run into memory.
- Do not promote lessons that were not actually verified.
- Favor small, reusable truths over vague retrospective prose.
