# Changelog

## 2.0.6 - 2026-03-14

### Added
- New git/worktree detection module `xlfg/gitmeta.py` and `.xlfg/worktree.json` output.
- New knowledge layout module `xlfg/knowledge.py` for tracked cards/events and generated local `_views/`.
- New tracked knowledge docs: `service-context.md`, `write-model.md`, card READMEs, event README, and role-memory README scaffolds.
- New CLI commands: `xlfg worktree` and `xlfg knowledge rebuild`.
- New bundle design note `docs/branch-safe-knowledge.md`.

### Changed
- Shared knowledge and role memory now write to immutable branch-scoped cards instead of hot tracked rollup files.
- Immutable event files now replace the single tracked `ledger.jsonl` as the durable source of truth.
- `docs/xlfg/knowledge/_views/` is now a local generated read model and gitignored by default.
- git/worktree detection now handles unborn branches more gracefully so local branch-scoped views still prioritize the active branch before the first commit.
- `/xlfg:prepare` now records git/worktree context and rebuilds local views.
- `/xlfg:compound` now writes immutable cards/events and rebuilds views instead of asking branches to edit the same shared markdown files.
- Recall now reads generated views, tracked cards, tracked role cards, immutable events, and local runs.
- Docs, command prompts, skills, and tests were rewritten around the branch-safe knowledge model.

### Why
- multiple branches and linked worktrees were causing avoidable PR conflicts because they edited the same shared knowledge files
- generated rollups are useful for reading but are the wrong write target under concurrent branch workflows
- xlfg needs durable learning without turning compounding into a git tax

## 2.0.5 - 2026-03-09

### Added
- New planning agent `xlfg-why-analyst`.
- New planning agent `xlfg-harness-profiler`.
- New run artifacts: `why.md`, `harness-profile.md`, `workboard.md`, and `proof-map.md`.
- New role-memory scaffolds for `why-analyst` and `harness-profiler`.
- New bundle-level design note `docs/deer-flow-harness-review.md` that explains what xlfg borrowed from DeerFlow and what it intentionally rejected.

### Changed
- `/xlfg:plan` is now explicitly why-first and progressively loads optional planning agents only when the diagnosis justifies them.
- `/xlfg` now reads verification depth from `harness-profile.md` instead of assuming the same intensity for every run.
- `/xlfg:implement` now treats `workboard.md` as execution truth and `proof-map.md` as proof truth.
- `/xlfg:verify` now treats unresolved proof gaps as RED even when command results are green.
- `/xlfg:review` now uses the harness profile to determine the required review lenses.
- `/xlfg:compound` now compounds why / proof / harness-profile lessons in addition to shared knowledge and role memory.
- Docs, scaffold templates, and tests were updated to reflect the new harness model.

### Why
- Bigger prompt fan-out was not enough; xlfg needed explicit execution structure.
- The system needed a way to choose the minimum honest harness intensity instead of wasting time by default.
- Verification needed a stricter link between requirements and evidence so green commands could not hide missing proof.

## 2.0.4 - 2026-03-06

### Added
- New tracked `docs/xlfg/knowledge/_views/current-state.md` scaffolded in target repos as the single handoff document a next agent should read first.
- New role-memory scaffolds for `solution-architect`, `test-implementer`, `task-checker`, `architecture-reviewer`, `security-reviewer`, and `performance-reviewer`.
- New bundle-level `NEXT_AGENT_CONTEXT.md` so future agents can continue this repo without extra explanation.

### Changed
- `/xlfg` now runs deterministic recall before planning.
- `/xlfg:plan` now treats recall as mandatory and requires `memory-recall.md` to capture the query, strong matches, rejected near-matches, and explicit no-hit cases before broad repo fan-out.
- `/xlfg:compound` now refreshes `current-state.md` in addition to shared memory, role memory, and the ledger.
- Plugin docs now explicitly treat the CLI as optional support rather than the product.
- More specialist prompts now read `current-state.md` and their own role memory when relevant.

### Why
- A recall system is only valuable if `/xlfg` actually uses it.
- A target repo needs one tracked handoff document so the next agent can start fast.
- Role memory should exist for specialists that repeatedly benefit from compact tactical memory.

## 2.0.3 - 2026-03-06

### Added
- Deterministic `xlfg recall` CLI command over shared knowledge, role memory, the append-only ledger, migrations, and local runs.
- New `/xlfg:recall` plugin command and `xlfg-recall` skill.
- New scaffolded durable memory files: `docs/xlfg/knowledge/_views/ledger.jsonl`, `docs/xlfg/knowledge/ledger.md`, and `docs/xlfg/knowledge/queries.md`.
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
