# xlfg-engineering plugin development

## What this plugin is (v6.5+)

Three slash commands, 5 hidden phase skills under `skills/xlfg-*-phase/`, 27 on-demand specialist lens skills under `skills/xlfg-*/` (directories without the `-phase` suffix), **4 sanctioned phase agents under `agents/`**, one audit script, one hooks file, two manifests, plus a minimal durable archive convention under `docs/xlfg/`. No v5 file-based *coordination* state, no Codex surface, no ledger, no nested delegation beyond a single conductor→phase-agent hop.

- `/xlfg` and `/xlfg-debug` are **conductors** — each dispatches a pipeline split between phase **skills** (in-context) and phase **agents** (delegated). These are where autonomous work lives.
- `/xlfg-init` is a **scaffold** — one-shot, idempotent, runs in the user's project CWD. Patches `.gitignore` and seeds `docs/xlfg/runs/` with a `.gitkeep` and a short README. Not a conductor, not a pipeline, no phases loaded.

The conductors carry the pipeline order, loopback rules, and operating contract. Decision-driving phase bodies live in the skills and load just-in-time via the `Skill` tool. Exploration-heavy phase bodies live in the agents and are dispatched via the `Agent` tool, returning a distilled synthesis instead of accumulating their tool-call log in the conductor's context. Specialist bodies load on-demand from within phase skills *or* phase agents when a focused lens is worth the context cost. That context-budget discipline — in two complementary directions — is the whole reason the split exists.

### Why v6.5 split phases into skills + agents

v6.0 killed all sub-agents because the v5 dispatch-contract tax (PRIMARY_ARTIFACT, OWNERSHIP_BOUNDARY, CONTEXT_DIGEST, RETURN_CONTRACT, etc.) cost more than the isolation bought. v6.2–v6.4 proved the skill-only pattern works for decision-driving phases, but left token discipline on the table for exploration-heavy phases: recall's git-log sweeps, context's file fan-out, verify's raw test output, and review's diff reads all accumulated in the conductor context even though the conductor only needed each phase's *conclusion*.

v6.5's carve-out is narrow by design: exactly **4** whitelisted phase-agents, each carrying a plain-prose `## Return format` section that replaces the v5 dispatch-packet machinery. The agent produces a tool-call log in *its* context; the conductor receives only the synthesis. No `PRIMARY_ARTIFACT` packet, no `CONTEXT_DIGEST`, no completion barriers — the same forbidden-token sweep that caught v5 regressions applies to the new agents too.

**What v6.5 did NOT do, and why.** v6.3.0's durable lesson holds for specialists: "specialist expertise belongs in skills that load on-demand, not in sub-agents with dispatch packets." Specialists sit on shared context with their parent (they apply a lens to content the parent already has); moving them to agents would re-serialize that overlap for no token win. Phases are the opposite — they generate their own context from scratch. That's why v6.5 is a carve-out, not a reversal. Specialists stay as skills.

### Five things that look similar but aren't

