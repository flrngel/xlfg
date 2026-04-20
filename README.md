# xlfg

An autonomous proof-first SDLC guide for Claude Code, designed for Opus-class models.

## Status

**v6.5.2** splits the pipeline into **phase skills** (decision-driving, in-context) and **phase agents** (exploration-heavy, delegated). Both conductors now carry an explicit `## Between phases` section that forbids ending the turn on natural transition sentences ("Plan is READY. Proceeding to implement.") — the run is one continuous conductor turn end-to-end. `/xlfg` dispatches 4 skills (intent, plan, implement, compound) + 4 agents (recall, context, verify, review) in canonical order; `/xlfg-debug` dispatches 2 skills (intent, debug) + 2 agents (recall, context). Each agent returns a distilled synthesis via a mandatory `## Return format` section instead of accumulating its tool-call log in the conductor. 27 specialist lens skills load on-demand for focused expertise — specialists stay as skills, not agents, because they sit on shared context with their parent. `/xlfg-init` remains the per-project scaffold (patches `.gitignore`, seeds `docs/xlfg/runs/`). The durable archive under `docs/xlfg/` (current-state + per-run summaries/diagnoses) stays.

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
