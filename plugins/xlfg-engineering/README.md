# xlfg-engineering (Claude Code plugin)

`/xlfg` is a **production-grade SDLC workflow** for Claude Code.

It is designed for:

- Long-horizon tasks
- Multi-file changes
- High correctness + UX standards
- Evidence-backed verification (tests/lint/build) and multi-lens review

## Commands

| Command | Purpose |
|---|---|
| `/xlfg` | End-to-end SDLC workflow (spec → plan → implement → verify → review → ship) |
| `/lfg` | Sequential wrapper for `/xlfg` |
| `/slfg` | Swarm wrapper for `/xlfg` |
| `/xlfg:init` | Create `docs/xlfg/` + `.xlfg/` scaffolding in the target repo |
| `/xlfg:verify` | Run verification + write evidence logs |
| `/xlfg:review` | Parallel multi-lens review into files |
| `/xlfg:compound` | Convert a run into durable knowledge for future work |

## Agents

Planning:
- `xlfg-repo-mapper`
- `xlfg-spec-author`
- `xlfg-test-strategist`
- `xlfg-risk-assessor`

Review:
- `xlfg-security-reviewer`
- `xlfg-performance-reviewer`
- `xlfg-ux-reviewer`
- `xlfg-architecture-reviewer`

Subagent model:
- Planning and review subagents use `sonnet`.

## Skills

- `xlfg-file-context`
- `xlfg-quality-gates`

## Installation

Point Claude Code at `plugins/xlfg-engineering` as a plugin directory.

## Versioning

Follow semver. Update all three files together:

- `.claude-plugin/plugin.json`
- `CHANGELOG.md`
- `README.md`
