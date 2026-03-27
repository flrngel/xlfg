# xlfg-engineering (Claude Code plugin)

`xlfg-engineering` is an autonomous SDLC harness for modern Claude Code.

The 2.6.0 design target is simple:

> **One public entrypoint, one run card, one intent contract, hidden phase skills loaded just in time, and specialist subagents that actually own their lanes.**

## What changed in 2.6.0

- `/xlfg-engineering:xlfg` stays the single public plugin entrypoint, and this baseline keeps the short `/xlfg` alias through `name: xlfg` on the plugin command.
- The batch still includes the mandatory **intent phase**, but now the next weak layer is hardened too: specialist agents have stronger personas, explicit tool allowlists, and foreground-only bias.
- Review specialists now write their own artifacts under `reviews/`, so the conductor synthesizes from real expert output instead of vague subagent summaries.
- The standalone pack now mirrors plugin agents under `.claude/agents/` for parity with the skill pack.
- Audit, lint, docs, and tests now check proactive specialist descriptions, explicit tool scopes, artifact-writing review lanes, and standalone agent parity.
- `xlfg eval-intent` remains in place, so intent quality and subagent hardening can both be measured instead of hand-waved.

## Quick start

### Plugin form (shared / team use)

Install the plugin and run:

- `/xlfg-engineering:xlfg "fix the login timeout flow"`

### Standalone form (short `/xlfg` command)

Copy the full `standalone/.claude/` directory into your target repo’s `.claude/`, then run:

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
