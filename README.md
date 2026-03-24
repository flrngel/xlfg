# xlfg-engineering

`xlfg` is an autonomous, proof-first SDLC harness for Claude Code.

Version 2.3.0 fixes the broken entrypoint behavior from 2.2.0:

- the plugin now exposes **one primary `/xlfg` entrypoint per install mode** instead of a colliding command+skill pair
- the main entrypoint is **self-contained** and no longer points Claude at a repo-relative plugin path that may not exist
- the plugin form stays namespaced for team reuse, while the standalone `.claude/` pack remains the short `/xlfg` path
- `spec.md` remains the single source of truth, with only six always-on run files
- support skills are now background helpers instead of competing user-facing entrypoints

## What is in this repo

1. A Claude Code plugin in `plugins/xlfg-engineering/`
2. A standalone `.claude/skills/xlfg/` pack in `standalone/`
3. A dependency-free Python helper CLI (`xlfg`) that can scaffold, recall, doctor, verify, and audit the same file model locally
4. Benchmarking guidance in `docs/benchmarking.md`
5. A repo handoff file in `NEXT_AGENT_CONTEXT.md`

## Quick start

### Plugin / team install

Run the plugin command:

- `/xlfg-engineering:xlfg "what you want built"`

### Standalone / short-command install

Copy `standalone/.claude/skills/xlfg/` into your target repo’s `.claude/skills/xlfg/`, then run:

- `/xlfg "what you want built"`

## Entry model

- `/xlfg` owns the whole SDLC run.
- It should not ask the user to run phase subcommands.
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
