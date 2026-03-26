# xlfg-engineering

`xlfg` is an autonomous, proof-first SDLC harness for Claude Code.

Version 2.5.0 strengthens the weakest part of the workflow: **understanding messy user intent before the repo fan-out starts**.

- `/xlfg` is still the **single public entrypoint**, and it still **batches hidden phase skills**
- the batch now includes a mandatory **intent phase** before context gathering and planning
- `spec.md` is now the only active home for the **intent contract** and objective groups
- bundled / messy requests are split into stable objective groups (`O1`, `O2`, ...)
- the workflow ships an artifact-graded **`xlfg eval-intent`** harness for scoring ask recall, objective splitting, blocker handling, and false assumptions
- hidden phase skills still load **just in time**, matching Claude Code’s skills model while keeping context small

## What is in this repo

1. A Claude Code plugin in `plugins/xlfg-engineering/`
2. A standalone `.claude/skills/` pack in `standalone/`
3. A dependency-free Python helper CLI (`xlfg`) that can scaffold, recall, verify, audit, and grade intent artifacts locally
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
- It loads hidden phase skills just in time: recall, intent, context, plan, implement, verify, review, compound.
- `spec.md` is the run card and single source of truth.
- Optional docs exist only when they change a decision or proof.
- The helper CLI is optional, but when installed it makes scaffold, recall, verification, audit, and intent grading more deterministic.

## Local helper CLI

```bash
python -m pip install -e .
xlfg init
xlfg start "fix login flow"
xlfg audit
xlfg eval-intent --fixture evals/intent/messy-bugfix-bundle.json --run <RUN_ID>
xlfg eval-intent --suite-dir evals/intent
xlfg verify --mode full
```

## License

MIT
