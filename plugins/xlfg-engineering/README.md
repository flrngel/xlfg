# xlfg-engineering (v6.3)

An autonomous proof-first SDLC guide for Claude Code, designed for Opus-class models.

## What you get

Two slash commands that act as **conductors**, each dispatching a pipeline of hidden phase skills just-in-time.

- `/xlfg "<request>"` — dispatches 8 phase skills in order: recall → intent → context → plan → implement → verify → review → compound. Each skill loads when invoked, does its phase work in the main model's context, and returns. After compound, the conductor commits tracked product changes as one Conventional Commits-style commit (skipped cleanly on investigation-only runs; `docs/xlfg/runs/**` and `.xlfg/**` never staged). Ends by writing `docs/xlfg/runs/<RUN_ID>/run-summary.md` and optionally updating `docs/xlfg/current-state.md`.
- `/xlfg-debug "<request>"` — dispatches 4 phase skills: recall → intent → context → debug. Diagnosis-only: `allowed-tools` excludes `Edit` and `MultiEdit`, so product source cannot be modified. Ends by writing `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.

The phases are `plugins/xlfg-engineering/skills/xlfg-<name>-phase/SKILL.md` — 9 files total. Three of them (recall, intent, context) are shared by both conductors.

Alongside the phase skills, v6.3 ships **27 specialist lens skills** under `plugins/xlfg-engineering/skills/xlfg-<name>/SKILL.md` (no `-phase` suffix). These are hidden (`user-invocable: false`), carry the same 5-section template as phase skills, and exist so a phase skill can load a focused lens on-demand — `xlfg-security-reviewer` during review, `xlfg-root-cause-analyst` during debug, and so on. They are *skills*, not sub-agents: they run in the conductor's own context, not in a delegated sub-context. The 7 non-trivial phase skills (intent, context, plan, implement, verify, review, debug) each list the specialists loadable from them.

## Architecture

```
commands/
  xlfg.md          ← conductor (~600 words): frontmatter + pipeline + loopback rules
  xlfg-debug.md    ← conductor (~500 words): frontmatter + pipeline + no-source-edits contract
skills/
  xlfg-recall-phase/SKILL.md      ← shared (used by /xlfg and /xlfg-debug)
  xlfg-intent-phase/SKILL.md      ← shared
  xlfg-context-phase/SKILL.md     ← shared
  xlfg-plan-phase/SKILL.md        ← /xlfg only
  xlfg-implement-phase/SKILL.md   ← /xlfg only
  xlfg-verify-phase/SKILL.md      ← /xlfg only
  xlfg-review-phase/SKILL.md      ← /xlfg only
  xlfg-compound-phase/SKILL.md    ← /xlfg only
  xlfg-debug-phase/SKILL.md       ← /xlfg-debug only
scripts/
  audit_harness.py  ← CI self-audit (5 checks)
hooks/
  hooks.json        ← ExitPlanMode auto-allow only
```

Skills run in the conductor's own context — no sub-agents, no nested delegation. The test suite enforces this: no `Agent` or `SendMessage` in any command or skill's `allowed-tools`.

## The durable archive under `docs/xlfg/`

Opus-class models hold one run in context, but context doesn't span sessions. The `docs/xlfg/` tree is how a future session recalls what past runs did:

- `docs/xlfg/current-state.md` — optional, one-page, tracked. The "read this first" handoff. ~300 words max.
- `docs/xlfg/runs/<RUN_ID>/run-summary.md` — one file per `/xlfg` run, fixed template.
- `docs/xlfg/runs/<RUN_ID>/diagnosis.md` — one file per `/xlfg-debug` run, fixed template.

`RUN_ID = <YYYYMMDD>-<HHMMSS>-<kebab-slug>`. Commit this directory to version control.

There is no `.xlfg/` directory in v6.

## What's not in v6

If you're migrating from v5 or earlier:

- **Sub-agents** — there are no sub-agents. The 27 specialists (`xlfg-task-divider`, `xlfg-verify-runner`, `xlfg-ux-reviewer`, …) exist in v6.3 as **hidden skills**, not as dispatched sub-contexts. Phase skills load them on-demand via the `Skill` tool.
- **v5 coordination layer** — no `spec.md`, no `workboard.md`, no `phase-state.json`, no `verification.md`, no `test-contract.md`, no ledger schema. The run lives in context; durable memory is the tracked `docs/xlfg/` archive.
- **Stop and SubagentStop hooks** — gone. Only `PermissionRequest` `ExitPlanMode` auto-allow remains.
- **Codex surface** — `.codex-plugin/`, `codex/`, and Codex marketplace wiring are removed. v6 ships on Claude Code (and, via `.cursor-plugin/`, Cursor).
- **`/xlfg-audit`, `/xlfg-status`, `/xlfg-init`** — all were tied to the v5 file-state surface.
- **`.xlfg/`** — v5 used it for the Stop hook's phase-state file. v6 has no phase-state.

## Installation

```text
/plugin marketplace add flrngel/xlfg
/plugin install xlfg-engineering@flrngel
```

Then:

```
/xlfg add a retry policy to the webhook consumer with exponential backoff
/xlfg-debug the auth middleware drops the session cookie on subdomain crossover
```

## Running the audit locally

```bash
python3 plugins/xlfg-engineering/scripts/audit_harness.py
```

Five checks: version sync, command surface, command frontmatter, forbidden-token sweep (covers commands AND skill bodies), skill surface (9 phase skills + 27 specialist skills with correct frontmatter). `--json` for machine output.

## Why this shape

v5 had specialists + skills + dispatch packets + coordination files + hooks — 44 scaffolding files that were serialization overhead for weaker models. v6.0 nuked all of it. v6.1 restored the cross-session durable archive. v6.2 restored the skill split for context-budget discipline (phase bodies load just-in-time). v6.3 restores the specialist expertise as **on-demand hidden skills** — a phase skill can reach for a focused lens (security, root-cause, test-strategist, …) when the work calls for it, without paying the token cost of every lens in every run.

Net: strong reasoners get the phase guidance *and* the specialist lens they need, when they need it, without holding thousands of words of unused text in the prompt for every invocation. Bans on sub-agents, dispatch packets, and coordination files stay in force.

## License

MIT. See `LICENSE` at repo root.
