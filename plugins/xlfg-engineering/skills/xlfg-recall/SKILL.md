---
name: xlfg-recall
description: Deterministic recall for xlfg memory. Use current-state first, then typed lexical recall over views, tracked cards/events, role memory, and runs.
---

# xlfg recall skill

Use this when an xlfg agent or user needs past context without relying on vector search.

## Read order

1. `docs/xlfg/knowledge/_views/current-state.md`
2. `docs/xlfg/knowledge/_views/*.md`
3. `docs/xlfg/knowledge/_views/agent-memory/*.md`
4. `docs/xlfg/knowledge/_views/ledger.jsonl`
5. `docs/xlfg/knowledge/cards/**`
6. `docs/xlfg/knowledge/events/**`
7. `docs/xlfg/knowledge/agent-memory/*/cards/**`
8. `docs/xlfg/runs/`

## Backends

If the helper CLI exists, you may use it:

```bash
xlfg recall yesterday
xlfg recall 'login button enter submit'
xlfg recall --file query.qmd
```

If the helper CLI does not exist, perform the same deterministic recall manually with exact lexical search over the files above.

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
xlfg recall $'lex: "port already in use" yarn dev healthcheck
stage: verify
kind: failure harness-rule
role: env-doctor
scope: memory runs
when: last 30 days'
```

Supported keys:
- `lex:` exact lexical search with phrases and negation
- `kind:` memory kind(s)
- `stage:` `plan`, `implement`, `verify`, `review`, `compound`, `cross`
- `role:` `why-analyst`, `root-cause-analyst`, `harness-profiler`, `solution-architect`, `test-strategist`, `env-doctor`, `test-implementer`, `task-implementer`, `task-checker`, `verify-reducer`, `ux-reviewer`, `architecture-reviewer`, `security-reviewer`, `performance-reviewer`
- `scope:` `knowledge`, `agent-memory`, `ledger`, `runs`, `migrations`, `memory`, `all`
- `path:` substring filter
- `when:` date filter

## Heuristics

- prefer `stage` + `kind` + `role` filters before broad lexical search
- use `scope: memory` when you want only durable knowledge
- use `scope: runs` when you want recent local context
- use quoted phrases and negation when a term is overloaded
- preserve strong hits or an explicit no-hit in `memory-recall.md` before planning continues
- do not ask for vector-like semantic recall; this skill is intentionally deterministic
