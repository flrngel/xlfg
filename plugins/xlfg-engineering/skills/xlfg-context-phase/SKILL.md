---
description: Internal xlfg phase skill. Use only during /xlfg runs to gather repo truth, current constraints, harness facts, and targeted external research when needed.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write, WebSearch, WebFetch, Agent, SendMessage
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
5. Use specialists as true lane owners, not optional advisors. Give each one objective context plus one bounded output artifact. Keep default fan-out small: run one active artifact-producing specialist at a time, then load the next specialist only if the previous artifact leaves a concrete unresolved gap. Repo-map, harness-profile, and external research should normally run sequentially because each artifact shapes the next packet:
   - always run `xlfg-repo-mapper`
   - run `xlfg-harness-profiler` for any build / bugfix / delivery run
   - run `xlfg-context-adjacent-investigator`, `xlfg-context-constraints-investigator`, or `xlfg-context-unknowns-investigator` one at a time when the request is bundled, risky, or still assumption-heavy
   - run `xlfg-env-doctor` when local server behavior is relevant
   - run `xlfg-researcher` only when freshness or missing domain knowledge makes repo truth insufficient
6. Keep these specialists foregrounded, short-lived, and leaf-only. After each specialist returns, verify its expected artifact exists, begins with `Status:`, and contains real findings instead of preparation notes. If it does not, use `SendMessage` with the returned agent ID to resume the same specialist once before treating the lane as failed. If no agent ID is available, re-dispatch the exact same packet once.
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

## Delegation packet rules

- Preseed the target artifact before dispatch. The parent conductor should create the file named in `PRIMARY_ARTIFACT` with `Status: IN_PROGRESS`, the scoped mission, and a short checklist so the specialist is resuming a concrete work item instead of starting from an empty chat turn.
- Every specialist packet must begin with machine-readable headers:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only
```

- Pass objective context, not just a naked query. Include the exact ask, nearby constraints, and why the artifact matters to the next phase.
- Only the phase conductor may delegate. Never ask a context specialist to spawn nested subagents or to fan out its own lane.
- Default to **sequential** dispatch for artifact-producing planning/context work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Guardrails

- Prefer repo truth over guesswork.
- Use external research only when it is truly needed or the user asked for it.
- Do not create duplicate mini-plans here; this phase is for truth gathering.
- Do not silently widen the objective set without updating the intent contract in `spec.md`.
