# xlfg repo guide

Read `NEXT_AGENT_CONTEXT.md` first. It is the required handoff document and explains why v6.5 looks the way it does.

## Core principles (v6.5)

- `/xlfg` is a conductor that dispatches a mixed pipeline via the `Skill` tool (for decision-driving phases) and the `Agent` tool (for exploration-heavy phases), in order: **recall** (agent) → intent (skill) → **context** (agent) → plan (skill) → implement (skill) → **verify** (agent) → **review** (agent) → compound (skill). Skill phases run in the main model's context; agent phases run in their own sub-contexts and return a distilled synthesis via a mandatory `## Return format` section.
- `/xlfg-debug` is the diagnosis-only conductor dispatching 4 phases: **recall** (agent) → intent (skill) → **context** (agent) → debug (skill). Its `allowed-tools` excludes `Edit` and `MultiEdit`; `Write` is granted narrowly for `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.
- Phase skills live at `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md` — 5 files (intent, plan, implement, compound, debug).
- Phase agents live at `plugins/xlfg-engineering/agents/xlfg-*.md` — 4 files (recall, context, verify, review). The `SANCTIONED_AGENTS` whitelist in the audit harness and test suite is the mechanical gate; expanding it requires justifying the token-discipline win.
- Specialist expertise (PM, architect, security, perf, UX, test strategist, runner/reducer, reviewer) lives as **27 hidden on-demand lens skills** under `plugins/xlfg-engineering/skills/xlfg-<name>/SKILL.md` (no `-phase` suffix). Phase skills *and* phase agents advertise their applicable specialists and load them via the `Skill` tool when needed. They are *skills*, not sub-agents — that's the v6.3.0 decision, still in force.
- One level of delegation only: conductors dispatch phase skills + phase agents; phase skills and phase agents load specialist skills; nothing re-dispatches agents.
- Durable cross-session memory lives under `docs/xlfg/` — `current-state.md`, `runs/<RUN_ID>/run-summary.md`, `runs/<RUN_ID>/diagnosis.md`. No `.xlfg/` coordination state, no `spec.md`, no `workboard.md`, no ledger. If you find yourself adding any of those, you're reinventing v5.
- Review confirms quality; it does not create quality.
- Proof before claim. A run isn't done until the test command actually ran green.

## Important paths

- `NEXT_AGENT_CONTEXT.md` — required handoff, explains v6.5 carve-out rationale
- `plugins/xlfg-engineering/commands/xlfg.md` — the SDLC conductor (4 Skill + 4 Agent dispatches)
- `plugins/xlfg-engineering/commands/xlfg-debug.md` — the diagnosis conductor (2 Skill + 2 Agent dispatches)
- `plugins/xlfg-engineering/agents/xlfg-*.md` — 4 phase agents (recall, context, verify, review)
- `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md` — 5 phase skills (intent, plan, implement, compound, debug)
- `plugins/xlfg-engineering/skills/xlfg-*/SKILL.md` (directories without `-phase` suffix) — 27 on-demand specialist lens skills
- `plugins/xlfg-engineering/scripts/audit_harness.py` — CI self-audit (6 checks)
- `plugins/xlfg-engineering/CHANGELOG.md` — v6 evolution notes
- `plugins/xlfg-engineering/CLAUDE.md` — plugin development rules
- `tests/test_xlfg_v6.py` — 54 invariants that guard the v6.5 shape
- `docs/` — archival research notes from the v3–v5 era (kept for reading, not active guidance)

## What NOT to reintroduce

See `plugins/xlfg-engineering/CLAUDE.md` for the full drift-prevention list. Summary: no agent files beyond `SANCTIONED_AGENTS` (re-adding a specialist as an agent is the regression v6.3.0 warned against), no subdirectories under `agents/` (v5 had `_shared/`, `planning/`, etc.), no skill directories beyond the 5 phase skills + 27 specialist lenses (adding a new one requires expanding `EXPECTED_PHASE_SKILLS`/`EXPECTED_SPECIALIST_SKILLS` in both `audit_harness.py` and `tests/test_xlfg_v6.py`), no Codex surface, no `Agent` or `SendMessage` in any *skill* or *agent*'s tool grants (conductor grants of `Agent` are expected; `/xlfg-init` must never grant it), no dispatch-contract headers (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, etc.) in commands, skills, or agents, no Stop or SubagentStop hooks, no agent missing a `## Return format` section.
