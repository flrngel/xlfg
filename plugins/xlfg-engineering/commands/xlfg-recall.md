---
name: xlfg:recall
description: Deterministic recall over generated views, immutable cards/events, role memory, and local runs.
argument-hint: "[today|yesterday|last week|TOPIC|typed query document]"
---

# /xlfg:recall

Load context from xlfg memory **before** wide repo fan-out and without relying on vector search or fuzzy semantic guesses.

<input>#$ARGUMENTS</input>

## Purpose

Keep only the parts of recall that are deterministic and auditable:

- current-state handoff from `docs/xlfg/knowledge/_views/current-state.md`
- temporal recall over local xlfg runs
- lexical topic recall over generated views, tracked cards, immutable events, and local runs
- typed query documents for precision (`lex:`, `kind:`, `stage:`, `role:`, `scope:`, `path:`, `when:`)
- a final One Thing recommendation only when the evidence is strong enough

## First read

Always read `docs/xlfg/knowledge/_views/current-state.md` first if it exists.

Treat it as the shortest worktree-local handoff for the next agent.

## Backends

If the helper CLI is installed, you may use it as a deterministic backend:

```bash
xlfg recall "$ARGUMENTS"
```

If the helper CLI is not installed, do recall manually using exact lexical search over:

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/*.md`
- `docs/xlfg/knowledge/_views/agent-memory/*.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`
- `docs/xlfg/knowledge/cards/**`
- `docs/xlfg/knowledge/events/**`
- `docs/xlfg/knowledge/agent-memory/*/cards/**`
- `docs/xlfg/knowledge/service-context.md`
- `docs/xlfg/knowledge/write-model.md`
- `docs/xlfg/runs/**`

Use exact file reads and lexical search (`rg`, `find`, `jq`, etc.). Do not substitute semantic guesses.

## Routing

### A) Temporal recall

If the query is just a date expression (`today`, `yesterday`, `last week`, `YYYY-MM-DD`, `last 7 days`):

- list the matching runs concisely
- show timestamp, run id, request / summary, and phases present

### B) Topic recall

For plain topic queries:
- use exact lexical search over current-state, views, cards, events, role memory, and runs

For precision-critical recall, use a typed query document, for example:

```bash
xlfg recall $'lex: "port already in use" yarn dev healthcheck
stage: verify
kind: failure harness-rule
role: env-doctor
scope: memory runs
when: last 14 days'
```

## Presentation

Organize results by scope when helpful:
- **Current state** — generated handoff for this worktree
- **Knowledge views** — generated rollups of durable shared cards
- **Tracked cards / events** — exact durable source records
- **Role memory** — generated specialist memory plus source cards when needed
- **Runs** — local episodic context and recent artifacts

For each hit, show:
- why it matched
- why it matters now
- path or run id

## One Thing

If the results clearly point to the next best action, end with:

> **One Thing:** <specific action>

Use this only when the evidence is concrete. Otherwise omit it.

## Rules

- Prefer exact lexical evidence over “close enough” semantic similarity.
- Do not invent results that the files did not support.
- When a result is stale or superseded, say so.
- Do not turn recall into a long essay; the goal is fast, usable context loading.
- When `/xlfg:recall` is used as part of `/xlfg`, planning must preserve the strongest hits or an explicit no-hit case in `memory-recall.md`.
