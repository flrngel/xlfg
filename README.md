# xlfg-engineering

`xlfg` is an autonomous, proof-first SDLC harness for Claude Code.

Version 2.4.1 adds `/xlfg` as an alias for `/xlfg-engineering:xlfg` and restores the architecture the workflow actually needed:

- `/xlfg` is still the **single public entrypoint**, but it now **batches hidden phase skills** instead of flattening the whole workflow into one giant prompt
- the plugin form keeps one public namespaced command: `/xlfg-engineering:xlfg`
- the standalone pack keeps the short `/xlfg` path and now ships the matching hidden phase skills too
- `spec.md` remains the single source of truth, with only six always-on run files
- hidden phase skills load **just in time**, which matches Claude Code’s current skills model and keeps context smaller than an always-inlined monolith
- the entrypoints now use current Claude Code tool names such as `Skill`, `WebSearch`, and `WebFetch` instead of the stale `Task` naming

## What is in this repo

1. A Claude Code plugin in `plugins/xlfg-engineering/`
2. A standalone `.claude/skills/` pack in `standalone/`
3. A dependency-free Python helper CLI (`xlfg`) that can scaffold, recall, doctor, verify, and audit the same file model locally
4. Benchmarking guidance in `docs/benchmarking.md`
5. A repo handoff file in `NEXT_AGENT_CONTEXT.md`

## Quick start

### Plugin / team install

Run the plugin command:

- `/xlfg-engineering:xlfg "what you want built"`

### Standalone / short-command install

Copy the full `standalone/.claude/skills/` directory into your target repo’s `.claude/skills/`, then run:

- `/xlfg "what you want built"`

## Entry model

- `/xlfg` owns the whole SDLC run.
- It should not ask the user to run phase subcommands or internal skills.
- It loads hidden phase skills just in time: recall, context, plan, implement, verify, review, compound.
- `spec.md` is the run card and single source of truth.
- Optional docs exist only when they change a decision or proof.
- The helper CLI is optional, but when installed it makes scaffold, recall, and verification more deterministic.

## Local helper CLI

```bash
python -m pip install -e .
xlfg init
xlfg start "fix login flow"
xlfg audit
xlfg verify --mode full
```

## License

MIT
