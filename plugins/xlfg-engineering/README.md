# xlfg-engineering

`xlfg-engineering` is an autonomous SDLC harness for modern Claude Code and Codex.

The 3.2.0 Codex surface adds `.codex-plugin/plugin.json`,
repo-scoped marketplace metadata, and two public Codex skills: `$xlfg` and
`$xlfg-debug`. The Codex skills live under `codex/skills/` and use shared phase
references under `codex/references/phases/` so the existing Claude command and
hidden-skill model remains unchanged.

The 2.9.0 design target is simple:

> **One public entrypoint, one run card, one intent contract, hidden phase skills loaded just in time, and specialist subagents that actually own their lanes — under a generous turn-budget ceiling so prompt-side write-first rules carry the forcing-function load.**

## What changed in 5.0.0

**Major: agent preamble + dispatch-rules extraction; cache-stable prefix; epic-default packets; decision-bearing CONTEXT_DIGEST.**

- New `agents/_shared/agent-preamble.md` owns the single authoritative copy of the 7 boilerplate sections (compatibility, execution contract, turn budget, tool failure recovery, ARTIFACT_KIND, completion barrier, final response contract). All 27 specialist files shrunk to role-delta only — each references the preamble rather than duplicating ~70 lines of identical boilerplate. Net per-agent file size −60% to −70%.
- New `agents/_shared/dispatch-rules.md` owns the delegation packet contract. All 6 phase skills replaced their near-identical ~40-line "Delegation packet rules" block with a pointer.
- Prompt caching win: the shared preamble is a **cache-stable prefix**. Prior per-agent boilerplate broke caching entirely (27 near-identical variants).
- New packet-size ladder (`trivial` / `standard` / `epic` / `split`). `xlfg-task-divider` now defaults to **epic** (one packet per objective group `O1`, `O2`, ...) — fewer but larger packets, matching Anthropic's finding that coding tasks have fewer parallelizable sub-problems than research. Atomic sub-division only when surfaces are truly unrelated.
- `CONTEXT_DIGEST` now carries **decisions + rationale + path refs**, not just raw facts. Forbidden: digest + re-read; specialists pull scoped file:line ranges on demand instead of re-reading canonical files the digest already summarized.
- Tests migrated to match: boilerplate assertions now check the preamble + agent references; packet-contract assertions accept either inlined contract or reference to `_shared/dispatch-rules.md`.

Research anchors: Anthropic's multi-agent research, effective context engineering, writing effective tools, building effective agents, and prompt caching posts; Cognition's *Don't Build Multi-Agents* ("share decisions, not just facts").

Deferred: agent merges (3 context investigators → 1; `xlfg-test-readiness-checker` → `xlfg-test-strategist`) and full optional-artifact collapse — tracked for a follow-up release to limit test-assertion churn.

## What changed in 4.6.0

- Dispatch packets now carry a micro-packet discipline: short contract, constraints, scoped evidence anchors, and proof signal, not long code excerpts or line-by-line implementation scripts.
- Task `DONE_CHECK` guidance now uses a proof budget. Task packets should run the cheapest honest local check; broad build/full-suite/live acceptance belongs to verify-phase `fast_check`, `smoke_check`, or `ship_check` unless the task is an integration lane.
- Conductors now compact specialist artifacts before updating canonical run files. Promote status, verdict, changed files, command results, blockers, and next action; leave full reports and logs in the lane artifact.
- `xlfg-task-implementer` now refuses out-of-scope repairs when a `DONE_CHECK` fails because of an unrelated file, fixture, test, hook, or dependency.
- The Codex `$xlfg` and `$xlfg-debug` skills carry the same micro-packet and compaction guidance.

## What changed in 4.5.0

