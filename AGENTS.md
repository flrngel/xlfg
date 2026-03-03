# xlfg repo guide

This repository builds the `xlfg` workflow.

## Core principles

- `/xlfg` is a macro that chains explicit subcommands.
- Planning is diagnosis-first.
- Implementation must use explicit agents and targeted proof.
- Review confirms quality; it does not create quality.
- The repo is the system of record for long-running agent work.

## Important paths

- `plugins/xlfg-engineering/commands/` — Claude Code commands
- `plugins/xlfg-engineering/agents/` — subagent prompts
- `plugins/xlfg-engineering/skills/` — shared plugin skills
- `xlfg/` — dependency-free CLI
- `tests/` — basic regression tests for the CLI scaffold / doctor / verify flow
