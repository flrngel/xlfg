# xlfg-engineering-plugin

`/xlfg` is an **adaptive research-to-release SDLC harness** for Claude Code.

The core rule in this revision is simple:

> **Let Claude Code stay the orchestrator. Add only the smallest amount of SDLC structure that increases trust: recall what matters, research only when external truth matters, plan the delivery, prove the changed behavior, and keep PM / Engineering / QA aligned in one run card.**

This repository includes:

1. A **Claude Code plugin** (in `plugins/xlfg-engineering`) with `/xlfg`, `/xlfg:prepare`, `/xlfg:recall`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, `/xlfg:compound`, and `/xlfg:audit`.
2. An optional dependency-free **Python helper CLI** (`xlfg`) that can scaffold, recall, doctor, verify, and audit the same file model locally.
3. A required bundle-level handoff doc: `NEXT_AGENT_CONTEXT.md`.
4. Benchmarking guidance in `docs/benchmarking.md`.

## Read this repo in this order

1. `NEXT_AGENT_CONTEXT.md`
2. `docs/benchmarking.md`
3. `plugins/xlfg-engineering/README.md`
4. `plugins/xlfg-engineering/commands/xlfg.md`
5. `plugins/xlfg-engineering/commands/xlfg-plan.md`
6. `xlfg/audit.py`
7. `xlfg/runs.py`
8. `tests/test_xlfg.py`

## Quick start (Claude Code)

1. Install the plugin from `plugins/xlfg-engineering`.
2. In your target repo, run:
   - `/xlfg "what you want built"`

Macro flow:

1. `/xlfg:recall`
2. `/xlfg:plan`
3. confirm `test-readiness.md` is `READY`
4. `/xlfg:implement`
5. `/xlfg:verify`
6. `/xlfg:review`
7. `/xlfg:compound`

Use `/xlfg:audit` when you want to measure the harness itself.

## Why 2.1.0 exists

The prior revision already removed the fake `prepare` ritual, but it was still too easy for xlfg to become **heavier than strong vanilla Claude Code**.

This revision tightens three ideas:

- `spec.md` is now the **run card** that PM / Engineering / QA all read first
- research is explicitly part of the SDLC, but **only when needed**
- subagent use is now **adaptive**, not routine

## Local helper CLI

```bash
python -m pip install -e .
xlfg start "fix login flow"
xlfg audit
xlfg verify --mode full
```

## License

MIT
