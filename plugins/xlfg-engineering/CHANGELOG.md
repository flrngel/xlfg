# Changelog

## 2.0.3 - 2026-03-06

### Added
- Deterministic `xlfg recall` CLI command over shared knowledge, role memory, the append-only ledger, migrations, and local runs.
- New `/xlfg:recall` plugin command and `xlfg-recall` skill.
- New scaffolded durable memory files: `docs/xlfg/knowledge/ledger.jsonl`, `docs/xlfg/knowledge/ledger.md`, and `docs/xlfg/knowledge/queries.md`.
- New `memory-recall.md` run artifact seeded for every run.

### Changed
- `/xlfg:plan` now performs stage-aligned memory recall before broad repo investigation.
- `/xlfg:compound` now appends structured immutable memory events to `ledger.jsonl`.
- Certain specialists now read and write stage-aligned memory rather than relying on one global summary blob.
- `xlfg recall` now supports `--file` and stdin (`--file -`) for multi-line typed query documents.

### Intentionally omitted
- Vector search, HyDE, LLM query expansion, and reranker-driven recall were kept out of xlfg's core path to preserve determinism and auditability.


## 2.0.2 - 2026-03-03

### Fixed
- `prepare` / `status` now clearly separate **installed xlfg version** from **repo scaffold version**.
- Legacy `docs/xlfg/metadata.json` is now recognized during migration and normalized to the canonical `docs/xlfg/meta.json` manifest.
- Version reports now include the **source file and key** used for repo scaffold detection to avoid stale-file confusion.

### Changed
- Migration notes now cover the metadata normalization step.
- Tests now cover legacy metadata migration and explicit installed-vs-repo version reporting.

## 2.0.1 - 2026-03-03

### Added
- New `/xlfg:prepare` command for fast scaffold/version checks and migration-on-drift.
- New `docs/xlfg/meta.json` scaffold manifest.
- New `docs/xlfg/migrations/` notes for version transitions.
- New `docs/xlfg/knowledge/agent-memory/` role memory files for high-value subagents.

### Changed
- `/xlfg` now runs `prepare → plan → implement → verify → review → compound`.
- `/xlfg:init` is now a manual bootstrap/repair path rather than a mandatory first step in the main macro.
- `docs/xlfg/runs/` is now treated as **local episodic evidence** and gitignored by default.
- README / skill docs now clarify tracked knowledge vs local run evidence.
- Scaffold and templates now emphasize state / transition UX contracts and disconfirming probes.

### Why
- Reduce wasted time on repeated scaffold bootstrapping.
- Keep repositories cleaner by tracking durable knowledge, not every run artifact.
- Allow specific subagents to accumulate compact, role-aligned memory without bloating shared prompts.

## 2.0.0 - 2026-03-03

### Breaking changes
- Removed `/lfg` and `/slfg` from the plugin. `/xlfg` is now the only top-level workflow command.
- Reworked `/xlfg` into a macro that explicitly chains `/xlfg:init`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, and `/xlfg:compound`.

### Added
- New `/xlfg:plan` command for diagnosis-first planning.
- New `/xlfg:implement` command for bounded implementation loops.
- New planning agent `xlfg-root-cause-analyst`.
- New planning agent `xlfg-solution-architect`.
- New implementation agent `xlfg-test-implementer`.
- New run artifacts: `diagnosis.md` and `solution-decision.md`.

### Changed
- Planning now requires explicit diagnosis, root-solution choice, and rejected shortcut documentation before coding.
- Implementation now uses specified agents instead of vague freeform execution.
- Review is explicitly positioned as a confirmation gate, not a cleanup phase.
- Scaffolded files and docs now reflect diagnosis-first execution.

### Kept
- Layered verification with evidence capture.
- Environment doctoring and harness memory.
- File-based compounding into durable knowledge.
