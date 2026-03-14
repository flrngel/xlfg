# NEXT_AGENT_CONTEXT

Read this before touching the repo. This document is the bundle-level handoff so the next intelligent agent can continue without extra explanation.

## 1. Mission

`xlfg` is not trying to be a generic CLI product. The real product is the **agent skill / harness** that helps Claude Code or similar coding agents build **production-grade services** with less fake-green output, less terminal thrash, and better retained operational knowledge.

The harness should make good engineering behavior easier than bad engineering behavior.

## 2. Non-negotiables from the user

- `/xlfg` must be a macro composed of explicit subcommands.
- `/xlfg` must **use recall**. A recall system that only exists in a side CLI is meaningless.
- Planning and implementation must prevent bad output; review is not the cleanup crew.
- The workflow must prefer the **root solution**, not temporal patches.
- Testing must be defined from concrete **UX / behavior flows** before coding.
- Environment / harness failures must be learned and compounded so the same failure does not keep happening.
- Every delivered bundle should include a high-signal handoff document so the next agent can pick up immediately.
- Do **not** push vector-search / RAG / HyDE / reranking as a required core dependency.
- Normal evolution bumps **patch version only**.

## 3. What changed in 2.0.5

This patch takes useful ideas from DeerFlow-style harness thinking without turning xlfg into a giant always-on runtime.

### Main changes

1. Planning now starts with an explicit `why.md` written by `xlfg-why-analyst`.
2. Planning now chooses a run-specific `harness-profile.md` (`quick`, `standard`, `deep`) written by `xlfg-harness-profiler`.
3. Every run now has a `workboard.md` as a persistent stage / task ledger.
4. Every run now has a `proof-map.md` so verification cannot pretend that green commands automatically mean real proof.
5. `/xlfg:plan` now loads optional planning agents progressively instead of fanning out by default.
6. `/xlfg` now reads the recommended verify mode from `harness-profile.md` instead of assuming maximal verification every time.
7. Role memory now includes `why-analyst` and `harness-profiler`.
8. This bundle now includes `docs/deer-flow-harness-review.md`, which explains what was borrowed, what was rejected, and why.

## 4. Why DeerFlow mattered here

The key useful lesson was **not** “make xlfg huge.”

The useful lesson was:
- think of the harness as **runtime structure**, not a bigger prompt
- keep explicit task state
- bound subagent concurrency and execution cost
- load capabilities progressively
- separate durable memory from per-run state

That pushed xlfg toward:
- `why.md`
- `harness-profile.md`
- `workboard.md`
- `proof-map.md`
- optional agent fan-out only when the diagnosis justifies it

## 5. Design direction

The desired shape is:

1. **Prepare fast** — check scaffold version, migrate only on drift.
2. **Recall first** — read the smallest relevant prior context before wide repo scanning.
3. **Why first** — anchor the run to the user / operator value and false-success rejection.
4. **Diagnose** — identify the real capability gap or fault chain.
5. **Contract** — define behavior, tests, and environment up front.
6. **Profile** — choose the minimum honest harness intensity.
7. **Implement with bounded loops** — task-scoped work, explicit checks, anti-shortcut discipline.
8. **Verify honestly** — layered proof with environment-state awareness.
9. **Review as confirmation** — not as rescue.
10. **Compound** — promote only small, verified lessons; keep runs local by default.
11. **Refresh the handoff** — keep a concise tracked context document for the next agent.

## 6. Why recall is mandatory

The user repeatedly ran into predictable harness failures such as duplicate `yarn dev`, port collisions, stale bundles, and expensive E2E loops that still missed real failures. When the system forgets those lessons at the start of a new run, it wastes time rediscovering them.

Therefore recall is a first-class workflow step, not a side utility.

`/xlfg` should always start from:

- `docs/xlfg/knowledge/current-state.md`
- durable shared knowledge (`testing.md`, `ux-flows.md`, `failure-memory.md`, `harness-rules.md`, etc.)
- role-specific memory when the role matches
- the append-only ledger
- recent local runs when they genuinely match

## 7. Memory model

There are now four layers of memory:

1. **current-state.md** — the one tracked handoff doc a new agent should read first
2. **shared knowledge** — tracked repo-wide durable lessons
3. **role memory** — compact specialist heuristics for recurring failure classes
4. **local runs** — episodic evidence, usually gitignored

The bundle-level analogue of `current-state.md` is this file: `NEXT_AGENT_CONTEXT.md`. Keep it updated whenever the bundle meaningfully changes.

## 8. Research synthesis that shaped the current design

This repo intentionally follows the non-hype parts of the research and ignores the parts that are hard to trust operationally.

### Adopted ideas

- **Long-horizon agents need explicit artifacts** instead of hoping the model keeps everything straight in chat history.
- **Verification should be requirement-linked** (new behavior and regression behavior) rather than a late generic suite blast.
- **Memory should be subtask-, stage-, and role-aligned** instead of one giant summary blob.
- **Append-only memory with provenance** is better than constantly rewriting “what we learned.”
- **A harness is runtime structure**: state, bounded loops, capability loading, and execution policies.

### Rejected from the core path

- vector search
- embedding stores
- HyDE / hypothetical query expansion
- mandatory reranking
- giant always-on server architecture for normal plugin usage

Those may be studied elsewhere, but they should not be required in the core harness until they are precise enough for production trust.

## 9. Current weak spots

These are not solved yet and remain high-value follow-ups:

- repo-specific stack profiles are still thin; command detection is still heuristic in unknown repos
- reviewer specialization can improve further for framework-specific systems
- `current-state.md` needs disciplined curation so it stays short and useful
- plugin prompts still rely on the lead agent to honestly maintain `workboard.md` and `proof-map.md`; stronger mechanical enforcement could help

## 10. Editing rules for the next agent

If you continue evolving this repo:

- bump **patch only**
- update version in all required files
- update `plugins/xlfg-engineering/CHANGELOG.md`
- update this `NEXT_AGENT_CONTEXT.md`
- prefer improving `/xlfg` and its subcommands over polishing the CLI
- do not add experimental retrieval as a core dependency
- keep `docs/xlfg/runs/` local by default unless there is a very strong reason not to

## 11. Suggested immediate next checks

If continuing from 2.0.5, inspect these first:

- `docs/deer-flow-harness-review.md`
- `plugins/xlfg-engineering/commands/xlfg.md`
- `plugins/xlfg-engineering/commands/xlfg-plan.md`
- `plugins/xlfg-engineering/commands/xlfg-verify.md`
- `xlfg/scaffold.py`
- `tests/test_xlfg.py`

## 12. Success criterion

The user should be able to install the plugin, run `/xlfg`, and get a workflow that:

- remembers relevant past failures and harness rules up front
- defines why, behavior, and proof before coding
- picks an honest harness intensity instead of wasting time by default
- avoids the same bad dev-server / port / stale-build loops
- prefers root fixes over temporal patches
- leaves behind a clear tracked handoff for the next agent

## 2.0.7 merge-friendly knowledge change

This bundle intentionally rolls back the heavier 2.0.6 branch-safe model and returns to the simpler 2.0.5 retrieval shape. The only merge-safety changes are:

- append-only shared knowledge files are protected with `.gitattributes` `merge=union` rules
- `current-state.md` is no longer meant to be rewritten on every feature branch
- feature branches/worktrees should write `docs/xlfg/runs/<RUN_ID>/current-state-candidate.md` instead and let recall read it as local branch context

This keeps retrieval simple and should reduce PR conflicts without introducing cards, events folders, or generated views.