- **Phase skills** (v6.2+, kept with reduced scope): `skills/xlfg-<phase>-phase/SKILL.md`. **5** files (intent, plan, implement, compound, debug), each carrying one phase's philosophy. The conductors dispatch these via the `Skill` tool — they load just-in-time, run in the main model's context, and return. This is the architectural decision v6.2 restored from v5.
- **Specialist lens skills** (v6.3+, kept): `skills/xlfg-<name>/SKILL.md` (no `-phase` suffix). 27 files, each carrying one specialist's lens (security, root-cause, test-strategist, UX, etc.). Phase skills *and* phase agents advertise them in an "Optional specialist skills" section and load them via `Skill` when a focused lens is worth the context cost. They are *skills* running in their loader's context (conductor for skills, agent sub-context for agents), not sub-agents with dispatch packets.
- **Phase agents (v6.5, new)**: `agents/xlfg-<name>.md`. Exactly **4** files — `xlfg-recall`, `xlfg-context`, `xlfg-verify`, `xlfg-review`. Each carries its phase body plus a mandatory `## Return format` section. The conductors dispatch them via the `Agent` tool; they run in their own sub-context and return a structured-prose synthesis. This is the v6.5 carve-out from the v6.0 agents ban.
- **Coordination files** (v5, dead): `spec.md`, `workboard.md`, `phase-state.json`, `task-division.md`, `verification.md`, etc. Written *during* a run by one phase so a *later phase* (or a sub-agent) can read them. These were the v5 sub-agent orchestration substrate. v6.5 phase agents don't need them either — the conductor briefs each agent via its invocation prompt, the agent returns a structured synthesis, and that's the whole contract.
- **Durable archive** (v6.1+, kept): `docs/xlfg/current-state.md`, `docs/xlfg/runs/<RUN_ID>/run-summary.md`, `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Written *at the end* of a run so a *future session* (new context window) can recall what happened. Cross-session memory, not intra-run coordination.

If you're tempted to:
- **Add a 5th phase agent** (or any agent file beyond the SANCTIONED_AGENTS whitelist): stop. Every expansion needs a written justification naming the token-discipline win (heavy tool log, small distilled output) that motivates it, plus updates to `SANCTIONED_AGENTS` in both `scripts/audit_harness.py` and `tests/test_xlfg_v6.py`. `test_no_unsanctioned_agents_or_codex` catches drift. Specialists do NOT qualify — they share parent context; see §"Why v6.5 split phases".
- **Re-add a specialist as a sub-agent** (a `.md` file under `agents/` with a specialist name): stop. The v6.3.0 durable lesson applies. Specialists are skills.
- **Add `Agent` or `SendMessage` to any skill's `allowed-tools`**: stop. `test_no_skill_grants_nested_delegation` catches it. Skills run in their loader's context; re-dispatching an agent from a skill would create two levels of delegation. One level only.
- **Add `Agent` or `SendMessage` to any agent's `tools` frontmatter**: stop. `test_agents_do_not_grant_nested_agents` catches it. Same one-level rule.
- **Re-add a dispatch header** (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`) anywhere: stop. `test_commands_do_not_reintroduce_dispatch_contract`, `test_no_skill_references_deleted_v5_dispatch`, and `test_agents_do_not_reintroduce_dispatch_contract` all catch it.
- **Re-add a per-phase coordination file** (`spec.md`, `workboard.md`, etc.): stop. The conductor briefs each agent via its invocation prompt and each skill via its loader context; neither needs file-based handoff state.
- **Collapse skills/agents back into the monolithic command body**: a regression. The context-budget win is the whole point.
- **Remove the `## Return format` section from any agent**: a regression. That section is the contract between agent and conductor; without it the conductor has no structured output to parse.
- **Remove the durable archive writes**: stop. Those are load-bearing for cross-session recall.

## Versioning (required)

Every behavior change MUST update:

1. `plugins/xlfg-engineering/CHANGELOG.md`
2. `plugins/xlfg-engineering/README.md` and the repo-level `README.md`
3. `plugins/xlfg-engineering/.claude-plugin/plugin.json`
4. `plugins/xlfg-engineering/.cursor-plugin/plugin.json`
5. `NEXT_AGENT_CONTEXT.md`

Normal evolution should bump **patch** unless the public entry surface (`/xlfg`, `/xlfg-debug`) or the runtime dependency surface changes materially. v6.5 was a minor bump because the runtime dependency surface changed (added plugin-shipped agents) without the public entry surface changing.

## Read order for future agents

1. `NEXT_AGENT_CONTEXT.md` — why v6.5 looks like this
2. `plugins/xlfg-engineering/commands/xlfg.md` — the conductor body (4 Skill + 4 Agent dispatches)
3. `plugins/xlfg-engineering/commands/xlfg-debug.md` — the diagnosis conductor (2 Skill + 2 Agent dispatches)
4. `plugins/xlfg-engineering/agents/xlfg-*.md` — 4 phase agents (recall, context, verify, review)
5. `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md` — 5 phase skills (intent, plan, implement, compound, debug)
6. `plugins/xlfg-engineering/skills/xlfg-*/SKILL.md` (no `-phase` suffix) — 27 on-demand specialist lens skills
7. `tests/test_xlfg_v6.py` — the invariants
8. `plugins/xlfg-engineering/CHANGELOG.md` — history

## Entry model

