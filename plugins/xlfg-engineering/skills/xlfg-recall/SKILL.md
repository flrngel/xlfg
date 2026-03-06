---
name: xlfg-recall
description: Deterministic recall for xlfg memory. Use temporal recall for recent runs and typed lexical query documents for durable knowledge, role memory, and the append-only ledger.
---

# xlfg recall skill

Use this when an xlfg agent or user needs past context without relying on vector search.

## Backends

- `docs/xlfg/runs/` — local episodic run history
- `docs/xlfg/knowledge/*.md` — durable shared knowledge
- `docs/xlfg/knowledge/agent-memory/*.md` — compact role memory
- `docs/xlfg/knowledge/ledger.jsonl` — append-only structured memory events

## Query modes

### 1) Temporal

```bash
xlfg recall yesterday
xlfg recall last week
xlfg recall 2026-03-06
```

### 2) Plain lexical

```bash
xlfg recall 'login button enter submit'
```

### 3) Typed query document

```bash
xlfg recall $'lex: "port already in use" yarn dev healthcheck\nstage: verify\nkind: failure harness-rule\nrole: env-doctor\nscope: memory runs\nwhen: last 30 days'
```

Supported keys:
- `lex:` exact lexical search with phrases and negation
- `kind:` memory kind(s)
- `stage:` `plan`, `implement`, `verify`, `review`, `compound`, `cross`
- `role:` `root-cause-analyst`, `test-strategist`, `env-doctor`, `task-implementer`, `verify-reducer`, `ux-reviewer`
- `scope:` `knowledge`, `agent-memory`, `ledger`, `runs`, `migrations`, `memory`, `all`
- `path:` substring filter
- `when:` date filter

## Heuristics

- Prefer `stage` + `kind` + `role` filters before broad lexical search.
- Use `scope: memory` when you want only durable tracked knowledge.
- Use `scope: runs` when you want recent local context.
- Use quoted phrases and negation when a term is overloaded.
- Do not ask for vector-like semantic recall; this skill is intentionally deterministic.
