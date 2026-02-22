# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
