# xlfg-engineering (v6)

An autonomous proof-first SDLC guide for Claude Code, designed for Opus-class models.

## What you get

Two slash commands. That's it.

- `/xlfg "<request>"` — walks recall → intent → context → plan → implement → verify → review → compound inline. The main model holds the whole run in its own context and plays PM, architect, security reviewer, performance reviewer, UX reviewer, test strategist, runner, reducer, and reviewer as separate mental passes — no sub-agents, no dispatch headers, no per-phase artifacts. Finishes with a concise status summary (files changed, proof run, residual risk, the durable lesson).
- `/xlfg-debug "<request>"` — diagnosis-only. Walks recall → intent → context → debug. `allowed-tools` intentionally excludes `Edit`, `MultiEdit`, and `Write`, so the command cannot ship a patch — it produces a mechanism, evidence, likely repair surface, rejected fake fixes, and residual unknowns.

Both commands carry the full philosophy in their own bodies — the whole guide loads at invocation time. There is no hidden skill tree to chase.

## What's not in v6

If you're migrating from v5 (or earlier), these are gone on purpose:

- **Sub-agents** — the 27 specialists (`xlfg-task-divider`, `xlfg-verify-runner`, `xlfg-ux-reviewer`, …) don't exist anymore. Their expertise is embedded in the `/xlfg` body as lenses the main model adopts in-line.
- **Phase skills** — the 9 hidden phase skills (`xlfg-recall-phase`, `xlfg-intent-phase`, …) are gone. A phase is a discipline, not a Skill file.
- **File-based run state** — no `docs/xlfg/runs/<RUN_ID>/`, no `spec.md`, no `workboard.md`, no `phase-state.json`, no ledger. The run lives in context and in the real repo.
- **Stop and SubagentStop hooks** — with no sub-agents and no phase-state file, the hooks were vestigial. Only `PermissionRequest` `ExitPlanMode` auto-allow remains.
- **Codex surface** — `.codex-plugin/`, `codex/`, and the Codex marketplace wiring are removed. v6 ships on Claude Code (and, via `.cursor-plugin/`, Cursor).
- **`/xlfg-audit`, `/xlfg-status`, `/xlfg-init`** — all were file-state-dependent. They don't make sense without the file-state surface.

## Installation

```bash
/plugin marketplace add flrngel/xlfg
/plugin install xlfg-engineering@flrngel
```

Then in any Claude Code session:

```
/xlfg add a retry policy to the webhook consumer with exponential backoff
/xlfg-debug the auth middleware drops the session cookie on subdomain crossover
```

## Running the audit locally

The plugin self-audits via `scripts/audit_harness.py` — four deterministic checks (version sync, command surface, command frontmatter, forbidden-token sweep). Runs in CI on every PR.

```bash
python3 plugins/xlfg-engineering/scripts/audit_harness.py
```

`--json` for machine output.

## Why the v6 cut

The v5 line carried 44 files of delegation scaffolding: specialist agents, phase skills, shared preambles, dispatch rules, file-protocol guards, and cross-runtime hooks. That made sense when weaker models needed externalized state to stay coherent across a long run.

Opus 4.7 has a 1M-token context and strong self-monitoring. The file protocol was paying serialization cost for a feature the model no longer needs. The discipline survives — 8 phases, proof before claim, scope discipline, completion barrier, no broken-window fixes, human-only blockers — but it survives as prose the model reads once at the start of the run, not as a graph of sub-agent dispatches.

See `CHANGELOG.md` for the complete 6.0.0 migration notes.

## License

MIT. See `LICENSE` at repo root.
