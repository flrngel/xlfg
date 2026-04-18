# xlfg-engineering plugin development

## What this plugin is (v6.1+)

Two slash commands (`/xlfg`, `/xlfg-debug`), one audit script, one hooks file, two manifests, plus a minimal durable archive convention under `docs/xlfg/`. No sub-agents, no phase skills, no file-based run *coordination* state, no Codex surface, no ledger. The runtime is pure inline prose the main model reads at invocation time.

### What's a coordination file vs. a durable archive?

This distinction bit v6.0.0. They look the same — both are .md files under `docs/xlfg/` — but they're different concerns:

- **Coordination files** (v5, dead): `spec.md`, `workboard.md`, `phase-state.json`, `task-division.md`, `verification.md`, etc. Written *during* a run by one phase so a *later phase* (or a sub-agent) can read them. These were the sub-agent orchestration substrate. Strong reasoners hold this in context; the files were pure overhead.
- **Durable archive** (v6.1+, kept): `docs/xlfg/current-state.md`, `docs/xlfg/runs/<RUN_ID>/run-summary.md`, `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Written *at the end* of a run so a *future session* (new context window) can recall what happened. Cross-session memory, not intra-run coordination.

If you're tempted to re-add a specialist agent, a hidden phase skill, a dispatch header, or a per-phase *coordination* artifact: stop. The v6 test suite will catch you (`tests/test_xlfg_v6.py::TestPluginShape` and `TestCommands`). The decision to remove those surfaces was deliberate.

If you're tempted to remove the durable archive writes (`run-summary.md`, `diagnosis.md`, `current-state.md`): also stop. Those are load-bearing for cross-session recall, and the test suite asserts the command bodies wire them in.

## Versioning (required)

Every behavior change MUST update:

1. `plugins/xlfg-engineering/CHANGELOG.md`
2. `plugins/xlfg-engineering/README.md` and the repo-level `README.md`
3. `plugins/xlfg-engineering/.claude-plugin/plugin.json`
4. `plugins/xlfg-engineering/.cursor-plugin/plugin.json`
5. `NEXT_AGENT_CONTEXT.md`

Normal evolution should bump **patch** unless the public entry surface (`/xlfg`, `/xlfg-debug`) or the runtime dependency surface changes materially.

## Read order for future agents

1. `NEXT_AGENT_CONTEXT.md` — why v6 looks like this
2. `plugins/xlfg-engineering/commands/xlfg.md` — the real body of the run
3. `plugins/xlfg-engineering/commands/xlfg-debug.md` — the real body of the diagnosis
4. `tests/test_xlfg_v6.py` — the invariants
5. `plugins/xlfg-engineering/CHANGELOG.md` — history

## Entry model

- Public plugin entrypoint: `/xlfg-engineering:xlfg` (aliased as `/xlfg` via `name: xlfg` in command frontmatter).
- Secondary entrypoint: `/xlfg-engineering:xlfg-debug` (aliased as `/xlfg-debug`).
- Both aliases are load-bearing; do not remove the `name:` frontmatter.
- Do not reference repo-relative plugin file paths from a command. Installed plugins are not laid out like the source repo.
- v6 has no sub-commands, no hidden skills, and no Codex surface. The minimal tree is enforced by the test suite.

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep commands **≤ 220 characters** for `description`. Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg` is autonomous by default. It must never hand back to the user except on true human-only blockers (missing secrets, destructive external approval, correctness-changing ambiguity it can't ground from the repo).
- `/xlfg` must always use deterministic recall (git log, grep, existing docs) before broad repo fan-out.
- `/xlfg` must resolve intent before broad repo fan-out; the intent contract lives in the model's own context, not in a file.
- `/xlfg` must never claim success unless proof actually ran and returned green.
- `/xlfg-debug` must not edit product source, tests, fixtures, migrations, or configs. This is enforced by `allowed-tools` (no `Edit`, `MultiEdit`, `Write`) and by the v6 test suite.
- Review confirms quality; it does not create quality.

## What NOT to reintroduce

The v6 test suite guards against drift back toward the v5 architecture. These things will trip it:

- Files under `plugins/xlfg-engineering/agents/**` (specialists)
- Files under `plugins/xlfg-engineering/skills/**` (phase skills or support skills)
- A `plugins/xlfg-engineering/codex/` directory or `.codex-plugin/` manifest
- More than `audit_harness.py` under `scripts/`
- Dispatch-contract tokens in command bodies: `PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`
- Stop or SubagentStop hook registrations in `hooks.json`
- `Skill(...)`, `Agent`, or `SendMessage` tokens in the `allowed-tools` frontmatter of either command

If you have a genuine case for re-adding any of these, open a discussion first. The removal was a decision, not an oversight.
