## 2.8.0

- Added a Stop hook (`phase-gate.mjs`) on the main conductor that blocks the pipeline from ending before all 8 phases complete.
- Added phase-state tracking (`.xlfg/phase-state.json`) so the Stop hook and conductor know which phases have completed; survives context compaction.
- Capped verify-fix and review-fix loopback cycles at 2 iterations to prevent unbounded context growth; exceeding the cap escalates to the user.
- Registered the Stop hook in both plugin `hooks.json` and standalone/plugin conductor frontmatter.
- Added `conductor_stop_gate` feature detection to the audit module.

## 2.7.5

- Restored bounded specialist turn budgets in the plugin agent pack to match the standalone pack, so phase-critical lanes are foregrounded and short-lived again.
- Declared specialists to be leaf workers in the conductor and all delegating phase skills; nested subagent fan-out is now explicitly forbidden.
- Tightened fan-out guidance so context, planning, verification, and review stay sequential or lean by default, with review capped at one standard lens and two deep lenses.
- Clarified that waiting on a specialist is valid only when a preseeded `PRIMARY_ARTIFACT` and explicit `RETURN_CONTRACT` exist.
- Added audit and test coverage for short turn budgets, leaf-worker specialist tools, atomic packet headers across delegating entrypoints, and lean review fan-out.

## 2.7.3

- Fixed sub-agent turn-budget starvation: raised maxTurns from 8 to 12 for review and heavy-analysis planning agents, and to 10 for test-implementer and verify-reducer.
- Replaced the bloated "Read first" imperative lists in review agents with lean "Context sources" blocks, cutting speculative reads from 14 to 3 core files.
- Added a "Turn budget rule" section to every specialist's execution contract, enforcing write-first behavior and prohibiting speculative file reads.
- Removed the stopHookActive escape hatch from the SubagentStop guard so agents cannot bypass artifact completion after a single block.
- Added CONTEXT_DIGEST to the review-phase dispatch protocol so conductors embed pre-digested context instead of expecting reviewers to re-read everything.

## 2.7.2

- Added a plugin-level `SubagentStop` guard that blocks xlfg specialists from stopping on progress chatter or missing artifacts, using a bundled hook script instead of prompt text alone.
- Tightened the conductor and phase skills around artifact-first atomic packets: preseed the lane artifact, pass machine-readable `PRIMARY_ARTIFACT` / `FILE_SCOPE` / `DONE_CHECK` headers, and default planning lanes to sequential dispatch unless packets are truly independent.
- Hardened every specialist with explicit tool-error recovery rules so directory-read failures, oversized-file reads, and similar nonfatal errors are repaired in-lane instead of being surfaced as premature chat replies.
- Added tests and audit checks for the stop guard, packet header discipline, and plugin hook wiring.

## 2.7.1

- Hardened specialist completion with an explicit completion barrier: progress-only returns are not accepted as done.
- Added atomic task packets and the `xlfg-task-divider` planner so delegation uses one mission, one artifact, and one honest done check.
- Updated main and phase orchestration to resume the same specialist once before accepting failure or repairing the lane.

# Changelog

## 2.6.0

- Hardened specialist agents with clearer expert personas, explicit tool allowlists, proactive delegation descriptions, and `background: false` for phase-critical work.
- Updated the main `/xlfg` conductor and phase skills to treat specialists as lane owners whose artifacts should drive synthesis, not optional advisors.
- Added explicit artifact-writing review lanes under `docs/xlfg/runs/<run>/reviews/` so architecture, security, performance, and UX review can no longer vanish into summary-only subagent replies.
- Added standalone `.claude/agents/` parity for the standalone skill pack.
- Extended audit, lint, docs, and tests to score and enforce subagent hardening, foreground execution, review artifacts, and standalone agent parity.
- Kept the intent-contract improvements from 2.5.x intact while strengthening the next weak layer in the workflow.

## 2.4.0

- Restored the intended architecture: `/xlfg` now batches separated hidden phase skills instead of flattening the whole workflow into one monolithic prompt.
- Added hidden phase skills for recall, context, planning, implementation, verification, review, and compounding in both the plugin and standalone packs.
- Kept exactly one public plugin entrypoint (`/xlfg-engineering:xlfg`) and one public standalone entrypoint (`/xlfg`).
- Switched the entrypoints to current Claude Code tool names, using `Skill` orchestration plus `WebSearch` / `WebFetch` instead of the stale `Task` wording.
- Updated linting, audit rules, and tests to catch missing phase skills, stale tool names, and loss of batch-skill orchestration.
- Updated docs and handoff notes so future revisions preserve the public-entrypoint + hidden-phase-skills model.

## 2.3.0

- Fixed the broken `/xlfg` entrypoint introduced by 2.2.0.
- Removed the colliding plugin `command + skill` pair named `xlfg`.
- Removed the repo-relative command shim that pointed Claude at `plugins/xlfg-engineering/skills/xlfg/SKILL.md`.
- Made `/xlfg-engineering:xlfg` self-contained so the command itself executes the full SDLC workflow.
- Hid support skills from the slash menu so the main entrypoint is clearer.
- Kept the standalone `.claude/skills/xlfg/` pack as the canonical short `/xlfg` install.
- Updated linting, audit rules, and tests to catch entrypoint collisions and repo-relative plugin path references.

## 2.2.0

- Collapsed duplicated planning state into a lean six-file core. `spec.md` is now the single source of truth for request truth, why, harness choice, solution, task map, and proof summary.
- Added a first-class standalone `.claude/skills/xlfg/` pack so users can get direct `/xlfg` without plugin namespaces.
- Added `allowed-tools`, `effort`, and a narrow `ExitPlanMode` auto-approval hook to reduce internal workflow friction.
- Added `xlfg audit` plus `docs/benchmarking.md` to score workflow load, SDLC coverage, and Claude Code compatibility.
- Routed cheap/read-only helper agents to Haiku.

## 2.1.0

- Reworked `/xlfg:plan` to be why-first and progressively load optional agents.
- Reworked `/xlfg:implement` to use harness-profile budgets and maintain the workboard / proof map.
- Added a more explicit research lane, lean artifact model, and updated tests.
