# xlfg-engineering (v6.5.7)

An autonomous proof-first SDLC guide for Claude Code, designed for Opus-class models.

## What you get

Two conductor commands that dispatch pipelines of hidden phase skills **and** plugin-shipped phase agents, plus one small scaffold command that bootstraps a project to use them.

- `/xlfg "<request>"` — dispatches 8 phases in order: **recall** (agent) → intent (skill) → **context** (agent) → plan (skill) → implement (skill) → **verify** (agent) → **review** (agent) → compound (skill). Skill phases load just-in-time and run in the conductor's own context; agent phases run in their own sub-contexts and return a distilled synthesis. After compound, the conductor commits tracked product changes as one Conventional Commits-style commit (skipped cleanly on investigation-only runs; `docs/xlfg/runs/**` and `.xlfg/**` never staged). Ends by writing `docs/xlfg/runs/<RUN_ID>/run-summary.md` and optionally updating `docs/xlfg/current-state.md`.
- `/xlfg-debug "<request>"` — dispatches 4 phases: **recall** (agent) → intent (skill) → **context** (agent) → debug (skill). Diagnosis-only: `allowed-tools` excludes `Edit` and `MultiEdit`, so product source cannot be modified. Ends by writing `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.
- `/xlfg-init` — one-shot, idempotent project scaffold. Patches the CWD's `.gitignore` with the canonical v6 runs block and creates `docs/xlfg/runs/.gitkeep` + `README.md`. Not a conductor. Run once after installing the plugin in a new project; safe to re-run.

**Phase skills** (5 files) live at `plugins/xlfg-engineering/skills/xlfg-<phase>-phase/SKILL.md`: intent, plan, implement, compound (for `/xlfg`) and debug (for `/xlfg-debug`). They load via the `Skill` tool when their phase fires.

**Phase agents** (4 files) live at `plugins/xlfg-engineering/agents/xlfg-<name>.md`: recall, context, verify, review. Each carries its phase body plus a mandatory `## Return format` section. They dispatch via the `Agent` tool with `subagent_type: "xlfg-<name>"`.

**Specialist lens skills** (27 files) live at `plugins/xlfg-engineering/skills/xlfg-<name>/SKILL.md` (no `-phase` suffix) — `xlfg-security-reviewer`, `xlfg-root-cause-analyst`, `xlfg-test-strategist`, and so on. They are hidden (`user-invocable: false`), carry the same 5-section template, and exist so a phase skill *or* a phase agent can load a focused lens on-demand. Specialists remain *skills*, not agents: they sit on shared context with their loader, so agent serialization would be wasteful. The 4 phase skills that use specialists and the 3 phase agents that use specialists each list the ones they can load.

## Architecture

```
commands/
  xlfg.md          ← conductor: frontmatter + 8-phase pipeline + loopback rules + end-of-run commit
  xlfg-debug.md    ← conductor: frontmatter + 4-phase pipeline + no-source-edits contract
  xlfg-init.md     ← scaffold: idempotent .gitignore + runs-dir bootstrap for user's project
agents/
  xlfg-recall.md   ← phase agent (shared by /xlfg and /xlfg-debug)
  xlfg-context.md  ← phase agent (shared)
  xlfg-verify.md   ← phase agent (/xlfg only)
  xlfg-review.md   ← phase agent (/xlfg only)
skills/
  xlfg-intent-phase/SKILL.md      ← phase skill (shared)
  xlfg-plan-phase/SKILL.md        ← phase skill (/xlfg only)
  xlfg-implement-phase/SKILL.md   ← phase skill (/xlfg only)
  xlfg-compound-phase/SKILL.md    ← phase skill (/xlfg only)
  xlfg-debug-phase/SKILL.md       ← phase skill (/xlfg-debug only)
  xlfg-<specialist>/SKILL.md      ← 27 specialist lens skills (load on-demand from phases)
scripts/
  audit_harness.py  ← CI self-audit (6 checks)
hooks/
  hooks.json        ← ExitPlanMode auto-allow only
```

One level of delegation only: conductors dispatch phase skills + phase agents; phase skills and phase agents may load specialist skills; nothing re-dispatches agents. The test suite enforces this: `Agent`/`SendMessage` are forbidden in any skill or agent's tool grants; `/xlfg-init` cannot grant `Agent` either.

