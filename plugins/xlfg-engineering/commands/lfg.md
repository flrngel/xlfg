---
name: lfg
description: Manual macro for shipping via /xlfg (sequential mode).
disable-model-invocation: true
---

# /lfg

Time to ship.

Use this when you want **one lead agent** plus focused subagents, without a full implementation swarm.

## Recommended sequence

1. **(Once per repo)** `/xlfg:init`
2. `/xlfg <what you want built>`

## Suggested prompt to pass to /xlfg

> Stay in **sequential mode**: one lead agent owns implementation. Run context-expansion and planning/review subagents as file-based handoffs. Use pair implementer/checker only for medium/high-risk tasks.
