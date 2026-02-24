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
| `/xlfg` | End-to-end SDLC workflow (context expansion → spec/plan → mandatory pair implementation → verify → review → ship → compound) |
| `/lfg` | Sequential wrapper for `/xlfg` |
| `/slfg` | Swarm wrapper for `/xlfg` |
| `/xlfg:init` | Create `docs/xlfg/` + `.xlfg/` scaffolding in the target repo |
| `/xlfg:verify` | Run verification pipeline + write evidence logs |
| `/xlfg:review` | Parallel multi-lens review into files |
| `/xlfg:compound` | Convert a run into durable knowledge for future work |

`/xlfg` auto-continues from planning into implementation. It only pauses for true blockers or safety-gated confirmations.
`/xlfg:review` is verification-aware and prioritizes net-new findings over verification overlap.

## Agents

Context expansion:
- `xlfg-context-adjacent-investigator`
- `xlfg-context-constraints-investigator`
- `xlfg-context-unknowns-investigator`

Planning:
- `xlfg-repo-mapper`
- `xlfg-spec-author`
- `xlfg-test-strategist`
- `xlfg-risk-assessor`

Implementation:
- `xlfg-task-implementer`
- `xlfg-task-checker`

Verify:
- `xlfg-verify-runner`
- `xlfg-verify-reducer`

Review:
- `xlfg-security-reviewer`
- `xlfg-performance-reviewer`
- `xlfg-ux-reviewer`
- `xlfg-architecture-reviewer`

Subagent model:
- `/xlfg` subagents use `sonnet`.

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