## Why v6.5 mixes skills and agents

Earlier v6 versions kept every phase as a skill for context-budget discipline — phase bodies loaded just-in-time instead of sitting in the command prompt. That worked for decision-driving phases (intent, plan, implement, compound, debug) but left token discipline on the table for exploration-heavy phases: recall's git-log sweeps, context's file fan-out, verify's raw test output, and review's diff reads all accumulated in the conductor context even though the conductor only needed each phase's *conclusion*.

v6.5's carve-out is narrow: exactly 4 phase-agents, each with a plain-prose `## Return format` section that replaces the v5 dispatch-packet machinery (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, etc. remain forbidden — the forbidden-token sweep now covers agent bodies too). The agent's tool-call log stays in *its* context; the conductor gets the synthesis.

**Why specialists stayed as skills.** v6.3.0's durable lesson said *"specialist expertise belongs in skills that load on-demand, not in sub-agents with dispatch packets."* That lesson still holds: specialists apply a focused lens to content the parent already has — they sit on **shared context**, so moving them to agents would re-serialize that overlap for no token win. Phases are the opposite: they **generate** their own context from scratch (scanning history, reading files, running tests). The signal/log gap is large and one-way, which is exactly where agent delegation pays off.

## The durable archive under `docs/xlfg/`

Opus-class models hold one run in context, but context doesn't span sessions. The `docs/xlfg/` tree is how a future session recalls what past runs did:

- `docs/xlfg/current-state.md` — optional, one-page, tracked. The "read this first" handoff. ~300 words max.
- `docs/xlfg/runs/<RUN_ID>/run-summary.md` — one file per `/xlfg` run, fixed template.
- `docs/xlfg/runs/<RUN_ID>/diagnosis.md` — one file per `/xlfg-debug` run, fixed template.

`RUN_ID = <YYYYMMDD>-<HHMMSS>-<kebab-slug>`. Commit this directory to version control.

There is no `.xlfg/` directory in v6.

## What's not in v6.5

If you're migrating from v5 or earlier:

- **Unbounded sub-agents** — v6.5 permits exactly 4 whitelisted phase-agents (the `SANCTIONED_AGENTS` tuple in the audit harness and test suite). Any new agent requires expanding that whitelist with a justification. The 27 specialist-lens files exist as hidden **skills**, not agents.
- **v5 coordination layer** — no `spec.md`, no `workboard.md`, no `phase-state.json`, no `verification.md`, no `test-contract.md`, no ledger schema. The run lives in the conductor's context plus 4 agent sub-contexts; durable memory is the tracked `docs/xlfg/` archive.
- **Dispatch-packet contract** — `PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`, `SubagentStop` are all forbidden tokens. Agents return plain-prose structured output.
- **Stop and SubagentStop hooks** — gone. Only `PermissionRequest` `ExitPlanMode` auto-allow remains.
- **Codex surface** — `.codex-plugin/`, `codex/`, and Codex marketplace wiring are removed. v6 ships on Claude Code (and, via `.cursor-plugin/`, Cursor).
- **`/xlfg-audit`, `/xlfg-status`** — both were tied to the v5 file-state surface and stay gone.
- **`.xlfg/`** — v5 used it for the Stop hook's phase-state file. v6 has no phase-state.

## Installation

```text
/plugin marketplace add flrngel/xlfg
/plugin install xlfg-engineering@flrngel
```

Then, once per project, from the project root:

```
/xlfg-init
```

That patches your `.gitignore` and seeds `docs/xlfg/runs/` with a `.gitkeep` and `README.md` so run summaries stay local but the archive directory is committable. After that:

```
/xlfg add a retry policy to the webhook consumer with exponential backoff
/xlfg-debug the auth middleware drops the session cookie on subdomain crossover
```

## Running the audit locally

```bash
python3 plugins/xlfg-engineering/scripts/audit_harness.py
```

Six checks: version sync, command surface, command frontmatter, forbidden-token sweep (covers commands, skill bodies, **and** agent bodies), skill surface (5 phase skills + 27 specialist skills), agent surface (4 sanctioned phase agents with correct frontmatter + Return format). `--json` for machine output.

## License

MIT. See `LICENSE` at repo root.
