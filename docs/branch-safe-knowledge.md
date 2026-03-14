# Branch-safe knowledge for xlfg 2.0.6

## Why this patch exists

Concurrent xlfg runs from multiple branches or linked worktrees were producing PR conflicts because they all edited the same tracked knowledge rollups.

That was a design smell, not just a git annoyance.

The rollup files were serving two jobs at once:

1. storage
2. read-time convenience

When the same file tries to do both jobs in a multi-branch workflow, compounding becomes a merge-conflict factory.

## Problem statement

The old hot files were things like:

- `current-state.md`
- `patterns.md`
- `decision-log.md`
- `testing.md`
- `ux-flows.md`
- `failure-memory.md`
- `harness-rules.md`
- `quality-bar.md`
- `ledger.jsonl`
- role-memory markdown files

Every branch that learned something wanted to edit the same files.

## Wrong fixes we intentionally rejected

### 1) “Just use union merge”

Not good enough.

A union merge can keep both sides’ text, but it does not preserve a strong knowledge model. It can duplicate or interleave lessons and still force humans to clean the result.

### 2) “Just keep compounding local only”

Also wrong.

If nothing durable lands in the repo, the harness stops evolving.

### 3) “Use vector memory instead”

Not a fix for the git conflict problem, and not acceptable as the core reliability mechanism here.

## New design

### Tracked write model

Write immutable tracked artifacts only:

- `docs/xlfg/knowledge/cards/<kind>/<branch-slug>/<timestamp>--<run-id>--<slug>.md`
- `docs/xlfg/knowledge/events/<branch-slug>/<timestamp>--<run-id>--<slug>.json`
- `docs/xlfg/knowledge/agent-memory/<role>/cards/<branch-slug>/<timestamp>--<run-id>--<slug>.md`

### Local generated read model

Read generated local views:

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/<kind>.md`
- `docs/xlfg/knowledge/_views/agent-memory/<role>.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`
- `docs/xlfg/knowledge/_views/worktree.md`

### Stable tracked seed

Keep a small, durable tracked seed:

- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/knowledge/commands.json`

## Compounding rules

When `/xlfg:compound` runs:

1. read the run artifacts
2. read the service context and generated views
3. identify only verified, reusable lessons
4. write each admitted lesson as a new immutable card or event file
5. rebuild local views
6. update `compound-summary.md`

Do **not** hand-edit generated `_views/` files on feature branches.

## Why the design is sound

It matches several non-experimental ideas that are already strong enough for production engineering workflows:

- separate **append-only / immutable write state** from **materialized read models**
- keep memory **role-aligned** and **unit-of-work aligned**
- treat concurrency as a first-class design concern
- prefer replayable artifacts over constantly rewritten summaries
- make the worktree/branch context explicit

## What the next agent should remember

- `_views/` are for reading
- `cards/` and `events/` are for tracked writing
- `service-context.md` is the stable tracked seed
- `commands.json` is where stack-specific verification commands should become exact
- `worktree.md` tells the current branch/worktree write namespace
- `xlfg knowledge rebuild` regenerates the local views

## Practical effect

This patch should sharply reduce knowledge-file merge conflicts while keeping the harness capable of real learning.

## Research signals behind the design

The design choice was guided by a few non-experimental ideas that fit production engineering better than “just add smarter retrieval”:

### Event-sourcing / CQRS style split

A durable system should separate **immutable writes** from **materialized reads**.

In xlfg terms:
- cards/events are the durable write side
- `_views/` are the local materialized reads

### Memory governance should be separate from memory growth

Not every learned thing deserves durable status.

That is why `/xlfg:compound` still has an admission gate:
- concrete
- verified or repeatedly observed
- reusable
- small enough to retrieve cheaply

### Concurrent multi-agent memory needs provenance and conflict resistance

If many branches or agents can write at once, the system needs:
- isolated write units
- stable naming
- provenance
- replayable rebuilds

That is exactly why each lesson now has its own card and event file.

### Role-aligned memory is better than one giant summary blob

Shared knowledge and role memory serve different jobs.

That is why role memory is also branch-scoped cards plus generated views.

## Design consequences

Because of those signals, xlfg now follows these rules:

1. do not use generated rollups as the source of truth
2. do not keep one hot tracked markdown file per knowledge kind
3. do not require vector retrieval to make memory useful
4. do keep durable memory reviewable in git
5. do keep recall deterministic and exact by default
6. do keep the next-agent handoff fast through local view generation

