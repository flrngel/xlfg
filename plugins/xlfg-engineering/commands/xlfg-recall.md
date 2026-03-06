---
name: xlfg:recall
description: Deterministic recall over durable xlfg knowledge, role memory, the append-only ledger, and local runs.
argument-hint: "[today|yesterday|last week|TOPIC|typed query document]"
---

# /xlfg:recall

Load context from xlfg memory without relying on vector search or fuzzy semantic guesses.

<input>#$ARGUMENTS</input>

## Purpose

Reverse-engineered useful parts of `/recall` and QMD, but keep only the parts that are deterministic and auditable:

- **Temporal recall** over local xlfg runs
- **Lexical topic recall** over tracked knowledge, role memory, the append-only ledger, and local runs
- **Typed query documents** for precision (`lex:`, `kind:`, `stage:`, `role:`, `scope:`, `path:`, `when:`)
- A final **One Thing** recommendation only when the retrieved evidence is strong enough

## Routing

### A) Temporal recall

If the query is just a date expression (`today`, `yesterday`, `last week`, `YYYY-MM-DD`, `last 7 days`), run:

```bash
xlfg recall "$ARGUMENTS"
```

Present the run list as a concise table with:
- timestamp
- run id
- request / summary
- phases present

### B) Topic recall

For plain topic queries, run:

```bash
xlfg recall "$ARGUMENTS"
```

For precision-critical recall, use a typed query document, for example:

```bash
xlfg recall $'lex: "login button" enter -oauth\nstage: verify\nkind: testing harness-rule\nscope: memory runs\nwhen: last 14 days'
```

## Presentation

Organize results by scope when helpful:
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
- Do not invent results that `xlfg recall` did not return.
- When a result is stale or superseded, say so.
- Do not turn recall into a long essay; the goal is fast, usable context loading.
