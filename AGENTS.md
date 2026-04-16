# xlfg repo guide

Read `NEXT_AGENT_CONTEXT.md` first. It is the bundle-level handoff document and the fastest way for a new agent to understand what this repo is trying to become.

## Core principles

- `/xlfg` is one autonomous SDLC run by default. Do not reintroduce manual phase slash-command choreography.
- `/xlfg` must always use deterministic recall before broad repo fan-out.
- `/xlfg` must resolve intent before broad repo/context fan-out.
- `spec.md` is the run card and single source of truth, including the intent contract and objective groups.
- Planning must declare concise practical scenario contracts and get `test-readiness.md = READY` before implementation.
- Planning should load optional agents progressively, not automatically.
- Implementation must use explicit agents and targeted proof.
- Verification must run scenario-targeted proof, not only generic repo checks.
- `workboard.md` is execution truth.
- Verification evidence in `verification.md` is proof truth; `proof-map.md` is optional only when it changes a decision.
- Review confirms quality; it does not create quality.
- The repo is the system of record for long-running agent work.
- Intent quality should be measured with artifact-based evaluation, not vibes.

## Important paths

- `NEXT_AGENT_CONTEXT.md` — bundle-level handoff and rationale
- `docs/architecture.md` — current entrypoint and run-file architecture
- `plugins/xlfg-engineering/commands/` — Claude Code plugin commands
- `plugins/xlfg-engineering/agents/` — subagent prompts
- `plugins/xlfg-engineering/skills/` — hidden support skills
- `tests/` — regression tests for plugin shape, version sync, and specialist contracts


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.
