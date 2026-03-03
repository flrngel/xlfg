# xlfg-engineering-plugin

`/xlfg` is a **diagnosis-first, contract-shared** software development workflow for agents.

The core change in this revision is simple:

> **Do not code until the problem, the user flow, the test contract, and the environment contract all agree.**

And do not force slow bootstrap when a repo is already prepared:

> **Prepare fast, migrate only on version drift, and keep noisy runs local by default.**

This repository includes:

1. A **Claude Code plugin** (in `plugins/xlfg-engineering`) with `/xlfg`, `/xlfg:prepare`, `/xlfg:init`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, and `/xlfg:compound`.
2. A dependency-free **Python CLI** (`xlfg`) that creates the same file structure and writes verification evidence.

## Quick start (Claude Code)

1. Install the plugin from `plugins/xlfg-engineering`.
2. In your target repo, run:
   - `/xlfg "what you want built"`

`/xlfg` is a **macro command** that orchestrates the subcommands in order:

1. `/xlfg:prepare`
2. `/xlfg:plan`
3. `/xlfg:implement`
4. `/xlfg:verify`
5. `/xlfg:review`
6. `/xlfg:compound`

Use `/xlfg:init` manually only when you want to bootstrap or repair the scaffold yourself.

## Quick start (CLI)

From any repo you’re working on:

```bash
# one-time from this repo
python -m pip install -e .

# optional fast prepare / migrate check
xlfg prepare

# start a run (auto-prepares if needed)
xlfg start "implement feature X"

# inspect detected commands / dev server contract
xlfg status
xlfg detect
xlfg doctor

# run verification and write evidence
xlfg verify --mode full
```

## What gets created in your repo

Tracked durable knowledge:

- `docs/xlfg/index.md` — map of the knowledge base
- `docs/xlfg/meta.json` — scaffold version and migration state
- `docs/xlfg/knowledge/` — decisions, patterns, test learnings, UX flows, failure memory, harness rules
- `docs/xlfg/knowledge/agent-memory/` — small role-specific memory files
- `docs/xlfg/migrations/` — notes written when xlfg versions drift

Local run evidence (gitignored by default):

- `docs/xlfg/runs/<run-id>/` — diagnosis, solution decisions, contracts, plans, scorecards, reviews, summaries
- `.xlfg/runs/<run-id>/verify/` — verification logs + exit codes
- `.xlfg/runs/<run-id>/doctor/` — dev-server and readiness reports

## Commands included (plugin)

- `/xlfg` — macro that runs the full SDLC command chain
- `/xlfg:prepare` — fast scaffold/version check with migration on drift
- `/xlfg:init` — manual bootstrap/repair for xlfg files
- `/xlfg:plan` — diagnosis-first planning and contract creation
- `/xlfg:implement` — bounded implementation loops with explicit agents and targeted checks
- `/xlfg:verify` — run layered verification and write evidence
- `/xlfg:review` — parallel multi-lens review into files
- `/xlfg:compound` — turn a run into durable knowledge

## Why this version is different

### Old failure mode
- vague request handling
- coding starts before the problem is understood
- tests are decided late
- review agents clean up bad implementation choices
- shortcut patches sneak through
- the same environment mistakes repeat
- run artifacts create commit noise

### New discipline
- prepare fast, migrate only on version drift
- diagnose first
- reject shortcut patches during planning
- make implementation and verification share the same contracts
- require specified agents for planning and implementation
- keep runs local, promote only durable lessons
- give certain agents their own compact memory
- treat review as confirmation, not cleanup
- compound real failures into reusable harness and testing memory

## Design principles

- **Diagnosis first:** identify the real change surface before writing code.
- **Root-cause over symptom patches:** every run must record tempting shortcuts and why they were rejected.
- **Contract-shared execution:** planning, implementation, verification, and review use the same flow/test/env contracts.
- **File-based context:** agents share state through files, not chat history.
- **Evidence-first:** no “done” without passing verification + captured evidence.
- **Verified compounding:** only durable, provenance-backed lessons enter the knowledge base.
- **Role memory, not prompt bloat:** small agent-specific memories for roles that repeatedly fail the same way.
- **Environment discipline:** reuse healthy dev servers; do not spawn duplicates blindly.

## License

MIT
