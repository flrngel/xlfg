---
name: lfg
description: Manual macro for shipping via /xlfg (single lead + focused subagents).
disable-model-invocation: true
---

# /lfg

Use this when one lead agent should own execution and only spawn the minimum necessary specialists.

## Recommended sequence

1. **(Once per repo)** `/xlfg:init`
2. `/xlfg <what you want built>`

## Suggested prompt to pass to /xlfg

> Stay in **single-lead mode**. Keep fan-out small. Define `flow-spec.md`, `test-contract.md`, and `env-plan.md` before coding. Use targeted checks after each task and only run full gate verification when the plan says it is time.
