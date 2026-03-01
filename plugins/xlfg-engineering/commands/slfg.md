---
name: slfg
description: Manual macro for shipping via /xlfg (swarm / agent-team mode).
disable-model-invocation: true
---

# /slfg

Use this when the request has multiple independent surfaces (frontend + backend + tests + infra) and parallel planning or review will help.

## Recommended sequence

1. **(Once per repo)** `/xlfg:init`
2. `/xlfg <what you want built>`

## Suggested prompt to pass to /xlfg

> Prefer **swarm mode** for planning and review, but keep implementation ownership conflict-free. All agents must coordinate through `docs/xlfg/runs/<run-id>/`. Do not start coding until `flow-spec.md`, `test-contract.md`, and `env-plan.md` are written.
