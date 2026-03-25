# NEXT_AGENT_CONTEXT

## Current state (2.4.0)

The main 2.4.0 fix is **restoring batch phase skills without re-breaking the entrypoint**.

2.3.0 fixed the broken command/skill collision, but it overcorrected into a monolithic `/xlfg` prompt. That made the public entrypoint work again, but it removed the separated-skill architecture the workflow actually needed.

2.4.0 keeps the good part of 2.3.0 — exactly one public entrypoint per install mode — while restoring the missing part:

- the plugin still exposes one public command at `/xlfg-engineering:xlfg`
- the standalone pack still exposes one public short-name skill at `/xlfg`
- both entrypoints now batch hidden phase skills in this order:
  1. recall
  2. context
  3. plan
  4. implement
  5. verify
  6. review
  7. compound
- the hidden phase skills stay `user-invocable: false`, so the slash menu stays clean
- `spec.md` remains the single source of truth, so phase batching does **not** reintroduce duplicate planning state
- the entrypoints now use current Claude Code tool names (`Skill`, `WebSearch`, `WebFetch`) instead of the stale `Task` naming

## What xlfg should be

A serious but lean SDLC exoskeleton for Claude Code:

- one public invocation
- hidden phase skills loaded just in time
- one run card (`spec.md`)
- deterministic recall
- explicit proof
- optional research
- proportional review
- durable compounding only when verified

## Product truths to preserve

- `/xlfg` should execute the entire workflow itself. Do not make the user run phase commands or hidden skills.
- The right structure is **public entrypoint + hidden phase skills**, not a public command chain and not a single giant prompt.
- `spec.md` is the single source of truth; optional docs exist only when they change a decision.
- The helper CLI is optional but valuable. When available, the main entrypoint should prefer it for scaffold sync, run creation, recall, and verification.
- The plugin form is for team reuse and therefore namespaced.
- The standalone `.claude/skills/` pack is the best short-name UX and must include the hidden phase skills too.

## Main files to understand first

1. `plugins/xlfg-engineering/commands/xlfg.md`
2. `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md`
3. `standalone/.claude/skills/xlfg/SKILL.md`
4. `xlfg/runs.py`
5. `xlfg/verify.py`
6. `xlfg/audit.py`
7. `tests/test_xlfg.py`

## Regression triggers

Treat any of the following as regressions:

- `/xlfg` asking the user to run or sequence internal phase commands or hidden skills
- removing the hidden phase skills and collapsing everything back into one monolithic prompt
- shipping a plugin command and plugin skill with the same slash name
- commands or skills that reference `plugins/xlfg-engineering/...` as if that path exists inside the target repo
- reintroducing the stale `Task` tool naming in entrypoints
- plugin support skills cluttering the slash menu instead of staying hidden helpers
- reintroducing duplicated planning state that competes with `spec.md`
- claiming green without scenario-targeted proof
