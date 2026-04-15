---
description: Internal xlfg phase skill. Use only during /xlfg runs to perform deterministic recall and record the smallest relevant carry-forward memory.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write
---


# xlfg-recall-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Perform deterministic recall before broad repo scanning and record only the smallest relevant carry-forward context.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read in this order when present:
   - `docs/xlfg/knowledge/current-state.md`
   - the latest related run if you are continuing work
   - `docs/xlfg/knowledge/*.md`
   - `docs/xlfg/knowledge/agent-memory/*.md`
   - `docs/xlfg/knowledge/ledger.jsonl`
3. Perform deterministic recall using Read and Grep:
   - Read `docs/xlfg/knowledge/current-state.md` and related run `spec.md` first
   - Use `Grep` with exact lexical terms (role, stage, kind, scope filters) over `docs/xlfg/knowledge/`
   - Use temporal filters by scanning ledger.jsonl or recent run dirs when the query is date-scoped
4. Write `memory-recall.md` with:
   - sources checked
   - strong matches
   - carry-forward rules for this run
   - rejected near-matches
   - an explicit no-hit statement when nothing relevant applies
5. Update `spec.md` so the recall summary is visible in the single source of truth.
6. Update the task/objective/next-action sections of `workboard.md` if needed. The `## Phase status` block (including `recall: DONE`) is rendered by the conductor via `render-workboard.mjs` after the phase returns — do not hand-write phase completion rows.

## Guardrails

- Do not write vague history dumps.
- Do not invent semantic recall when lexical evidence is weak.
- Keep the memory note compact enough to help the next phase immediately.
