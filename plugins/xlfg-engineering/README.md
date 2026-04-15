# xlfg-engineering (Claude Code plugin)

`xlfg-engineering` is an autonomous SDLC harness for modern Claude Code.

The 2.9.0 design target is simple:

> **One public entrypoint, one run card, one intent contract, hidden phase skills loaded just in time, and specialist subagents that actually own their lanes — under a generous turn-budget ceiling so prompt-side write-first rules carry the forcing-function load.**

## What changed in 2.7.1

- `/xlfg-engineering:xlfg` stays the single public plugin entrypoint, and this baseline keeps the short `/xlfg` alias through `name: xlfg` on the plugin command.
- The batch still includes the mandatory **intent phase**, but now the next weak layer is hardened too: specialist agents have stronger personas, explicit tool allowlists, and foreground-only bias.
- Specialists stay leaf-only and bounded by a generous safety ceiling (`maxTurns: 150`), with prompt-side write-first rules carrying the forcing-function load so a bad lane gets re-split rather than drifting silently.
- Review specialists now write their own artifacts under `reviews/`, so the conductor synthesizes from real expert output instead of vague subagent summaries.
- The standalone pack now mirrors plugin agents under `.claude/agents/` for parity with the skill pack.
- Audit, lint, docs, and tests now check proactive specialist descriptions, explicit tool scopes, artifact-writing review lanes, and standalone agent parity.
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


## 2.7.5 note

- The conductor and phase skills now explicitly forbid nested specialist delegation; only the conductor may fan out work.
- Plugin and standalone agent packs are back in sync on `maxTurns`, restoring the intended short-lived specialist behavior.
- Review fan-out is leaner by default, and packet waiting is documented as artifact-first rather than chat-first.


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.


## 2.7.2 hardening note

The plugin build now ships a plugin-level `SubagentStop` guard. In plugin mode, xlfg specialists are not allowed to stop on setup chatter or missing artifacts; the hook blocks the stop once and forces the specialist to finish the promised artifact or write an explicit `BLOCKED` / `FAILED` artifact instead.

## 2.7.3 turn-budget fix

Production testing found agents exhausting their 8-turn budget on speculative reads and never writing artifacts. Fix: raised maxTurns to 12 for review and heavy-analysis agents, added a "Turn budget rule" to all 26 specialists enforcing write-first behavior, replaced the bloated 14-file "Read first" lists in review agents with lean 3+3 context blocks, removed the `stopHookActive` escape hatch from the stop guard, and added `CONTEXT_DIGEST` to the review-phase dispatch protocol.
