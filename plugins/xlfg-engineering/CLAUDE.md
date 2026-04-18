# xlfg-engineering plugin development

## What this plugin is (v6.4+)

Three slash commands, 9 hidden phase skills under `skills/xlfg-*-phase/`, 27 on-demand specialist lens skills under `skills/xlfg-*/` (directories without the `-phase` suffix), one audit script, one hooks file, two manifests, plus a minimal durable archive convention under `docs/xlfg/`. No sub-agents, no nested delegation, no v5 file-based *coordination* state, no Codex surface, no ledger.

- `/xlfg` and `/xlfg-debug` are **conductors** — each dispatches a pipeline of hidden phase skills. These are where autonomous work lives.
- `/xlfg-init` is a **scaffold** — one-shot, idempotent, runs in the user's project CWD. Patches `.gitignore` and seeds `docs/xlfg/runs/` with a `.gitkeep` and a short README. Not a conductor, not a pipeline, no phase skills loaded.

The conductors carry the pipeline order, loopback rules, and operating contract. The phase bodies live in the skills and load just-in-time via the `Skill` tool. Specialist bodies likewise load on-demand from within phase skills when a focused lens is worth the context cost. That context-budget discipline is the whole reason the split exists.

### Four things that look similar but aren't

- **Phase skills** (v6.2+, kept): `skills/xlfg-<phase>-phase/SKILL.md`. Nine files, each carrying one phase's philosophy. The `/xlfg` and `/xlfg-debug` conductors dispatch these via the `Skill` tool — they load just-in-time, run in the main model's context, and return. This is the architectural decision v6.2 restored from v5.
- **Specialist lens skills** (v6.3+, kept): `skills/xlfg-<name>/SKILL.md` (no `-phase` suffix). 27 files, each carrying one specialist's lens (security, root-cause, test-strategist, UX, etc.). Phase skills advertise them in an "Optional specialist skills" section and load them via `Skill` when a focused lens is worth the context cost. They are *skills* running in the conductor's own context, not sub-agents with dispatch packets.
- **Coordination files** (v5, dead): `spec.md`, `workboard.md`, `phase-state.json`, `task-division.md`, `verification.md`, etc. Written *during* a run by one phase so a *later phase* (or a sub-agent) can read them. These were the sub-agent orchestration substrate. v6 skills do not need them — each skill runs in the conductor's own context with access to the same working memory.
- **Durable archive** (v6.1+, kept): `docs/xlfg/current-state.md`, `docs/xlfg/runs/<RUN_ID>/run-summary.md`, `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Written *at the end* of a run so a *future session* (new context window) can recall what happened. Cross-session memory, not intra-run coordination.

If you're tempted to:
- **Re-add a specialist sub-agent** (under `agents/`): stop. The specialists exist as *skills* now, not agents. `test_no_agents_or_codex` will catch the directory.
- **Add `Agent` or `SendMessage` to any skill's allowed-tools**: stop. `test_no_skill_grants_nested_delegation` catches it. `Skill(...)` grants are fine and expected — that's how the conductor dispatches phases and how phase skills optionally load specialists.
- **Re-add a dispatch header** (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`) anywhere: stop. `test_commands_do_not_reintroduce_dispatch_contract` and `test_no_skill_references_deleted_v5_dispatch` both catch it.
- **Re-add a per-phase coordination file** (`spec.md`, `workboard.md`, etc.): stop. The audit harness does not catch this directly, but any skill that writes one is a regression — open a discussion first.
- **Collapse skills back into the monolithic command body**: also a regression. The context-budget win is the whole point. `test_xlfg_dispatches_eight_phase_skills` and `test_all_expected_skills_exist` catch it.
- **Remove the durable archive writes**: stop. Those are load-bearing for cross-session recall.
- **Add a new skill directory outside the 9 phase + 27 specialist set**: stop unless it's a deliberate architectural change. If it is, expand `EXPECTED_SPECIALIST_SKILLS` in `scripts/audit_harness.py` and `tests/test_xlfg_v6.py` first, then add the SKILL.md using the 5-section template.

## Versioning (required)

Every behavior change MUST update:

1. `plugins/xlfg-engineering/CHANGELOG.md`
2. `plugins/xlfg-engineering/README.md` and the repo-level `README.md`
3. `plugins/xlfg-engineering/.claude-plugin/plugin.json`
4. `plugins/xlfg-engineering/.cursor-plugin/plugin.json`
5. `NEXT_AGENT_CONTEXT.md`

