# xlfg-engineering (Claude Code plugin)

`/xlfg` is a **diagnosis-first SDLC macro** for Claude Code.

It is designed for:

- long-horizon tasks
- multi-file changes
- user-flow-sensitive product work
- evidence-backed verification and review
- compounding from real failures instead of vague summaries

## Commands

| Command | Purpose |
|---|---|
| `/xlfg` | Macro that runs init → plan → implement → verify → review → compound |
| `/xlfg:init` | Create `docs/xlfg/` + `.xlfg/` scaffolding in the target repo |
| `/xlfg:plan` | Diagnose the problem and write the root-solution contracts before coding |
| `/xlfg:implement` | Execute bounded task loops with explicit implementation agents |
| `/xlfg:verify` | Run layered verification + write evidence |
| `/xlfg:review` | Parallel multi-lens review into files |
| `/xlfg:compound` | Convert a run into durable knowledge for future work |

`/xlfg` intentionally mirrors Compound’s macro style: it is a set of other commands, not one giant hidden workflow prompt.

## Key artifact model

Before coding, every serious run should produce:

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `scorecard.md`

These are the shared contracts for implementation, verification, and review.

## Agents

Planning:
- `xlfg-repo-mapper`
- `xlfg-root-cause-analyst`
- `xlfg-spec-author`
- `xlfg-test-strategist`
- `xlfg-env-doctor`
- `xlfg-solution-architect`
- `xlfg-risk-assessor`
- `xlfg-brainstorm`
- context investigators / researcher when needed

Implementation:
- `xlfg-test-implementer`
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

Follow semver. Update all of these together:

- `xlfg/__init__.py`
- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`
- `plugins/xlfg-engineering/CHANGELOG.md`
- `plugins/xlfg-engineering/README.md`
