---
description: Internal xlfg phase skill. Use only during /xlfg runs to perform deterministic recall and record the smallest relevant carry-forward memory.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write
status: DONE
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
6. Update the task/objective/next-action sections of `workboard.md` if needed. The `## Phase status` block (including `recall: DONE`) is rendered by the conductor via `render_workboard.py` after the phase returns — do not hand-write phase completion rows.

## Guardrails

- Do not write vague history dumps.
- Do not invent semantic recall when lexical evidence is weak.
- Keep the memory note compact enough to help the next phase immediately.

## Git-recency guard (mandatory when promoting a prior fix class)

When you promote a carry-forward rule from a prior STABLE run, you MUST run a git-recency check against the diagnosed surface before recording the rule. This catches cases where the baseline's fix class is stale — the code that baseline covered has moved under it, so the new regression looks the same from the symptom angle but has a different root cause.

Required steps:

1. Identify the cited prior run's date and the list of files the carry-forward rule names.
2. Run: `git log --since=<baseline-date> -- <file1> <file2> ...`. Record the exact command and the result inside `memory-recall.md` (even an empty result — record that the window was checked).
3. If the result is empty, record the rule as normal carry-forward.
4. If the result contains ANY commit in the window:
   - Mark the rule as `HYPOTHESIS-ONLY` in `memory-recall.md`.
   - Add a `Verify-before-use:` line telling the plan phase to re-diagnose from the current code before treating the rule as established.
   - Do not let intent / context / plan phases silently adopt the hypothesis as an accepted root cause.

The cost is ~1 shell call per promoted rule. The saved cost on a stale promotion is one full verify→implement loopback.
