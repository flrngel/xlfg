# xlfg repo guide

Read `NEXT_AGENT_CONTEXT.md` first. It is the required handoff document and explains why v6 looks the way it does.

## Core principles (v6)

- `/xlfg` is one autonomous SDLC run held entirely in the main model's context. It does not dispatch sub-agents, does not chain hidden phase skills, and does not produce per-phase file artifacts.
- `/xlfg-debug` is the diagnosis-only sibling. It cannot edit source — `allowed-tools` excludes `Edit`, `MultiEdit`, `Write` on purpose.
- The 8-phase SDLC (recall → intent → context → plan → implement → verify → review → compound) is a discipline, not a file layout. Each phase is a separate mental pass in the main model.
- Specialist expertise (PM, architect, security, perf, UX, test strategist, runner/reducer, reviewer) lives as lenses inside the `/xlfg` body, not as separate agent files.
- The repo ships no `docs/xlfg/runs/` tree, no `spec.md`, no `workboard.md`, no `phase-state.json`, no ledger. If you find yourself adding any of those, you're reinventing v5.
- Review confirms quality; it does not create quality.
- Proof before claim. A run isn't done until the test command actually ran green.

## Important paths

- `NEXT_AGENT_CONTEXT.md` — required handoff, explains v5 → v6 migration
- `plugins/xlfg-engineering/commands/xlfg.md` — the full SDLC guide (the real product)
- `plugins/xlfg-engineering/commands/xlfg-debug.md` — the diagnosis-only guide
- `plugins/xlfg-engineering/scripts/audit_harness.py` — CI self-audit
- `plugins/xlfg-engineering/CHANGELOG.md` — v6 migration notes
- `plugins/xlfg-engineering/CLAUDE.md` — plugin development rules
- `tests/test_xlfg_v6.py` — the invariants that guard the v6 shape
- `docs/` — archival research notes from the v3–v5 era (kept for reading, not active guidance)

## What NOT to reintroduce

See `plugins/xlfg-engineering/CLAUDE.md` for the full drift-prevention list. Summary: no agents directory, no skills directory, no Codex surface, no hidden-skill chaining, no dispatch-contract headers in command bodies, no Stop or SubagentStop hooks.
