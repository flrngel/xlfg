# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
