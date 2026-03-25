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
3. Prefer the helper when available:
   - `xlfg recall yesterday`
   - `xlfg recall '<quoted lexical query>'`
   - typed lexical recall when the failure or flow is known
4. Write `memory-recall.md` with:
   - sources checked
   - strong matches
   - carry-forward rules for this run
   - rejected near-matches
   - an explicit no-hit statement when nothing relevant applies
5. Update `spec.md` so the recall summary is visible in the single source of truth.
6. Update `workboard.md` so `recall` is `DONE` and planning is the next active step.

## Guardrails

- Do not write vague history dumps.
- Do not invent semantic recall when lexical evidence is weak.
- Keep the memory note compact enough to help the next phase immediately.
