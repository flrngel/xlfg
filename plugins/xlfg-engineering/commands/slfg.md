---
name: slfg
description: Manual macro for shipping via /xlfg (swarm / agent-team mode).
disable-model-invocation: true
---

# /slfg

Swarm LFG.

Use this when parallelism pays off:

- Multi-layer changes (frontend + backend + tests)
- Debugging with competing hypotheses
- Big refactors with many independent files
- Security/performance/test reviews in parallel

## Recommended sequence

1. **(Once per repo)** `/xlfg:init`
2. `/xlfg <what you want built>`

## Suggested prompt to pass to /xlfg

> Prefer **swarm mode**: run context-expansion + planning/review agents in parallel, then execute implementation as mandatory scoped implementer/checker pairs for every plan task, managed by one lead. Keep ownership conflict-free and hand off only through `docs/xlfg/runs/<run-id>/`.
