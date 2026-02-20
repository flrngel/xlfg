# xlfg-engineering-plugin

`/xlfg` is an **agent-first software development workflow** designed to reliably ship **production-ready** changes.

This repository includes:

1. A **Claude Code plugin** (in `plugins/xlfg-engineering`) that implements `/xlfg`, `/lfg`, and `/slfg`.
2. A small, dependency-free **Python CLI** (`xlfg`) that creates the same file-based scaffolding and can run verification with logs.

## Quick start (Claude Code)

1. Install the plugin from the `plugins/xlfg-engineering` directory.
2. In your target repo, run:
   - `/xlfg:init` once per repo (creates `docs/xlfg/` and `.xlfg/` scaffolding)
   - `/xlfg "<what you want built>"`

Shortcuts:

- `/lfg` — “sequential” guidance (single lead agent + subagents)
- `/slfg` — “swarm” guidance (agent teams if enabled, otherwise subagents)

## Quick start (CLI)

From any repo you’re working on:

```bash
# from this repo (one-time):
python -m pip install -e .

# sanity-check install
xlfg --version

# initialize scaffolding in the target repo
xlfg init

# start a run
xlfg start "implement feature X"

# run verification and write evidence
xlfg verify --mode full
```

## What gets created in your repo

Durable knowledge (intended to be committed):

- `docs/xlfg/index.md` — map of the knowledge base
- `docs/xlfg/knowledge/` — principles, decisions, and lessons learned
- `docs/xlfg/runs/<run-id>/` — specs, plans, risk analysis, review notes, final run summary

Ephemeral execution logs (intended to be gitignored):

- `.xlfg/runs/<run-id>/` — command outputs, test logs, screenshots, traces

## Commands included (plugin)

- `/xlfg` — end-to-end SDLC workflow (adaptive; includes planning, implementation, verification, review, ship)
- `/lfg` — macro for running `/xlfg` in a single-lead style
- `/slfg` — macro for running `/xlfg` in swarm style
- `/xlfg:init` — add repo scaffolding for xlfg runs (safe, idempotent)
- `/xlfg:verify` — run the verification loop (tests/lint/build) and write evidence files
- `/xlfg:review` — parallel multi-lens review into files; blocks on critical issues
- `/xlfg:compound` — turn a run into durable knowledge (patterns, decisions, checklists)

## Design principles (what makes it “xlfg”)

- **Map, not manual:** a small entrypoint file links to deeper sources of truth.
- **File-based context:** agents share state through files, not chat history.
- **Evidence-first:** no “done” without passing verification + captured evidence.
- **Parallel where safe:** research/review/testing can run concurrently; merges happen deterministically.
- **Quality gates:** risky changes require explicit approval + rollback planning.

## License

MIT
