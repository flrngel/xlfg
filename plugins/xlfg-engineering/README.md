# xlfg-engineering (Claude Code plugin)

`xlfg-engineering` is an autonomous SDLC harness for modern Claude Code.

The 2.4.0 design target is simple:

> **One public entrypoint, one run card, hidden phase skills loaded just in time.**

## What changed in 2.4.0

- `/xlfg-engineering:xlfg` is still the single public plugin entrypoint.
- The entrypoint now **batches separated hidden skills** for recall, context, plan, implement, verify, review, and compound.
- The standalone pack now ships the same hidden phase skills, so short-name `/xlfg` behaves like the plugin entrypoint.
- The workflow now uses current Claude Code tool names such as `Skill`, `WebSearch`, and `WebFetch` instead of the stale `Task` naming.
- Support skills remain hidden background helpers instead of cluttering the slash menu.
- `spec.md` remains the single source of truth, so phase batching does not reintroduce duplicated planning files.

## Quick start

### Plugin form (shared / team use)

Install the plugin and run:

- `/xlfg-engineering:xlfg "fix the login timeout flow"`

### Standalone form (short `/xlfg` command)

Copy the full `standalone/.claude/skills/` directory into your target repo’s `.claude/skills/`, then run:

- `/xlfg "fix the login timeout flow"`

## Core files

Always-on run files:

- `context.md`
- `memory-recall.md`
- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`

Optional only when they add decision value:

- `research.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`
- `proof-map.md`
- `risk.md`
- `run-summary.md`
- `review-summary.md`
- `compound-summary.md`

## Philosophy

- Claude Code stays the orchestrator.
- `/xlfg` owns the full run and should not ask the human to run internal phases.
- Hidden phase skills are loaded just in time instead of being inlined into one monolithic entrypoint.
- `spec.md` carries PM / UX / Engineering / QA truth in one place.
- Verification must prove changed behavior, not just produce green-looking motion.
- Extra docs and extra agents are optional, not the default.
