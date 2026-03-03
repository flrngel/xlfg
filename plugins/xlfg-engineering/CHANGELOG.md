# Changelog

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
