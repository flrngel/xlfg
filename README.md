# xlfg-engineering-plugin

`/xlfg` is a **behavior-contract-first** software development workflow for agents.

The core change in this version is simple:

> **Define the user flow and the shared test contract before writing code.**

Instead of waiting until the end to ask "does this work?", xlfg now starts by creating a shared contract for:

1. **What to build** — `flow-spec.md`
2. **What to test** — `test-contract.md`
3. **How the environment must run** — `env-plan.md`
4. **How progress is scored** — `scorecard.md`

This repository includes:

1. A **Claude Code plugin** (in `plugins/xlfg-engineering`) that implements `/xlfg`, `/lfg`, and `/slfg`.
2. A dependency-free **Python CLI** (`xlfg`) that creates the same file structure, runs environment doctor checks, and writes verification evidence.

## Quick start (Claude Code)

1. Install the plugin from `plugins/xlfg-engineering`.
2. In your target repo, run:
   - `/xlfg:init` once per repo
   - `/xlfg "what you want built"`

Shortcuts:

- `/lfg` — single lead + focused subagents
- `/slfg` — broader swarm / team orchestration

## Quick start (CLI)

From any repo you’re working on:

```bash
# one-time from this repo
python -m pip install -e .

# initialize scaffolding
xlfg init

# start a run
xlfg start "implement feature X"

# inspect detected commands / dev server contract
xlfg detect
xlfg doctor

# run verification and write evidence
xlfg verify --mode full
```

## What gets created in your repo

Durable knowledge (intended to be committed):

- `docs/xlfg/index.md` — map of the knowledge base
- `docs/xlfg/knowledge/` — decisions, patterns, test learnings, UX flows, failure memory, harness rules
- `docs/xlfg/runs/<run-id>/` — contracts, plans, scorecards, reviews, summaries

Ephemeral execution logs (intended to be gitignored):

- `.xlfg/runs/<run-id>/verify/` — verification logs + exit codes
- `.xlfg/runs/<run-id>/doctor/` — dev-server and readiness reports

## Commands included (plugin)

- `/xlfg` — end-to-end SDLC workflow (contract → plan → implement → targeted verify → gate verify → review → compound)
- `/lfg` — sequential mode guidance
- `/slfg` — swarm mode guidance
- `/xlfg:init` — add repo scaffolding for xlfg runs
- `/xlfg:verify` — run layered verification and write evidence
- `/xlfg:review` — parallel multi-lens review into files
- `/xlfg:compound` — turn a run into durable knowledge

## Why this version is different

### Old pattern
- define acceptance loosely
- implement
- run big tests later
- get stuck on port conflicts / watch mode / stale servers
- repeat the same failed command

### New pattern
- define **user-flow contract** first
- define **test contract** first
- define **environment contract** first
- run the **fastest relevant check after each task**
- run **full gate verification only at the right time**
- compound real failures into **failure memory** and **harness rules**

## Design principles

- **Shift-left contracts:** behavior, testing, and environment are agreed before coding.
- **Dual-set verification:** prove new behavior (Fail → Pass) and preserve old behavior (Pass → Pass).
- **File-based context:** agents share state through files, not chat history.
- **Evidence-first:** no “done” without passing verification + captured evidence.
- **Verified compounding:** only durable, provenance-backed lessons enter the knowledge base.
- **Environment discipline:** reuse healthy dev servers; do not spawn duplicates blindly.

## License

MIT
