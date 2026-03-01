# Agent Instructions

This repo is a **Claude Code plugin** implementing `/xlfg`: a behavior-contract-first SDLC workflow that coordinates independent subagents via file-based context.

## Start here

- Plugin root: `plugins/xlfg-engineering`
- Commands: `plugins/xlfg-engineering/commands/`
- Agents: `plugins/xlfg-engineering/agents/`
- Skills: `plugins/xlfg-engineering/skills/`
- CLI: `xlfg/`

## Working agreement

- Keep all `description:` fields short to avoid context-budget waste.
- Prefer **file-based context** over long prompts.
- The pre-implementation contracts are the core of the system:
  - `flow-spec.md`
  - `test-contract.md`
  - `env-plan.md`
- Update all three when changing plugin behavior:
  - `plugins/xlfg-engineering/.claude-plugin/plugin.json`
  - `plugins/xlfg-engineering/CHANGELOG.md`
  - `plugins/xlfg-engineering/README.md`

## Quality bar

- `/xlfg:init` must stay idempotent.
- `/xlfg` must never claim success unless verification evidence exists.
- Compounding should only admit concrete, verified lessons.
- Favor "map not manual": put durable guidance in docs and owned run files, not in monolithic chat history.
