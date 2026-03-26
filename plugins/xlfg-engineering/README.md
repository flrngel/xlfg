# xlfg-engineering (Claude Code plugin)

`xlfg-engineering` is an autonomous SDLC harness for modern Claude Code.

The 2.5.1 design target is simple:

> **One public entrypoint, one run card, one intent contract, hidden phase skills loaded just in time.**

## What changed in 2.5.1

- `/xlfg-engineering:xlfg` still stays the single public plugin entrypoint, and this baseline keeps the short `/xlfg` alias through `name: xlfg` on the plugin command.
- The batch now includes a mandatory **intent phase** before broad repo fan-out.
- `spec.md` is now the only active home for the intent contract and objective groups.
- Bundled / messy prompts are split into explicit objective groups with assumptions or blockers called out early.
- `xlfg eval-intent` scores real run artifacts against fixtures so bad prompts can be measured instead of hand-waved.
- Support skills remain hidden background helpers instead of cluttering the slash menu.

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
- `spec.md` carries the intent contract plus PM / UX / Engineering / QA truth in one place.
- Verification must prove changed behavior, not just produce green-looking motion.
- Extra docs and extra agents are optional, not the default.


Reference intent fixtures ship in `evals/intent/`, and `xlfg eval-intent --suite-dir evals/intent` scores the bundled example artifacts out of the box.
