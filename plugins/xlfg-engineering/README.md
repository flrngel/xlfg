# xlfg-engineering (Claude Code plugin)

`xlfg-engineering` is a **skill-first autonomous SDLC harness** for modern Claude Code.

The design target in 2.2.0 is simple:

> **One invocation, one owner, one run card.** Claude Code should execute the full SDLC itself, while xlfg adds only the structure that increases trust.

## What changed in 2.2.0

- **Skills-first UX**: the primary entrypoint is now the skill `/xlfg-engineering:xlfg`.
- **Direct `/xlfg` support**: a standalone pack now ships in `standalone/.claude/skills/xlfg/` for users who want the short command name.
- **Autonomous macro**: `/xlfg` no longer asks the human to run phase subcommands or approve internal phase transitions.
- **Lean artifact model**: the run now starts with six core files, with `spec.md` as the single source of truth.
- **Consent reduction**: the main skill and command use `allowed-tools`, and the plugin includes a narrow `ExitPlanMode` auto-approval hook.
- **Claude Code 2026 alignment**: namespaced plugin skills, standalone short-name skills, hooks, and `effort` frontmatter are all supported.

## Quick start

### Plugin form (shared / team use)

Install the plugin and run:

- `/xlfg-engineering:xlfg "fix the login timeout flow"`

### Standalone form (short `/xlfg` command)

Copy `standalone/.claude/skills/xlfg/` into your target repo’s `.claude/skills/xlfg/`, then run:

- `/xlfg "fix the login timeout flow"`

This matches current Claude Code guidance: use **plugins** for shared reusable distributions and **standalone `.claude/`** when you want short skill names.

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

## Manual phase commands

These remain available as escape hatches, but they are no longer the normal UX:

- `/xlfg-engineering:xlfg:plan`
- `/xlfg-engineering:xlfg:implement`
- `/xlfg-engineering:xlfg:verify`
- `/xlfg-engineering:xlfg:review`
- `/xlfg-engineering:xlfg:compound`

## Philosophy

- Claude Code stays the orchestrator.
- `spec.md` carries PM / UX / Engineering / QA truth in one place.
- Verification must prove the changed behavior, not just produce green-looking motion.
- Extra docs and extra agents are optional, not the default.
