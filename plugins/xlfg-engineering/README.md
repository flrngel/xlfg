# xlfg-engineering (v6)

An autonomous proof-first SDLC guide for Claude Code, designed for Opus-class models.

## What you get

Two slash commands, plus a tiny tracked archive under `docs/xlfg/`.

- `/xlfg "<request>"` — walks recall → intent → context → plan → implement → verify → review → compound inline. The main model holds the whole run in its own context and plays PM, architect, security reviewer, performance reviewer, UX reviewer, test strategist, runner, reducer, and reviewer as separate mental passes — no sub-agents, no dispatch headers, no per-phase coordination files. Ends by writing `docs/xlfg/runs/<RUN_ID>/run-summary.md` (Ask / What changed / Proof / Residual risk / Durable lesson) and optionally updating the project's `docs/xlfg/current-state.md` if the run earned a promotion.
- `/xlfg-debug "<request>"` — diagnosis-only. Walks recall → intent → context → debug. `allowed-tools` includes `Write` but excludes `Edit` and `MultiEdit` — the command cannot ship a patch. Ends by writing `docs/xlfg/runs/<RUN_ID>/diagnosis.md` (Mechanism / Strongest evidence / Likely repair surface / Fake fixes rejected / No-code-change guarantee / Residual unknowns / Next safest proof step).

Both commands carry the full philosophy in their own bodies — the whole guide loads at invocation time. There is no hidden skill tree to chase.

## The durable archive under `docs/xlfg/`

Opus-class models hold one run in context, but the model's context does not span sessions. The `docs/xlfg/` tree is how a future session recalls what past runs did:

- `docs/xlfg/current-state.md` — optional, one-page, tracked. The "read this first" handoff for anyone entering the repo. ~300 words max.
- `docs/xlfg/runs/<RUN_ID>/run-summary.md` — one file per `/xlfg` run, ~200 words, fixed template.
- `docs/xlfg/runs/<RUN_ID>/diagnosis.md` — one file per `/xlfg-debug` run, fixed template.

`RUN_ID = <YYYYMMDD>-<HHMMSS>-<kebab-slug>`. Commit this directory to version control.

There is no `.xlfg/` directory in v6. All durable state is under `docs/xlfg/` and tracked.

## What's not in v6

If you're migrating from v5 (or earlier), these are gone on purpose:

- **Sub-agents** — the 27 specialists (`xlfg-task-divider`, `xlfg-verify-runner`, `xlfg-ux-reviewer`, …) don't exist anymore. Their expertise is embedded in the `/xlfg` body as lenses the main model adopts in-line.
- **Phase skills** — the 9 hidden phase skills (`xlfg-recall-phase`, `xlfg-intent-phase`, …) are gone. A phase is a discipline, not a Skill file.
- **The sub-agent coordination layer** — no `spec.md`, no `workboard.md`, no `phase-state.json`, no `verification.md`, no ledger schema. The run lives in context, not in a cross-phase file protocol. (v6.1.0 note: the tracked `docs/xlfg/runs/<RUN_ID>/run-summary.md` and `docs/xlfg/current-state.md` are **not** this layer — they're cross-session memory, written once at the end of a run.)
- **Stop and SubagentStop hooks** — with no sub-agents and no phase-state file, the hooks were vestigial. Only `PermissionRequest` `ExitPlanMode` auto-allow remains.
- **Codex surface** — `.codex-plugin/`, `codex/`, and the Codex marketplace wiring are removed. v6 ships on Claude Code (and, via `.cursor-plugin/`, Cursor).
- **`/xlfg-audit`, `/xlfg-status`, `/xlfg-init`** — all were tied to the v5 file-state surface.
- **`.xlfg/`** — v5 used it for the Stop hook's phase-state file. v6 has no phase-state, so no `.xlfg/`.

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
