# xlfg

An autonomous proof-first SDLC guide for Claude Code, designed for Opus-class models.

## Status

**v6.1.0** keeps the v6 philosophy cut — two slash commands whose bodies carry the whole SDLC discipline inline, no sub-agents, no hidden phase skills, no per-phase coordination files — and restores the minimal durable archive under `docs/xlfg/` that v6.0.0 dropped too eagerly. A fresh session needs something to recall; every run now ends by writing a compact summary or diagnosis to `docs/xlfg/runs/<RUN_ID>/`.

See `plugins/xlfg-engineering/CHANGELOG.md` for the migration notes from v5.1.0 and the v6.1.0 restore.

## What you get

- `/xlfg "<request>"` — walks recall → intent → context → plan → implement → verify → review → compound inline. The main model holds the whole run in its own context and plays PM, architect, security reviewer, performance reviewer, UX reviewer, test strategist, runner, reducer, and reviewer as separate mental passes. Ends by writing `docs/xlfg/runs/<RUN_ID>/run-summary.md` (Ask / What changed / Proof / Residual risk / Durable lesson) and optionally updating `docs/xlfg/current-state.md`.
- `/xlfg-debug "<request>"` — diagnosis-only. Walks recall → intent → context → debug. `allowed-tools` includes `Write` (for the diagnosis file) but excludes `Edit` and `MultiEdit` (product source stays untouched). Ends by writing `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.

Both bodies load the whole philosophy at invocation time. The tracked `docs/xlfg/` archive is how cross-session memory survives — there is no hidden tree to chase and no `.xlfg/` coordination state.

## Install

```text
/plugin marketplace add flrngel/xlfg
/plugin install xlfg-engineering@flrngel
```

Then:

```
/xlfg add a retry policy to the webhook consumer with exponential backoff
/xlfg-debug the auth middleware drops the session cookie on subdomain crossover
```

Update with `/plugin marketplace update xlfg`.

Cursor users: the plugin ships a `.cursor-plugin/plugin.json` manifest. Codex support was removed in v6.

## What's in this repo

1. `plugins/xlfg-engineering/` — the plugin itself (commands, hooks, audit script, manifests, CHANGELOG)
2. `tests/` — a lean test suite (`test_xlfg_v6.py`) that guards the plugin shape, the command frontmatter, and the load-bearing philosophy
3. `scripts/lint_plugin.py` — a frontmatter linter run in CI
4. `docs/` — historical research notes from the v3–v5 era (architecture, hooks, subagent hardening, planning autonomy). Kept as archival reading, not active guidance
5. `NEXT_AGENT_CONTEXT.md` — required handoff document for the next agent who touches this repo
6. `AGENTS.md` — short repo-level orientation

## Running the audit locally

```bash
python3 plugins/xlfg-engineering/scripts/audit_harness.py
```

Four checks: version sync, command surface, command frontmatter, forbidden-token sweep. Exit 0 on clean, 1 on any failure. `--json` for machine output.

## Running the test suite

```bash
python3 -m unittest discover -v
```

## License

MIT
