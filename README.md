# xlfg

An autonomous proof-first SDLC guide for Claude Code, designed for Opus-class models.

## Status

**v6.5.6** is a follow-up to v6.5.5 driven by a real-world `/xlfg` run whose summary still bloated even after v6.5.5's labeled-row template. The labels were tight; the *cell values* were narrative — multi-clause sentences, semicolons, parentheticals, dir-listing dumps in the `Files` row. v6.5.5 governed the row count but not the content density. v6.5.6 adds three changes that govern the latter. (1) The summary template switches from `**Label:** value` lines to an actual markdown table (`| Label | value |`) so terminal output renders in a tight grid. (2) Each cell carries a hard ≤80-char one-clause cap — no compound sentences, no semicolons, no em-dash splitting one cell into two ideas, no nested parentheticals. If detail does not fit, the cell says `see archive` and the user opens `run-summary.md`. (3) The `Files` row is dropped entirely from `/xlfg` — `git show <sha>` and `run-summary.md` already list files. The question template gets matching tightening: the lead drops from `Need <n> answers before proceeding:` to `Need <n> answers:`, the footer from `Blocking because:` to `Blocking:`, and the same ≤80-char cap applies per question. Five new tests pin the table format and the cell-length declaration; the four existing summary/question tests are updated to match the new strings. Test surface 58 → 61. Everything underneath v6.5.5 — the v6.5.4 handoff-cue reminders on all 9 phase bodies, the `/xlfg-debug` no-source-edits check, the sanctioned-write-path naming, the mixed skill/agent pipeline, the 27 specialist lens skills, `/xlfg-init`, and the `docs/xlfg/` durable archive — stays.

See `plugins/xlfg-engineering/CHANGELOG.md` for the full evolution from v5 to v6.5.

## What you get

- `/xlfg-init` — one-shot idempotent project scaffold. Patches the CWD's `.gitignore` with the canonical v6 runs block and creates `docs/xlfg/runs/.gitkeep` + `README.md`. Not a conductor. Run once after installing the plugin in a new project; safe to re-run.
- `/xlfg "<request>"` — dispatches 8 phase skills in order: recall → intent → context → plan → implement → verify → review → compound. Each skill loads when invoked, runs in the main model's context, and returns. Ends by writing `docs/xlfg/runs/<RUN_ID>/run-summary.md` (Ask / What changed / Proof / Residual risk / Durable lesson) and optionally updating `docs/xlfg/current-state.md`.
- `/xlfg-debug "<request>"` — dispatches 4 phase skills: recall → intent → context → debug. Diagnosis-only: `allowed-tools` includes `Write` (for the diagnosis file) but excludes `Edit` and `MultiEdit` (product source stays untouched). Ends by writing `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.

The conductors carry the pipeline order, loopback rules, and operating contract; the phase bodies live in `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md` (9 files total, three shared between the conductors). Alongside them, `plugins/xlfg-engineering/skills/xlfg-<name>/SKILL.md` (no `-phase` suffix) holds 27 hidden specialist lens skills that phase skills load on-demand. The tracked `docs/xlfg/` archive is how cross-session memory survives — there is no `.xlfg/` coordination state.

## Install

```text
/plugin marketplace add flrngel/xlfg
/plugin install xlfg-engineering@flrngel
```

Then, once per project, from the project root:

```
/xlfg-init
```

After that:

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
