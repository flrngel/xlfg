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

> Stay in **sequential mode**: one lead agent owns orchestration. Run context-expansion and planning/review subagents as file-based handoffs. For implementation, use implementer/checker pairs for every plan task. Auto-continue from plan to implementation; only pause for true blockers or safety-gated confirmations.