- Public plugin entrypoints: `/xlfg-engineering:xlfg`, `/xlfg-engineering:xlfg-debug`, `/xlfg-engineering:xlfg-init` — aliased as `/xlfg`, `/xlfg-debug`, `/xlfg-init` via `name:` frontmatter. All three aliases are load-bearing; do not remove the `name:` line.
- Each **conductor** (`/xlfg`, `/xlfg-debug`) dispatches its pipeline via **both** `Skill(xlfg-engineering:xlfg-<phase>-phase *)` grants (for skill-backed phases) and the `Agent` tool (for agent-backed phases). The 4 sanctioned phase-agents are referenced by bare name (e.g., `xlfg-recall`) in the conductor body; the `subagent_type` argument to the Agent tool is resolved against `plugins/xlfg-engineering/agents/<name>.md`.
- Conductors do **not** grant specialist lens skills. Each phase skill and phase agent names the specialists it may load in its own `allowed-tools`/`tools` frontmatter; the conductor is pure dispatch and never loads a specialist itself. (Pre-v6.5.1 conductors enumerated all 27 specialists redundantly — removed as dead weight.)
- Phase skills grant `Skill(xlfg-engineering:xlfg-<specialist> *)` only for the specialists they advertise; phase agents do the same in their `tools:` frontmatter. Intentional narrowing on both sides.
- The **scaffold** (`/xlfg-init`) grants **no** `Skill(...)` entries and **no** `Agent` — it is not a conductor and must not dispatch anything. `allowed-tools` is minimal: `Read, Edit, Write, Bash, Glob, LS`. `test_xlfg_init_is_project_scaffolding` and `test_xlfg_init_does_not_grant_agent` guard this.
- Do not reference repo-relative plugin file paths from a command. Installed plugins are not laid out like the source repo.
- v6.5 has no sub-commands, one sanctioned level of delegation (conductor → 4 whitelisted phase-agents), no Codex surface. The bounded tree is enforced by the test suite.

## Context-budget discipline

Claude Code loads `description:` fields at session start. Keep commands, skills, and agents **≤ 220 characters** for `description`. Put examples and long guidance in the body (loads on invocation).

## Safety

- `/xlfg` is autonomous by default. It must never hand back to the user except on true human-only blockers (missing secrets, destructive external approval, correctness-changing ambiguity it can't ground from the repo).
- `/xlfg` must always use deterministic recall (git log, grep, existing docs) before broad repo fan-out. In v6.5 recall is a phase agent; its Return format is what the conductor reads.
- `/xlfg` must resolve intent before broad repo fan-out; the intent contract lives in the model's own context, not in a file.
- `/xlfg` must never claim success unless proof actually ran and returned green. In v6.5 verify is a phase agent; its `VERIFY RESULT: GREEN|RED|FAILED` classification line is what the conductor reads.
- `/xlfg-debug` must not edit product source, tests, fixtures, migrations, or configs. Enforced by `allowed-tools` (no `Edit`, `MultiEdit`) and by the v6.5 test suite. `Write` is granted narrowly so the debug skill can create `docs/xlfg/runs/<RUN_ID>/diagnosis.md`; that is the only sanctioned Write target.
- Review confirms quality; it does not create quality.

## What NOT to reintroduce

The v6.5 test suite guards against drift in two directions — back toward the v5 architecture, and back toward the v6.4 pre-agents shape. These will trip it:

- Agent files under `plugins/xlfg-engineering/agents/` with a stem outside `SANCTIONED_AGENTS` (`xlfg-recall`, `xlfg-context`, `xlfg-verify`, `xlfg-review`). Any expansion needs an entry in both `SANCTIONED_AGENTS` constants (audit + tests) and a documented justification. Specialists do not qualify.
- Subdirectories under `agents/` (e.g., `_shared/`, `planning/`, `implementation/` — the v5 shape). Agents live as bare files.
- Skill directories under `skills/` beyond the 5 `xlfg-<phase>-phase/` + 27 named specialist lens skills. Adding a new one is a deliberate architectural change; expand `EXPECTED_PHASE_SKILLS` or `EXPECTED_SPECIALIST_SKILLS` in both the audit and test suite first.
- A `plugins/xlfg-engineering/codex/` directory or `.codex-plugin/` manifest.
- More than `audit_harness.py` (plus the two `.mjs` no-op shims) under `scripts/`.
- Dispatch-contract tokens anywhere: `PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`, `SubagentStop`, `subagent-stop-guard`, `ledger-append`. These are swept in commands, skills, AND agents.
- Stop or SubagentStop hook registrations in `hooks.json`.
- `Agent` or `SendMessage` tokens in the `allowed-tools`/`tools` frontmatter of any skill or agent. Conductor grants of `Agent` are expected and required for the 4 phase-agent dispatches; `/xlfg-init` must never grant `Agent`.
- `## Return format` absence from any agent. The structured-prose contract is the whole point of delegating a phase to an agent.

If you have a genuine case for re-adding or expanding any of these, open a discussion first. The scope of v6.5's carve-out was a decision, not an oversight.