Normal evolution should bump **patch** unless the public entry surface (`/xlfg`, `/xlfg-debug`) or the runtime dependency surface changes materially.

## Read order for future agents

1. `NEXT_AGENT_CONTEXT.md` — why v6.3 looks like this
2. `plugins/xlfg-engineering/commands/xlfg.md` — the conductor body
3. `plugins/xlfg-engineering/commands/xlfg-debug.md` — the diagnosis conductor
4. `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md` — the 9 phase skills (where the real phase work lives)
5. `plugins/xlfg-engineering/skills/xlfg-*/SKILL.md` (no `-phase` suffix) — the 27 on-demand specialist lens skills
6. `tests/test_xlfg_v6.py` — the invariants
7. `plugins/xlfg-engineering/CHANGELOG.md` — history

## Entry model

- Public plugin entrypoints: `/xlfg-engineering:xlfg`, `/xlfg-engineering:xlfg-debug`, `/xlfg-engineering:xlfg-init` — aliased as `/xlfg`, `/xlfg-debug`, `/xlfg-init` via `name:` frontmatter. All three aliases are load-bearing; do not remove the `name:` line.
- Each **conductor** (`/xlfg`, `/xlfg-debug`) dispatches its pipeline via the `Skill` tool, granted in `allowed-tools` as `Skill(xlfg-engineering:xlfg-<phase>-phase *)`. Nine phase skills exist under `skills/xlfg-*-phase/SKILL.md`.
- Conductors also grant `Skill(xlfg-engineering:xlfg-<specialist> *)` for each of the 27 on-demand specialist lens skills, so phase skills can load them when the work calls for focused expertise.
- Phase skills grant `Skill(xlfg-engineering:xlfg-<specialist> *)` only for the specialists they advertise; this is intentional narrowing.
- The **scaffold** (`/xlfg-init`) grants **no** `Skill(xlfg-engineering:...)` entries — it is not a conductor and must not dispatch phase skills. `allowed-tools` is minimal: `Read, Edit, Write, Bash, Glob, LS`. `test_xlfg_init_is_project_scaffolding` guards this.
- Do not reference repo-relative plugin file paths from a command. Installed plugins are not laid out like the source repo.
- v6 has no sub-commands, no sub-agents, no Codex surface. The bounded tree is enforced by the test suite.

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep commands **≤ 220 characters** for `description`. Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg` is autonomous by default. It must never hand back to the user except on true human-only blockers (missing secrets, destructive external approval, correctness-changing ambiguity it can't ground from the repo).
- `/xlfg` must always use deterministic recall (git log, grep, existing docs) before broad repo fan-out.
- `/xlfg` must resolve intent before broad repo fan-out; the intent contract lives in the model's own context, not in a file.
- `/xlfg` must never claim success unless proof actually ran and returned green.
- `/xlfg-debug` must not edit product source, tests, fixtures, migrations, or configs. This is enforced by `allowed-tools` (no `Edit`, `MultiEdit`) and by the v6 test suite. `Write` is granted narrowly so the debug skill can create `docs/xlfg/runs/<RUN_ID>/diagnosis.md`; that is the only sanctioned Write target.
- Review confirms quality; it does not create quality.

## What NOT to reintroduce

The v6 test suite guards against drift back toward the v5 architecture. These things will trip it:

- Files under `plugins/xlfg-engineering/agents/**` (sub-agents — gone for good; specialist expertise lives as skills now)
- Skill directories under `skills/` beyond the 9 `xlfg-<phase>-phase/` + 27 named specialist lens skills (adding a new one is a deliberate architectural change; expand `EXPECTED_SPECIALIST_SKILLS` in both the audit and test suite first)
- A `plugins/xlfg-engineering/codex/` directory or `.codex-plugin/` manifest
- More than `audit_harness.py` (plus the two `.mjs` no-op shims) under `scripts/`
- Dispatch-contract tokens anywhere: `PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`, `SubagentStop`
- Stop or SubagentStop hook registrations in `hooks.json`
- `Agent` or `SendMessage` tokens in the `allowed-tools` frontmatter of any command or skill (`Skill(...)` grants are expected and required — they are how the conductor dispatches phases and how phase skills optionally load specialists)

If you have a genuine case for re-adding any of these, open a discussion first. The removal was a decision, not an oversight.
