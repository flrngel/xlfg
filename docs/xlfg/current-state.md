# xlfg — current state

Read this first when entering this repo with xlfg.

## What this project is

xlfg is an autonomous proof-first SDLC plugin for Claude Code, designed for Opus-class models. Shape at v6.4: two conductor slash commands (`/xlfg`, `/xlfg-debug`) dispatching 9 hidden phase skills, 27 hidden specialist lens skills that phase skills load on-demand, plus one scaffold command (`/xlfg-init`) that bootstraps a user's project with the right `.gitignore` entries and a committable `docs/xlfg/runs/` directory. All skills run in the main model's own context — no sub-agents, no nested delegation.

## Load-bearing truths

- The 36 skills split into two kinds by naming: phase skills are `skills/xlfg-<phase>-phase/SKILL.md` (9 of them); specialist lens skills are `skills/xlfg-<name>/SKILL.md` without the `-phase` suffix (27 of them). The audit harness and test suite enforce both sets via `EXPECTED_PHASE_SKILLS` + `EXPECTED_SPECIALIST_SKILLS`. Adding or renaming any skill requires editing `scripts/audit_harness.py` and `tests/test_xlfg_v6.py` together.
- Specialist expertise is *skills*, not sub-agents. The `plugins/xlfg-engineering/agents/` directory is gone for good (v6.0 philosophy cut) and `test_no_agents_or_codex` enforces this. Never recreate it. If a specialist needs tools beyond `Read/Grep/Glob/LS/Bash`, add them to that specialist's own frontmatter — do not reintroduce packet contracts.
- `Skill(xlfg-engineering:xlfg-<name> *)` grants in `allowed-tools` are expected and correct — that's how conductors dispatch phases and how phase skills optionally load specialists. `Agent` and `SendMessage` grants are forbidden anywhere and tests catch them.
- Dispatch-contract tokens (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`, `SubagentStop`) are forbidden in every command and skill body. The forbidden-token sweep covers all 36 skills.
- Durable cross-session memory lives at `docs/xlfg/current-state.md` (this file) + `docs/xlfg/runs/<RUN_ID>/{run-summary,diagnosis}.md`. No `.xlfg/` directory, no `spec.md`/`workboard.md`/`phase-state.json`. If you find yourself wanting per-run coordination files, you are reinventing v5.

## Known traps

- Monolithic phase bodies (v6.0 shape) cost tokens on every invocation. Do not inline specialist expertise into phase bodies. Load specialists via `Skill` on-demand instead.
- `.xlfg/` is explicitly not a directory in v6+. Writing to it is a regression.
- The conductors' `allowed-tools` is long and load-bearing. Adding a new specialist means updating both conductor grants (if it should be reachable from the conductor) and the relevant phase skill's grants, plus both `EXPECTED_SPECIALIST_SKILLS` lists.

## Active constraints

- Runtime dependencies: `python3` on PATH (for CI audit). No Node. Zero runtime deps for end users.
- Plugin manifests (`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`) must stay version-synced; `test_version_sync` enforces it.
