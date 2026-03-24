# xlfg-engineering (Claude Code plugin)

`xlfg-engineering` is an autonomous SDLC harness for modern Claude Code.

The 2.3.0 design target is simple:

> **One entrypoint, one owner, one run card.**

## What changed in 2.3.0

- The plugin now exposes `/xlfg-engineering:xlfg` as a **single self-contained entrypoint**.
- The broken command→skill indirection was removed.
- The colliding plugin `skill + command` pair named `xlfg` was removed.
- Support skills remain, but they are now background helpers instead of primary user-facing entrypoints.
- The standalone pack still ships the short `/xlfg` command for project-local installs.

## Quick start

### Plugin form (shared / team use)

Install the plugin and run:

- `/xlfg-engineering:xlfg "fix the login timeout flow"`

### Standalone form (short `/xlfg` command)

Copy `standalone/.claude/skills/xlfg/` into your target repo’s `.claude/skills/xlfg/`, then run:

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
- `spec.md` carries PM / UX / Engineering / QA truth in one place.
- Verification must prove changed behavior, not just produce green-looking motion.
- Extra docs and extra agents are optional, not the default.
