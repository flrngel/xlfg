# Changelog

## 2.4.1

- Added a project-level `.claude/skills/xlfg/SKILL.md` wrapper so `/xlfg` invokes `/xlfg-engineering:xlfg`.

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
