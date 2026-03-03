# xlfg-engineering-plugin

`/xlfg` is a **diagnosis-first, contract-shared** software development workflow for agents.

The core change in this revision is simple:

> **Do not code until the problem, the user flow, the test contract, and the environment contract all agree.**

Instead of treating verification as a late question — “does this work?” — xlfg now treats planning and implementation as the first line of quality:

1. **Diagnose the real problem** — `diagnosis.md`
2. **Choose the root solution, not the tempting patch** — `solution-decision.md`
3. **Define the shared user-flow contract** — `flow-spec.md`
4. **Define the shared test contract** — `test-contract.md`
5. **Define the environment / harness contract** — `env-plan.md`
6. **Execute bounded task loops with targeted proof** — `tasks/<task-id>/...`

This repository includes:

1. A **Claude Code plugin** (in `plugins/xlfg-engineering`) with `/xlfg`, `/xlfg:init`, `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, `/xlfg:review`, and `/xlfg:compound`.
2. A dependency-free **Python CLI** (`xlfg`) that creates the same file structure and writes verification evidence.

## Quick start (Claude Code)

1. Install the plugin from `plugins/xlfg-engineering`.
2. In your target repo, run:
   - `/xlfg:init` once per repo
   - `/xlfg "what you want built"`

`/xlfg` is now a **macro command** that orchestrates the subcommands in order:

1. `/xlfg:init`
2. `/xlfg:plan`
3. `/xlfg:implement`
4. `/xlfg:verify`
5. `/xlfg:review`
6. `/xlfg:compound`

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
- `docs/xlfg/runs/<run-id>/` — diagnosis, solution decisions, contracts, plans, scorecards, reviews, summaries

Ephemeral execution logs (intended to be gitignored):

- `.xlfg/runs/<run-id>/verify/` — verification logs + exit codes
- `.xlfg/runs/<run-id>/doctor/` — dev-server and readiness reports

## Commands included (plugin)

- `/xlfg` — macro that runs the full SDLC command chain
- `/xlfg:init` — add repo scaffolding for xlfg runs
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

### New discipline
- diagnose first
- reject shortcut patches during planning
- make implementation and verification share the same contracts
- require specified agents for planning and implementation
- run the cheapest proof that matches the scenario after each task
- treat review as confirmation, not cleanup
- compound real failures into reusable harness and testing memory

## Design principles

- **Diagnosis first:** identify the real change surface before writing code.
- **Root-cause over symptom patches:** every run must record tempting shortcuts and why they were rejected.
- **Contract-shared execution:** planning, implementation, verification, and review use the same flow/test/env contracts.
- **File-based context:** agents share state through files, not chat history.
- **Evidence-first:** no “done” without passing verification + captured evidence.
- **Verified compounding:** only durable, provenance-backed lessons enter the knowledge base.
- **Environment discipline:** reuse healthy dev servers; do not spawn duplicates blindly.

## License

MIT
