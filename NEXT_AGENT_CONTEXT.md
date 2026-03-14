# NEXT_AGENT_CONTEXT

Version: **2.0.6**

This file is the bundle-level handoff for the next intelligent agent. Read this before touching the repo.

## 1. Mission

`xlfg` is an **agent harness skill** for building production-grade services.

The main product is not the helper CLI. The main product is the **plugin workflow and file protocol** that force agents to:

- recall relevant prior knowledge before broad fan-out
- define why, behavior, and proof before coding
- avoid fake-green verification
- learn from repeated environment failures
- leave behind durable, low-conflict knowledge for future runs

## 2. Problem solved in 2.0.6

The user reported a real operational failure:

> when multiple worktrees or branches used xlfg at the same time, they kept getting PR merge conflicts on shared knowledge files.

The old model had a hidden flaw: feature branches were editing the same tracked rollup docs (`current-state.md`, `patterns.md`, `testing.md`, `failure-memory.md`, `harness-rules.md`, `ledger.jsonl`, role memory markdown). Those files were serving **two jobs at once**:

1. durable storage
2. convenient read model

That was the wrong design for concurrent branches.

## 3. New design in one sentence

**Tracked knowledge is now written only as immutable branch-scoped cards and immutable event files. Local `_views/` files are generated read models and must not be hand-edited on feature branches.**

## 4. Current target-repo knowledge model

### Tracked durable artifacts

- `docs/xlfg/meta.json`
- `docs/xlfg/index.md`
- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/knowledge/commands.json`
- `docs/xlfg/knowledge/cards/<kind>/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `docs/xlfg/knowledge/events/<branch-slug>/<timestamp>--<run-id>--<slug>.json`
- `docs/xlfg/knowledge/agent-memory/<role>/cards/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `docs/xlfg/migrations/`

### Local generated read models

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/<kind>.md`
- `docs/xlfg/knowledge/_views/agent-memory/<role>.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`
- `docs/xlfg/knowledge/_views/worktree.md`

### Local evidence

- `docs/xlfg/runs/<run-id>/...`
- `.xlfg/runs/<run-id>/...`

## 5. Why this matters

This resolves the merge-conflict problem without weakening compounding.

- feature branches write new files instead of editing the same shared file
- generated rollups become local conveniences, not merge-sensitive write targets
- the next agent in the same worktree still gets a fast `current-state.md`
- durable knowledge is preserved through cards/events and can be replayed into views at any time

## 6. Code changes in this patch

### New modules / capabilities

- `xlfg/gitmeta.py`
  - detects git top/common dir, branch, default branch, worktree name, branch slug, and knowledge write namespace
  - writes `.xlfg/worktree.json`

- `xlfg/knowledge.py`
  - creates tracked card/event layout
  - creates local `_views/` layout
  - rebuilds shared and role-memory read models
  - rebuilds local `ledger.jsonl`
  - writes `worktree.md`

### Reworked modules

- `xlfg/scaffold.py`
  - scaffold schema version is now **7**
  - creates `service-context.md`, `write-model.md`, `cards/`, `events/`, and role card dirs
  - treats `_views/` as local generated read models
  - records worktree context and rebuilds views during prepare/init

- `xlfg/cli.py`
  - `status` now reports git/worktree context
  - new `worktree` subcommand
  - new `knowledge rebuild` subcommand

- `xlfg/recall.py`
  - recall now searches local generated views, tracked cards, tracked role cards, immutable events, static docs, and runs
  - legacy `ledger.jsonl` is still read if present for migration compatibility

- `tests/test_xlfg.py`
  - now verifies branch-safe layout, `_views/` generation, event recall, role-memory views, and legacy metadata handling

## 7. Prompt / plugin changes in this patch

The command and skill docs were rewritten so future agents do not accidentally keep using the old hot-file model.

Important behavior now expected from the prompts:

- `/xlfg:prepare`
  - ensure scaffold exists
  - detect version drift
  - record worktree context
  - rebuild local views

- `/xlfg:recall`
  - read `_views/current-state.md` first
  - read other `_views/`, cards, events, and runs deterministically

- `/xlfg:compound`
  - write immutable shared cards under `cards/<kind>/<branch-slug>/...`
  - write immutable role cards under `agent-memory/<role>/cards/<branch-slug>/...`
  - write immutable event JSON files under `events/<branch-slug>/...`
  - rebuild local `_views/`
  - never hand-edit `_views/current-state.md` or `_views/ledger.jsonl`

## 8. Research synthesis that justified this design

The design direction is:

- append-only or immutable write model
- deterministic replay / projection into read models
- explicit worktree-aware context
- role-aligned memory instead of a giant shared blob
- no vector/RAG dependency in the core path

For the detailed reasoning, read `docs/branch-safe-knowledge.md`.

## 9. Editing rules for the next agent

- bump **patch only**
- keep the plugin workflow as the product; CLI is optional support
- do not reintroduce tracked hot rollup files as the main write target
- do not add vector-search or semantic recall as a core dependency
- keep `_views/` local and generated
- if you change the knowledge model, update:
  - `NEXT_AGENT_CONTEXT.md`
  - `docs/branch-safe-knowledge.md`
  - `plugins/xlfg-engineering/README.md`
  - `plugins/xlfg-engineering/CHANGELOG.md`
  - `xlfg/scaffold.py`
  - `tests/test_xlfg.py`

## 10. Read these next

1. `docs/branch-safe-knowledge.md`
2. `plugins/xlfg-engineering/commands/xlfg-compound.md`
3. `plugins/xlfg-engineering/commands/xlfg-prepare.md`
4. `xlfg/knowledge.py`
5. `xlfg/scaffold.py`
6. `tests/test_xlfg.py`

## 11. Validation

- `pytest`: 15 passed
- branch-priority view generation is covered by tests
- prepare/recall/migration/layout behavior is covered by tests

## 12. Success criterion

A target repo using `/xlfg` across multiple branches or linked worktrees should now be able to:

- compound useful lessons without all branches editing the same shared file
- rebuild a useful local handoff in each worktree
- keep durable knowledge reviewable in git
- avoid the old PR conflict pattern on knowledge files
