# xlfg repo guide

Read `NEXT_AGENT_CONTEXT.md` first. It is the bundle-level handoff document and the fastest way for a new agent to understand what this repo is trying to become.

## Core principles

- `/xlfg` is a macro that chains explicit subcommands.
- `/xlfg` must always use deterministic recall before broad repo fan-out.
- Planning is diagnosis-first.
- Implementation must use explicit agents and targeted proof.
- Review confirms quality; it does not create quality.
- The repo is the system of record for long-running agent work.
- The Python CLI is optional implementation support; the plugin workflow is the product.

## Important paths

- `NEXT_AGENT_CONTEXT.md` — bundle-level handoff and rationale
- `plugins/xlfg-engineering/commands/` — Claude Code commands
- `plugins/xlfg-engineering/agents/` — subagent prompts
- `plugins/xlfg-engineering/skills/` — shared plugin skills
- `xlfg/` — optional dependency-free helper CLI / scaffold backend
- `tests/` — regression tests for scaffold, recall, verification, and repo contracts
