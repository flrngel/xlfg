# Changelog

## 2.2.0 - 2026-03-23

### Changed
- Rebuilt xlfg around the **current Claude Code skills model**. The main entrypoint is now a real `xlfg` skill, with legacy commands kept only as compatibility shims.
- `/xlfg` now runs the full SDLC **autonomously in one invocation** instead of asking the human to sequence phase commands.
- Collapsed duplicated planning state into a lean six-file core. `spec.md` is now the single source of truth for request truth, why, harness choice, solution, task map, and proof summary.
- Added a **standalone `.claude/skills/xlfg/` pack** so users can install a direct `/xlfg` command without plugin namespacing.
- Added `allowed-tools` to the main skill and legacy shim to reduce permission churn while `/xlfg` is active.
- Added a narrow plugin hook that auto-approves `ExitPlanMode`, removing a common extra consent step without broadly weakening permissions.
- Added `effort` frontmatter on the main workflow and escape-hatch commands.
- Updated the audit model to score **Claude Code compatibility** in addition to workflow load and SDLC coverage.
- Updated benchmarking guidance for a skill-first, autonomy-first xlfg.

### Why
- The user reported that xlfg still asked for too much consent, duplicated too much state, and confused recent Claude Code behavior.
- Official Claude Code guidance now clearly favors skills, hooks, namespaced plugins, standalone short-name skills, and aggressive context control.

## 2.1.0 - 2026-03-19

### Changed
- Reframed `/xlfg` as a **thin SDLC macro** that should complement Claude Code instead of competing with it.
- `/xlfg:plan` now distinguishes **always-on artifacts** from **optional artifacts**, adds a first-class **research lane**, and treats `spec.md` as the run card for PM / Engineering / QA.
- `/xlfg:implement` now starts from the run card plus proof docs instead of front-loading every run artifact, and it uses **adaptive subagent budgets** instead of routine test+implement+checker fan-out on every task.
- `/xlfg:review` now has an explicit **lens budget** tied to harness profile and changed surface.
- Added `/xlfg:audit` command plus `xlfg audit` CLI support.
- Added `docs/benchmarking.md` describing both deterministic harness audit and live Claude Code A/B evaluation.
- Synced plugin manifest versions with the package version.
- Moved several read-only/mapping agents to lighter models.

### Why
- The user reported that `/xlfg` still felt worse than strong vanilla Claude Code because workflow load, fan-out, and artifact sprawl could outweigh the trust gains.
- Recent work on coding-agent evaluation reinforces the same lesson: better proof and better planning are good, but excessive skills, prompt load, and orchestration overhead can cancel out the benefit.
