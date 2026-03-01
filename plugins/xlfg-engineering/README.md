# xlfg-engineering (Claude Code plugin)

`/xlfg` is a **behavior-contract-first SDLC workflow** for Claude Code.

It is designed for:

- long-horizon tasks
- multi-file changes
- user-flow-sensitive product work
- evidence-backed verification and review
- compounding from real failures instead of vague summaries

## Commands

| Command | Purpose |
|---|---|
| `/xlfg` | End-to-end workflow (contract → plan → implement → targeted verify → gate verify → review → compound) |
| `/lfg` | Sequential wrapper for `/xlfg` |
| `/slfg` | Swarm wrapper for `/xlfg` |
| `/xlfg:init` | Create `docs/xlfg/` + `.xlfg/` scaffolding in the target repo |
| `/xlfg:verify` | Run layered verification + write evidence |
| `/xlfg:review` | Parallel multi-lens review into files |
| `/xlfg:compound` | Convert a run into durable knowledge for future work |

`/xlfg` is intentionally **self-contained**: it performs init / verify / review / compound steps inline so the workflow does not get stuck on subcommand chaining.

## Key artifact model

Before coding, every serious run should produce:

- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `scorecard.md`

These are the shared contracts for implementation, verification, and review.

## Agents

Planning / contracts:
- `xlfg-spec-author`
- `xlfg-test-strategist`
- `xlfg-env-doctor`
- `xlfg-risk-assessor`
- `xlfg-brainstorm`
- context investigators / repo mapper / researcher (when needed)

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
