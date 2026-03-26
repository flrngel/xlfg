# xlfg recall query syntax

xlfg recall uses deterministic typed query documents inspired by QMD's query documents, but **without vector search, HyDE, or LLM expansion**. Always read `current-state.md` first.

## Plain query

A plain query is treated as an exact lexical search:

```
xlfg recall 'login button enter submit'
```

If the plain query is a supported date expression, xlfg does temporal recall instead:

```
xlfg recall yesterday
xlfg recall last week
xlfg recall 2026-03-06
```

## Typed query document

Each non-empty line is `type: value`. Supported types:
- `lex:` quoted phrases + negation + exact lexical terms
- `kind:` filter memory kind(s)
- `stage:` filter SDLC stage(s)
- `role:` filter role memory
- `scope:` filter `knowledge`, `agent-memory`, `ledger`, `runs`, `migrations`, `memory`, or `all` (with `current-state.md` living under `knowledge`)
- `path:` substring filter on relative path
- `when:` temporal filter (`today`, `yesterday`, `last week`, `YYYY-MM-DD`, `last 7 days`)

Example:

```
lex: "login button" enter -oauth
stage: plan verify
kind: testing harness-rule
role: test-strategist env-doctor
scope: memory runs
when: last 14 days
```

## Lex rules

- `word` → exact token / prefix-like lexical match
- `"phrase"` → exact phrase
- `-word` → exclude results containing the word
- `-"phrase"` → exclude results containing the phrase

This mode is intentionally precision-first and auditable.
