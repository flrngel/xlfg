# xlfg — current state

Read this first when entering this repo with xlfg.

## What this project is

xlfg is an autonomous proof-first SDLC plugin for Claude Code, designed for Opus-class models. Shape at v6.5: two conductor slash commands (`/xlfg`, `/xlfg-debug`) each dispatching a mixed pipeline — some phases are **skills** (run in conductor's context), some are **agents** (run in their own sub-contexts and return a distilled synthesis). `/xlfg` is 4 skills + 4 agents; `/xlfg-debug` is 2 skills + 2 agents. Alongside the phases, 27 hidden specialist lens skills load on-demand from whichever phase needs them. `/xlfg-init` is a project scaffold.

## Load-bearing truths

- The three kinds of prompt asset split by naming and directory: **phase skills** live at `skills/xlfg-<phase>-phase/SKILL.md` (5 files — intent, plan, implement, compound, debug); **phase agents** live at `agents/xlfg-<name>.md` (4 files — recall, context, verify, review); **specialist lens skills** live at `skills/xlfg-<name>/SKILL.md` without the `-phase` suffix (27 files). The audit harness and test suite enforce all three sets via `EXPECTED_PHASE_SKILLS`, `EXPECTED_SPECIALIST_SKILLS`, and `SANCTIONED_AGENTS`. Any addition requires editing `scripts/audit_harness.py` and `tests/test_xlfg_v6.py` together.
- v6.5's two-sided rule: **agents for phases that generate their own context from scratch (heavy exploration log, small distilled conclusion)**; **skills for phases or lenses that sit on shared context with their loader**. Specialists are skills, not agents — moving them to agents would re-serialize shared context for no token win. Any proposal to add a 5th phase-agent must name the token-discipline win.
- Each phase agent's body carries a mandatory `## Return format` section. That prose template is the contract between agent and conductor — if you remove it, `test_every_agent_carries_return_format` catches it. Dispatch-contract tokens (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`, `SubagentStop`) remain forbidden across commands, skills, AND agents.
- One level of delegation only: conductors dispatch phase skills + phase agents; phase skills and phase agents may load specialist skills; nothing re-dispatches agents. `Agent`/`SendMessage` are banned in every skill and agent; conductor grants of `Agent` are expected and required (except `/xlfg-init` which must not grant either).
- Durable cross-session memory lives at `docs/xlfg/current-state.md` (this file) + `docs/xlfg/runs/<RUN_ID>/{run-summary,diagnosis}.md`. No `.xlfg/` directory, no `spec.md`/`workboard.md`/`phase-state.json`. If you find yourself wanting per-run coordination files, you are reinventing v5.
- **Contracts name their verifying command.** v6.0 cut enforcement hooks and bet on prompt discipline; that bet pays off for pipeline flow but leaks whenever a safety-relevant rule is expressed as prose alone. The v6.5.3 fix pattern: when a contract matters (git state, sanctioned Write path, completion-summary integrity), the prompt must name the command that proves it held (e.g., `git status --porcelain`, "verified via …") AND the test suite must pin that string. Prompt-only stays the rule — hooks are not coming back — but prompts must be executable in the sense that a reader can *see the check*, not just read a promise.

## Known traps

- Agent names are substrings of specialist names (`xlfg-verify` ⊂ `xlfg-verify-runner`). Tests that check "conductor body references agent X" use backtick-delimited needles (`` `xlfg-verify` ``) and search the body post-frontmatter via the `_body()` helper, to avoid false hits in allowed-tools grants.
- Monolithic phase bodies (v6.0 shape) cost tokens on every invocation. Do not inline specialist expertise into phase bodies. Load specialists via `Skill` on-demand instead.
- `.xlfg/` is explicitly not a directory in v6+. Writing to it is a regression.
- The conductors do **not** grant specialist lens skills (6.5.1 removed the redundancy). Specialists load from within phase skills and phase agents, each of which holds its own narrow specialist grants. Adding a new specialist means updating both `EXPECTED_SPECIALIST_SKILLS` tuples (audit harness + test file) plus the relevant phase skill's `allowed-tools` or phase agent's `tools:` frontmatter — never the conductor's. `test_conductor_does_not_grant_specialists_directly` guards the rule.

## Active constraints

- Runtime dependencies: `python3` on PATH (for CI audit). No Node. Zero runtime deps for end users.
- Plugin manifests (`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`) must stay version-synced; `test_version_sync` enforces it.
- Runtime dispatch resolution of `subagent_type: "xlfg-<name>"` to `agents/xlfg-<name>.md` is not test-covered; if a future Claude Code release changes plugin-agent resolution semantics, the first real `/xlfg` run will surface it.
