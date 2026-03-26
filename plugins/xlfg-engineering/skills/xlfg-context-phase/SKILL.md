---
description: Internal xlfg phase skill. Use only during /xlfg runs to gather repo truth, current constraints, harness facts, and targeted external research when needed.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write, WebSearch, WebFetch, Agent
---

# xlfg-context-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Gather the repo and product truth needed for an honest plan without exploding context or duplicating state.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read:
   - `context.md`
   - `memory-recall.md`
   - `spec.md`
   - `workboard.md`
   - `docs/xlfg/knowledge/current-state.md`
3. Start from the intent contract already written in `spec.md`. Keep repo exploration scoped to those direct asks, implied asks, objective groups, and blockers.
4. Explore repo truth first with targeted reads and grep, not broad file hoarding.
5. Use specialized agents only when they buy clarity:
   - `xlfg-repo-mapper`
   - `xlfg-context-adjacent-investigator`
   - `xlfg-context-constraints-investigator`
   - `xlfg-context-unknowns-investigator`
   - `xlfg-harness-profiler`
   - `xlfg-env-doctor` when local server behavior is relevant
   - `xlfg-researcher` only when freshness or missing domain knowledge makes repo truth insufficient
6. Write or update `context.md` with:
   - relevant repo and product context
   - hard constraints
   - known unknowns
   - likely harness / environment facts
7. Update the research and context sections of `spec.md`.
8. Create `research.md` only when external research materially changes the decision surface.
9. Keep `workboard.md` current while planning is in progress.

## Guardrails

- Prefer repo truth over guesswork.
- Use external research only when it is truly needed or the user asked for it.
- Do not create duplicate mini-plans here; this phase is for truth gathering.
- Do not silently widen the objective set without updating the intent contract in `spec.md`.
