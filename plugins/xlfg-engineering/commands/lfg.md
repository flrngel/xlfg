---
name: lfg
description: Manual macro for shipping via /xlfg (sequential mode).
disable-model-invocation: true
---

# /lfg

Time to ship.

Use this when you want **one lead agent** plus a few focused subagents (plan/review/testing), without spawning a full agent team.

## Recommended sequence

1. **(Once per repo)** `/xlfg:init`
2. `/xlfg <what you want built>`

## Suggested prompt to pass to /xlfg

> Stay in **sequential mode**: one lead agent does implementation. Use subagents only for repo mapping, test planning, and review. Avoid parallel code edits.
