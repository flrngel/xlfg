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
   - run `xlfg-repo-mapper` unless `memory-recall.md` already contains grep-cited `file:line` entries covering every objective in `spec.md`. When skipping, append a one-line skip note to `context.md` that names the recall coverage (`xlfg-repo-mapper skipped — memory-recall.md lines N–M cover O1, O2`). Do not skip when the surface is unfamiliar, when recall returned an explicit no-hit, or when any objective's files are not cited.
   - run `xlfg-harness-profiler` for any build / bugfix / delivery run
   - run `xlfg-context-adjacent-investigator`, `xlfg-context-constraints-investigator`, or `xlfg-context-unknowns-investigator` one at a time when the request is bundled, risky, or still assumption-heavy
   - run `xlfg-env-doctor` when local server behavior is relevant
   - run `xlfg-researcher` only when freshness or missing domain knowledge makes repo truth insufficient
6. Keep these specialists foregrounded, short-lived, and leaf-only. After each specialist returns, verify its expected artifact exists, begins with YAML frontmatter `status: DONE`, `status: BLOCKED`, or `status: FAILED`, and contains real findings instead of preparation notes. If it does not, use `SendMessage` with the returned agent ID to resume the same specialist once before treating the lane as failed. If no agent ID is available, re-dispatch the exact same packet once.
7. Use the specialist artifacts as the primary lane evidence. The main conductor should synthesize from them rather than silently redoing their work in chat.
8. Write or update `context.md` with:
   - relevant repo and product context
   - hard constraints
   - known unknowns
   - likely harness / environment facts
9. Update the research and context sections of `spec.md`.
10. If a required specialist failed to produce its artifact, classify that in `workboard.md` and either retry once or continue only with an explicit gap note.
11. Create `research.md` only when external research materially changes the decision surface.
12. Keep the task/objective/blocker sections of `workboard.md` current. The `## Phase status` block is rendered by the conductor from `.xlfg/phase-state.json`.

## Delegation packet rules

Follow `agents/_shared/dispatch-rules.md` for the full delegation contract (packet-size ladder, preseed rule, machine-readable headers with `PRIMARY_ARTIFACT` / `DONE_CHECK` / `RETURN_CONTRACT` / `OWNERSHIP_BOUNDARY` / `CONTEXT_DIGEST` / `PRIOR_SIBLINGS` / `Do not redo` / `Consume:`, micro-packet budget, proof budget, compaction, sequential-dispatch default, resume-same-specialist-before-fallback). Only the phase conductor may delegate.

Every context-phase packet MUST begin with the machine-readable headers from `_shared/dispatch-rules.md §3`. `CONTEXT_DIGEST` carries decisions + rationale + path refs so siblings (`context/adjacent.md` → `context/constraints.md` → `context/unknowns.md`) skip ground already covered instead of re-deriving overlapping findings.

### Context ownership boundaries

- `xlfg-repo-mapper` owns command and structure inventory; it does not choose harness intensity or proof strategy.
- `xlfg-harness-profiler` owns budget/profile selection; it cites `repo-map.md` for command discovery instead of rediscovering commands.
- `xlfg-context-adjacent-investigator` owns implied adjacent behaviors; it does not promote weak ideas into intent IDs.
- `xlfg-context-constraints-investigator` owns hard constraints and dependency/security/ops boundaries; it does not restate adjacent feature scope unless the constraint changes acceptance.
- `xlfg-context-unknowns-investigator` owns unresolved assumptions and blockers after prior context artifacts; it does not repeat already-classified adjacent or constraint findings.
- `xlfg-env-doctor` owns runnable environment shape; it does not choose scenario proof breadth.
- `xlfg-researcher` owns only external facts local repo truth cannot provide; it does not research topics already covered by `repo-map.md`, `context.md`, or existing `research.md`.

Compact returned artifacts before updating `context.md` or `spec.md`: carry forward relevant facts, constraints, unknowns, evidence paths, and blockers only; leave long notes in the specialist artifact. Do not paste full specialist reports into canonical run files.

Keep dispatches as **micro-packets**: contract, constraints, and file:line evidence anchors only. Do not paste full source files, full prior artifacts, or a step-by-step investigation script when the specialist can read only the scoped paths it needs.

## Guardrails

- Prefer repo truth over guesswork.
- Use external research only when it is truly needed or the user asked for it.
- Do not create duplicate mini-plans here; this phase is for truth gathering.
- Do not silently widen the objective set without updating the intent contract in `spec.md`.
