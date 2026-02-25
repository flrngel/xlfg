# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-02-25

### Changed
- Added **must-spawn agents per tier** table — defines non-negotiable minimum agent spawns for each tier (S/M/L), replacing advisory-only skip guidance.
- **Checker agent is now explicitly mandatory at all tiers.** Added CRITICAL callout in Phase 5: the lead must NEVER write checker reports itself.
- **Phase 2 (context expansion):** Now skipped for both Tier S and M (only L spawns investigators). Lead assesses context directly for normal features.
- **Phase 3 (planning):** Tier M now spawns only `xlfg-spec-author` (independent spec). Lead writes plan directly. Skip repo-mapper, test-strategist, risk-assessor.
- **Phase 5 (implementation):** Tier S/M lead may implement directly and write implementer reports, but must always spawn the checker agent.
- **Phase 6 (verification):** Tier S lead may run commands inline. Tier M/L must spawn verify-runner + verify-reducer.
- **Phase 7 (review):** Tier S may skip review agents. Tier M must spawn security + architecture reviewers. Tier L spawns all four.

### Added
- **Knowledge flywheel**: `xlfg-spec-author` now reads `docs/xlfg/knowledge/` (patterns, decisions, testing) before writing spec. Compound writes → spec reads → knowledge compounds.
- **System-wide test check** in `xlfg-task-checker`: 5 questions (what fires, real chains vs mocks, orphaned state, other interfaces, error alignment) before issuing ACCEPT.
- **Protected artifacts rule** in security + architecture reviewers: never flag `docs/xlfg/` for deletion/cleanup.
- **Post-deploy monitoring required** in Phase 8 run-summary (or explicit "No monitoring needed: [reason]").

### Fixed
- Addressed "tier rationalization" anti-pattern where the lead downgrades tier classification to skip all agents. The must-spawn table makes minimum requirements unambiguous.
- Closed broken flywheel: compound phase was write-only (knowledge never queried in subsequent runs).

## [0.7.1] - 2026-02-25

### Changed
- Made `/xlfg` explicitly self-contained: it now performs init/verify/review/compound steps inline instead of requiring subcommand chaining.
- Added run-tier guidance (S/M/L) to reduce unnecessary parallelism and keep plans coarse.
- Hardened verification guidance against common hang modes (watch/interactive runners) and added `CI=1` recommendation.

## [0.7.0] - 2026-02-22

### Changed
- Reordered `/xlfg` phases so `/xlfg:compound` is now the strict final phase.
- Kept compounding mandatory for completion while moving ship before final compound execution.

## [0.6.0] - 2026-02-22

### Changed
- Made `/xlfg:review` verification-aware: reviewers now read verification artifacts, report net-new issues, and explain why verification missed them.
- Added selective review fan-out in `/xlfg:review` to skip non-relevant performance/UX reviewers.
- Added reducer deduplication guidance in `/xlfg:review` by `(file, line/area, issue class)`.
- Made compounding a hard gate in `/xlfg` before final ship completion.
- Updated `/xlfg:compound` to capture durable testing knowledge and write `compound-summary.md`.
- Updated `/xlfg:init` scaffolding with `docs/xlfg/knowledge/testing.md`.
- Updated `xlfg-test-strategist` to reuse `docs/xlfg/knowledge/testing.md`.

## [0.5.0] - 2026-02-22

### Added
- New verify subagents:
  - `xlfg-verify-runner`
  - `xlfg-verify-reducer`

### Changed
- Refactored `/xlfg:verify` into a map/reduce verification pipeline driven by subagent handoffs.
- Added canonical `verify-fix-plan.md` output for red verification runs.
- Updated README agent inventory to include verify agents.

## [0.4.0] - 2026-02-22

### Changed
- Removed pre-implementation approval pauses in `/xlfg`; runs now auto-continue from plan to implementation.
- Clarified that user questions are only asked for true blocking ambiguity or safety-gated confirmations.
- Updated context-expansion behavior to defer unapproved scope expansions to backlog instead of blocking implementation.
- Updated wrappers and docs to reflect no-pause default behavior.

## [0.3.0] - 2026-02-22

### Changed
- Made paired implementation mandatory in `/xlfg`: every plan task now runs through `xlfg-task-implementer` + `xlfg-task-checker`.
- Updated `/xlfg` completion criteria to require implementer/checker reports with `Verdict: ACCEPT` for every task.
- Updated `lfg` and `slfg` wrappers to require implementer/checker pairs for all implementation tasks.
- Updated README and quality/file-context skills to reflect mandatory pair-mode implementation.

## [0.2.0] - 2026-02-22

### Added
- New context-expansion investigation agents for adjacent requirements, constraints, and unknowns:
  - `xlfg-context-adjacent-investigator`
  - `xlfg-context-constraints-investigator`
  - `xlfg-context-unknowns-investigator`
- New implementation pair agents:
  - `xlfg-task-implementer`
  - `xlfg-task-checker`

### Changed
- Updated `/xlfg` workflow with a new Phase 2 context-expansion step before planning.
- Updated implementation phase to lead-orchestrated adaptive pair mode for medium/high-risk tasks.
- Updated `lfg` and `slfg` guidance to reflect context expansion and pair loops.
- Expanded file-context and quality-gate skills to include context artifacts and checker reports.

## [0.1.2] - 2026-02-20

### Changed
- Use `sonnet` as the explicit model for all `/xlfg` planning and review subagents.

## [0.1.1] - 2026-02-20

### Changed
- Set all `/xlfg` planning and review subagents to an explicit Sonnet model instead of inheriting the parent model.

## [0.1.0] - 2026-02-20

### Added
- Initial release of `/xlfg` (Extreme LFG) end-to-end SDLC workflow
- `/lfg` and `/slfg` wrappers for sequential and swarm modes
- `/xlfg:init`, `/xlfg:verify`, `/xlfg:review`, `/xlfg:compound`
- File-based context knowledge base under `docs/xlfg/` and ephemeral logs under `.xlfg/`
- Planning + review agents and core skills
