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
5. Use specialists as true lane owners, not optional advisors:
   - always run `xlfg-repo-mapper`
   - run `xlfg-harness-profiler` for any build / bugfix / delivery run
   - run `xlfg-context-adjacent-investigator`, `xlfg-context-constraints-investigator`, and `xlfg-context-unknowns-investigator` whenever the request is bundled, risky, or still assumption-heavy
   - run `xlfg-env-doctor` when local server behavior is relevant
   - run `xlfg-researcher` only when freshness or missing domain knowledge makes repo truth insufficient
6. Keep these specialists foregrounded. After each specialist returns, verify its expected artifact exists, begins with `Status:`, and contains real findings instead of preparation notes.
7. Use the specialist artifacts as the primary lane evidence. The main conductor should synthesize from them rather than silently redoing their work in chat.
8. Write or update `context.md` with:
   - relevant repo and product context
   - hard constraints
   - known unknowns
   - likely harness / environment facts
9. Update the research and context sections of `spec.md`.
10. If a required specialist failed to produce its artifact, classify that in `workboard.md` and either retry once or continue only with an explicit gap note.
11. Create `research.md` only when external research materially changes the decision surface.
12. Keep `workboard.md` current while planning is in progress.

## Guardrails

- Prefer repo truth over guesswork.
- Use external research only when it is truly needed or the user asked for it.
- Do not create duplicate mini-plans here; this phase is for truth gathering.
- Do not silently widen the objective set without updating the intent contract in `spec.md`.
