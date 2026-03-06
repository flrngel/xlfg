---
name: xlfg:recall
description: Deterministic recall over current-state, durable xlfg knowledge, role memory, the append-only ledger, and local runs.
argument-hint: "[today|yesterday|last week|TOPIC|typed query document]"
---

# /xlfg:recall

Load context from xlfg memory **before** wide repo fan-out and without relying on vector search or fuzzy semantic guesses.

<input>#$ARGUMENTS</input>

## Purpose

Reverse-engineered useful parts of `/recall` and QMD, but keep only the parts that are deterministic and auditable:

- **Current-state handoff** from `docs/xlfg/knowledge/current-state.md`
- **Temporal recall** over local xlfg runs
- **Lexical topic recall** over tracked knowledge, role memory, the append-only ledger, and local runs
- **Typed query documents** for precision (`lex:`, `kind:`, `stage:`, `role:`, `scope:`, `path:`, `when:`)
- A final **One Thing** recommendation only when the retrieved evidence is strong enough

## First read

Always read `docs/xlfg/knowledge/current-state.md` first if it exists.

Treat it as the shortest tracked handoff for the next agent.

## Backends

If the helper CLI is installed, you may use it as a deterministic backend:

```bash
xlfg recall "$ARGUMENTS"
```

If the helper CLI is **not** installed, do recall manually using exact lexical search over:

- `docs/xlfg/knowledge/current-state.md`
- `docs/xlfg/knowledge/*.md`
- `docs/xlfg/knowledge/agent-memory/*.md`
- `docs/xlfg/knowledge/ledger.jsonl`
- `docs/xlfg/runs/**`

Use exact file reads and lexical search (`rg`, `find`, `jq`, etc.). Do not substitute semantic guesses.

## Routing

### A) Temporal recall

If the query is just a date expression (`today`, `yesterday`, `last week`, `YYYY-MM-DD`, `last 7 days`):

- list the matching runs concisely
- show timestamp, run id, request / summary, and phases present

### B) Topic recall

For plain topic queries:
- use exact lexical search over current-state, knowledge, role memory, ledger, and runs

For precision-critical recall, use a typed query document, for example:

```bash
xlfg recall $'lex: "port already in use" yarn dev healthcheck\nstage: verify\nkind: failure harness-rule\nrole: env-doctor\nscope: memory runs\nwhen: last 14 days'
```

## Presentation

Organize results by scope when helpful:
- **Current state** — the tracked handoff document
- **Knowledge** — durable repo-level rules, patterns, testing, UX
- **Role memory** — stage-specific lessons for a single specialist
- **Ledger** — structured memory events with evidence
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
