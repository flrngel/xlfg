# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-01

### Added
- **Behavior-contract-first workflow**: `/xlfg` now requires `flow-spec.md`, `test-contract.md`, and `env-plan.md` before implementation starts.
- **Step-level run scorecard**: runs now maintain `scorecard.md` as the shared status view for new requirements and regressions.
- **Environment doctor**:
  - new planning agent `xlfg-env-doctor`
  - new CLI command `xlfg doctor`
  - best-effort dev-server reuse, port/health checks, and duplicate-server avoidance
- New durable knowledge files:
  - `ux-flows.md`
  - `failure-memory.md`
  - `harness-rules.md`
- New CLI support for layered verification inputs:
  - `smoke`
  - `e2e`
  - `dev` contract in `commands.json`

### Changed
- `/xlfg` now starts by defining **what to build**, **what to test**, and **how the environment runs** before coding.
- `/xlfg:verify` now describes layered verification: fast → smoke → e2e → broader regression.
- `xlfg-spec-author` now writes a real flow contract rather than a vague spec.
- `xlfg-test-strategist` now writes `test-contract.md` instead of a late generic test plan.
- Implementer / checker / reviewer prompts now read the shared contracts.
- Compounding now updates failure memory and harness rules, not just patterns / decisions.
- CLI verification now writes `verify-fix-plan.md` on failure.

### Fixed
- Reduced the common hackathon failure mode where the workflow burns time on unexpected environment issues (duplicate `yarn dev`, stale servers, port conflicts, watch-mode hangs).
- Shifted testing earlier so verification is not a naive afterthought.
- Made compounding more operational: repeated real failures can now become durable prevention rules.

## [0.9.0] - 2026-02-25

### Added
- **Phase 1.5 — Brainstorm** (conditional): When the request is ambiguous, spawns `xlfg-brainstorm` agent to explore WHAT to build (2–3 approaches with tradeoffs) before planning HOW. Triggers on exploratory language or missing acceptance criteria. Skips automatically for clear bugfixes/features.
- **`xlfg-brainstorm` agent**: Inspects codebase + knowledge files, proposes concrete approaches with effort estimates, recommends one with rationale. Designed for < 2 minute exploration.
- **`xlfg-researcher` agent**: External research via WebSearch + Context7 MCP (framework docs). Focuses on common pitfalls, security patterns, migration gotchas, and performance traps specific to the current task.
- **Research decision gate in Phase 3**: Intelligent decision about when to spawn researcher — always for security/payments/external APIs, skip for simple bugfixes, conditional for uncertain domains.

### Changed
- Phase 3 Tier M now spawns `xlfg-researcher` conditionally (high-risk/unfamiliar domains).
- Phase 3 Tier L now always spawns `xlfg-researcher` alongside other planning agents.
- Phase 4 (Reduce) now reads `brainstorm.md` and `research.md` if present.
- Must-spawn table updated with `xlfg-brainstorm` (if ambiguous) and `xlfg-researcher` (conditional/spawn).
- Minimum agent counts updated: Tier M = 6–7, Tier L = 15+.

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
