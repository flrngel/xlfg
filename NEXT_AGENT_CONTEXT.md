# NEXT AGENT CONTEXT

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

## 3. What changed in 2.0.4

This patch fixes the strategic mistake where recall existed but was not guaranteed to shape `/xlfg`.

### Main changes

1. `/xlfg` now runs recall before planning.
2. `/xlfg:plan` treats recall as mandatory, not optional.
3. `docs/xlfg/knowledge/current-state.md` was added as a single tracked handoff document for the next agent in any target repo.
4. `/xlfg:compound` now updates that current-state handoff along with shared memory and role memory.
5. More role-specific memory files were added for agents that repeatedly need tactical memory.
6. Plugin docs now make it explicit that the CLI is optional support, not the product.

## 4. Design direction

The desired shape is:

1. **Prepare fast** — check scaffold version, migrate only on drift.
2. **Recall first** — read the smallest relevant prior context before wide repo scanning.
3. **Diagnose** — identify the real capability gap or fault chain.
4. **Contract** — define behavior, tests, and environment up front.
5. **Implement with bounded loops** — task-scoped work, explicit checks, anti-shortcut discipline.
6. **Verify honestly** — layered proof with environment-state awareness.
7. **Review as confirmation** — not as rescue.
8. **Compound** — promote only small, verified lessons; keep runs local by default.
9. **Refresh the handoff** — keep a concise tracked context document for the next agent.

## 5. Why recall is mandatory

The user repeatedly ran into predictable harness failures such as duplicate `yarn dev`, port collisions, stale bundles, and expensive E2E loops that still missed real failures. When the system forgets those lessons at the start of a new run, it wastes time rediscovering them.

Therefore recall is a first-class workflow step, not a side utility.

`/xlfg` should always start from:

- `docs/xlfg/knowledge/current-state.md`
- durable shared knowledge (`testing.md`, `ux-flows.md`, `failure-memory.md`, `harness-rules.md`, etc.)
- role-specific memory when the role matches
- the append-only ledger
- recent local runs when they genuinely match

## 6. Why the CLI is secondary

The Python CLI is still useful as a local deterministic helper for scaffold / recall / verify. But the user does not value xlfg because of a CLI. They value it if the **plugin skill itself** makes agent execution better.

When editing this repo, prefer changes that improve the plugin prompts, contracts, and memory model. Do not mistake backend convenience for product value.

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
- **Memory should be stage- and role-aligned** instead of one giant summary blob.
- **Append-only memory with provenance** is better than constantly rewriting “what we learned.”
- **Short, typed, lexical recall** is more auditable than semantic retrieval for production harness memory.

### Rejected from the core path

- vector search
- embedding stores
- HyDE / hypothetical query expansion
- mandatory reranking
- speculative graph-memory dependencies

Those may be studied elsewhere, but they should not be required in the core harness until they are precise enough for production trust.

## 9. Current weak spots

These are not solved yet and remain high-value follow-ups:

- repo-specific stack profiles are still thin; command detection is still heuristic in unknown repos
- reviewer specialization can improve further for framework-specific systems
- `current-state.md` needs disciplined curation so it stays short and useful
- target repos still rely on the agent to honestly maintain contracts; stronger mechanical enforcement could help

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

If continuing from 2.0.4, inspect these first:

- `plugins/xlfg-engineering/commands/xlfg.md`
- `plugins/xlfg-engineering/commands/xlfg-plan.md`
- `plugins/xlfg-engineering/commands/xlfg-compound.md`
- `plugins/xlfg-engineering/skills/xlfg-recall/SKILL.md`
- `xlfg/scaffold.py`
- `tests/test_xlfg.py`

## 12. Success criterion

The user should be able to install the plugin, run `/xlfg`, and get a workflow that:

- remembers relevant past failures and harness rules up front
- defines behavior and proof before coding
- avoids the same bad dev-server / port / stale-build loops
- prefers root fixes over temporal patches
- leaves behind a clear tracked handoff for the next agent