- Sub-agent dispatch packets now require `OWNERSHIP_BOUNDARY` in addition to `CONTEXT_DIGEST` and `PRIOR_SIBLINGS`.
- The conductor and every delegating phase skill now state what each lane owns, what it must not redo, and which artifacts it consumes before dispatch.
- High-overlap lanes are explicitly separated: flow/spec vs test proof, UI design vs UX review, source implementation vs test implementation, task checking vs verification, and verify runner vs reducer.
- All 27 specialist agents now honor the ownership boundary and use a `Covered elsewhere` pointer rather than repeating adjacent-lane analysis.
- The Codex `$xlfg` and `$xlfg-debug` skill packet shapes now carry the same dedup fields.

## What changed in 4.4.0

- Sub-agent dispatch packets now require two new mandatory fields — `CONTEXT_DIGEST` (canonical excerpts the specialist needs) and `PRIOR_SIBLINGS` (artifacts already produced in the same phase lane that overlap the specialist's surface).
- Defined once in `agents/_shared/output-template.md`; enforced by the conductor (`commands/xlfg.md`) and every delegating phase skill (`intent`, `context`, `plan`, `implement`, `verify`, `review`, `debug`).
- All 27 specialist agents updated to honor both fields: trust the digest over re-reading canonical files, skim listed siblings to skip ground already covered.
- Net effect: specialists stop re-reading the same `spec.md` / `context.md` / `verification.md` for each lane, and sibling specialists in the same phase build on each other instead of re-deriving overlapping findings.

## What changed in 3.3.0

- `/xlfg-init` and `/xlfg-audit` are back as manual maintenance commands after being swept up in the v3.0.0 CLI removal.
- `/xlfg-init` is an idempotent scaffold repair: creates missing xlfg directories and durable knowledge skeletons without overwriting, and ensures `.gitignore` has the canonical xlfg ignore set.
- `/xlfg-audit` is a deterministic harness self-audit: version sync across the three plugin manifests, SDLC phase coverage, workflow load (word counts), Claude Code compatibility, and Codex surface integrity. No Python; no network.
- `/xlfg` and `/xlfg-debug` behavior is unchanged.

## What changed in 2.7.1

- `/xlfg-engineering:xlfg` stays the single public plugin entrypoint, and this baseline keeps the short `/xlfg` alias through `name: xlfg` on the plugin command.
- The batch still includes the mandatory **intent phase**, but now the next weak layer is hardened too: specialist agents have stronger personas, explicit tool allowlists, and foreground-only bias.
- Specialists stay leaf-only and bounded by a generous safety ceiling (`maxTurns: 150`), with prompt-side write-first rules carrying the forcing-function load so a bad lane gets re-split rather than drifting silently.
- Review specialists now write their own artifacts under `reviews/`, so the conductor synthesizes from real expert output instead of vague subagent summaries.
- Audit, lint, docs, and tests now check proactive specialist descriptions, explicit tool scopes, and artifact-writing review lanes.
## Quick start

### Plugin form (shared / team use)

Install the plugin and run:

- `/xlfg-engineering:xlfg "fix the login timeout flow"`

### Codex form

Install `xlfg-engineering` from the repo marketplace at
`.agents/plugins/marketplace.json`, then run:

- `$xlfg "fix the login timeout flow"`
- `$xlfg-debug "diagnose the failing login timeout flow"`

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
- Specialists use bounded `maxTurns` budgets, restoring the intended short-lived specialist behavior.
- Review fan-out is leaner by default, and packet waiting is documented as artifact-first rather than chat-first.


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.


## 2.7.2 hardening note

The plugin build now ships a plugin-level `SubagentStop` guard. In plugin mode, xlfg specialists are not allowed to stop on setup chatter or missing artifacts; the hook blocks the stop once and forces the specialist to finish the promised artifact or write an explicit `BLOCKED` / `FAILED` artifact instead.

## 2.7.3 turn-budget fix

Production testing found agents exhausting their 8-turn budget on speculative reads and never writing artifacts. Fix: raised maxTurns to 12 for review and heavy-analysis agents, added a "Turn budget rule" to all 26 specialists enforcing write-first behavior, replaced the bloated 14-file "Read first" lists in review agents with lean 3+3 context blocks, removed the `stopHookActive` escape hatch from the stop guard, and added `CONTEXT_DIGEST` to the review-phase dispatch protocol.
