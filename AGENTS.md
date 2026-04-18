# xlfg repo guide

Read `NEXT_AGENT_CONTEXT.md` first. It is the required handoff document and explains why v6.3 looks the way it does.

## Core principles (v6.3)

- `/xlfg` is a conductor that dispatches 8 hidden phase skills via the `Skill` tool, in order: recall → intent → context → plan → implement → verify → review → compound. Each skill loads just-in-time and runs in the main model's own context. No sub-agents, no nested delegation.
- `/xlfg-debug` is the diagnosis-only conductor dispatching 4 skills (recall → intent → context → debug). Its `allowed-tools` excludes `Edit` and `MultiEdit`; `Write` is granted narrowly for `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.
- The 8-phase SDLC is a discipline implemented as 9 phase skills under `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md`. Three are shared between conductors (recall, intent, context); five are `/xlfg`-only; one is `/xlfg-debug`-only.
- Specialist expertise (PM, architect, security, perf, UX, test strategist, runner/reducer, reviewer) lives as **27 hidden on-demand lens skills** under `plugins/xlfg-engineering/skills/xlfg-<name>/SKILL.md` (no `-phase` suffix). Phase skills list the applicable specialists and load them via the `Skill` tool only when the work calls for that expertise. They are *skills*, not sub-agents.
- Durable cross-session memory lives under `docs/xlfg/` — `current-state.md`, `runs/<RUN_ID>/run-summary.md`, `runs/<RUN_ID>/diagnosis.md`. No `.xlfg/` coordination state, no `spec.md`, no `workboard.md`, no ledger. If you find yourself adding any of those, you're reinventing v5.
- Review confirms quality; it does not create quality.
- Proof before claim. A run isn't done until the test command actually ran green.

## Important paths

- `NEXT_AGENT_CONTEXT.md` — required handoff, explains v5 → v6.2 migration
- `plugins/xlfg-engineering/commands/xlfg.md` — the SDLC conductor (dispatches 8 skills)
- `plugins/xlfg-engineering/commands/xlfg-debug.md` — the diagnosis conductor (dispatches 4 skills)
- `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md` — 9 phase skills (where the real phase work lives)
- `plugins/xlfg-engineering/skills/xlfg-*/SKILL.md` (directories without `-phase` suffix) — 27 on-demand specialist lens skills
- `plugins/xlfg-engineering/scripts/audit_harness.py` — CI self-audit (5 checks)
- `plugins/xlfg-engineering/CHANGELOG.md` — v6 evolution notes
- `plugins/xlfg-engineering/CLAUDE.md` — plugin development rules
- `tests/test_xlfg_v6.py` — the 37 invariants that guard the v6.3 shape
- `docs/` — archival research notes from the v3–v5 era (kept for reading, not active guidance)

## What NOT to reintroduce

See `plugins/xlfg-engineering/CLAUDE.md` for the full drift-prevention list. Summary: no `agents/` directory, no skill directories beyond the 9 phase skills + 27 specialist lenses (adding a new specialist requires expanding `EXPECTED_SPECIALIST_SKILLS` in both `audit_harness.py` and `tests/test_xlfg_v6.py`), no Codex surface, no nested delegation (`Agent`/`SendMessage` in any `allowed-tools`), no dispatch-contract headers (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, etc.) in commands or skills, no Stop or SubagentStop hooks.
