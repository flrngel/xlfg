---
description: Internal xlfg phase skill. Turn intent + context into a concrete plan with a falsifiable proof contract and a risk pass.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Skill(xlfg-engineering:xlfg-solution-architect *), Skill(xlfg-engineering:xlfg-test-strategist *), Skill(xlfg-engineering:xlfg-task-divider *), Skill(xlfg-engineering:xlfg-risk-assessor *), Skill(xlfg-engineering:xlfg-root-cause-analyst *), Skill(xlfg-engineering:xlfg-ui-designer *), Skill(xlfg-engineering:xlfg-test-readiness-checker *), Skill(xlfg-engineering:xlfg-brainstorm *)
---

# xlfg-plan-phase

Use only during `/xlfg` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

Turn what you now know into a concrete, falsifiable sequence of changes with a proof contract.

## Lens

You are a solution architect, a test strategist, a risk assessor, and (when the task touches UI) a UX designer. Each is a separate pass.

## How to work it

- **Solution choice.** If more than one approach is plausible, compare them briefly — 3–5 bullets, not an essay. Pick the smallest honest fix. Name the main tradeoff out loud. "Smallest honest" beats "most correct in theory" when both satisfy the contract.
- **Task split.** Divide the work into **coherent decision slices**, not atomic one-line edits. Prefer one slice per objective group. Many tiny packets create parallel divergent decisions that conflict at merge; one owner per decision is cleaner.
- **Test contract.** Before you write any source code, declare the proof. Every claim in the intent contract needs a cheap honest check:
  - `fast_check` — runs in seconds, covers the core behavior. You always run this.
  - `smoke_check` — runs in under a minute, covers the primary failure mode. Run before declaring done on non-trivial changes.
  - `ship_check` — the full suite and/or live integration. Run when the change touches shared surfaces or before you claim "ready to ship."
- **Test readiness gate.** Re-read your test contract with a skeptical eye. If any scenario in your intent contract has no matching proof step, the plan is not READY. Repair the plan until every contract bullet has a matching check.
- **Risk pass.** What could this break that isn't obvious? Migrations, auth, data loss, silent drift, performance cliffs. If a risk is real, name the rollback path.
- **UI pass (only if the task touches UI).** Who uses this? What's the happy path? What are the 2–3 most likely edge cases (empty state, error state, slow network)? What are the a11y requirements (keyboard, screen reader, contrast)?

## Done signal

You have:
- a one-paragraph description of the change,
- an ordered list of files you'll edit and why,
- a test contract that covers every correctness-critical bullet from intent,
- a named rollback path if the change is risky.

## Stop-traps

- Deferring the test contract to "after I code." That's a coding plan, not an engineering plan. Write proof first.
- Tests that assert implementation ("the function calls X") rather than behavior ("the user can do Y"). Behavior tests survive refactors; implementation tests punish them.
- Planning for hypothetical future requirements. YAGNI. Three similar lines beats a premature abstraction.
- Over-specifying a recipe for yourself. The plan is a contract with the proof, not a transcription of the code you're about to write.

## Optional specialist skills

These hidden lens skills can be loaded on-demand via the `Skill` tool when the corresponding plan pass is non-trivial. Load at most 1–2 per run; loading all of them is almost never the right move.

- `xlfg-engineering:xlfg-solution-architect` — solution choice when more than one fix is plausible and the layer/shape matters.
- `xlfg-engineering:xlfg-root-cause-analyst` — when the diagnosis isn't settled and the chosen fix depends on which mechanism is correct.
- `xlfg-engineering:xlfg-test-strategist` — test contract design when the change spans multiple tiers of the harness.
- `xlfg-engineering:xlfg-task-divider` — task split when the change touches more than one surface and ordering matters.
- `xlfg-engineering:xlfg-risk-assessor` — risk pass when the change touches durable state, auth, data, or hot paths.
- `xlfg-engineering:xlfg-ui-designer` — UI pass only when the change produces pixels.
- `xlfg-engineering:xlfg-test-readiness-checker` — the final readiness gate: every spec bullet maps to a check, every check to a bullet.
- `xlfg-engineering:xlfg-brainstorm` — when one approach is dominating the plan and you want a sanity check against alternatives.
