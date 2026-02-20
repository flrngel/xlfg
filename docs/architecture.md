# Architecture

xlfg ships two complementary layers:

1. **A Claude Code plugin** (commands/agents/skills)
2. **A lightweight CLI** (`xlfg`) that creates the same file structure and can run verification with logs

They share the same core artifact model:

- Durable artifacts live in `docs/xlfg/` (commit these)
- Ephemeral logs live in `.xlfg/` (gitignore these)

## Artifact model

Each run has:

- `docs/xlfg/runs/<run-id>/context.md` — original request + assumptions/constraints
- `.../spec.md` — acceptance criteria + edge cases
- `.../plan.md` — task breakdown + quality gates
- `.../verification.md` — evidence of tests/lint/build runs
- `.../reviews/` — multi-lens review outputs
- `.xlfg/runs/<run-id>/verify/` — raw command output logs

## File-based subagent protocol

Subagents should:

1. Read `context.md` (and `spec.md`/`plan.md` if present)
2. Write exactly one output file in the run folder
3. Avoid editing shared files unless explicitly assigned

This reduces conflicts and keeps the system deterministic.
