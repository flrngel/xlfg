# Next agent context

## Current state (3.1.0)

3.1.0 targets inter-agent communication waste. The run artifacts now carry a single canonical `status:` field (inside YAML frontmatter), phase-status in `workboard.md` is rendered from `.xlfg/phase-state.json` instead of hand-written per phase, the Claude Code task pane is kept in sync with xlfg's phase list via a startup `TaskCreate` bridge, `ledger.jsonl` has a real schema and a single validating writer, and two specialist lanes (`xlfg-repo-mapper` in context-phase; verify-phase `xlfg-ui-designer` re-fire) are gated instead of unconditional.

What changed:
- `plugins/xlfg-engineering/scripts/subagent-stop-guard.mjs` parses YAML frontmatter `status:` first, falls back to the legacy bare `Status:` first line for backward compatibility. New templates prescribe YAML only.
- 54 agent files (27 × 2 packs) converted from bare `Status: DONE | BLOCKED | FAILED` to YAML frontmatter. Completion-barrier prose, turn-budget rule, and preseed convention all point at the YAML shape.
- `plugins/xlfg-engineering/agents/_shared/output-template.md` (mirrored to standalone) is the single reference for frontmatter / preseed / final-chat shape.
- `plugins/xlfg-engineering/skills/xlfg-context-phase/SKILL.md:29` replaces `always run xlfg-repo-mapper` with a conditional skip when `memory-recall.md` already grep-cites coverage.
- `plugins/xlfg-engineering/skills/xlfg-verify-phase/SKILL.md:34` adds a task-checker-DA-coverage gate to the UI-designer re-fire.
- `plugins/xlfg-engineering/scripts/render-workboard.mjs` (mirrored to standalone) renders the `## Phase status` block from `.xlfg/phase-state.json` between HTML-comment markers. Phase skills no longer write phase-completion rows.
- `plugins/xlfg-engineering/commands/xlfg.md` (and standalone `xlfg/SKILL.md`) add `TaskCreate`/`TaskUpdate`/`TaskList` to `allowed-tools`, and a "Harness task bridge" startup step that creates `xlfg: <phase>` tasks.
- `docs/xlfg/knowledge/ledger-schema.md` is the canonical shape. `plugins/xlfg-engineering/scripts/ledger-append.mjs` is the only allowed writer.

Why this matters:
- Artifact bytes-per-run drop: one status line per artifact instead of two, phase-status rendered once per boundary instead of hand-re-described each phase.
- Harness-task-pane nag is silenced without making `workboard.md` a second source of truth.
- Ledger events stop drifting across runs — schema rejects unknown shapes at write time.
- Specialist theater removed on two common axes (recall vs repo-mapper; UI-designer plan + task-checker + UI-designer verify).

If you continue from here:
- Keep YAML frontmatter as the canonical artifact header shape. The stop-guard's bare-Status fallback is a transition branch, not a long-term contract — future breaking release can remove it.
- When creating a new agent, copy the scaffold from `agents/_shared/output-template.md`; don't reinvent it.
- When appending to `ledger.jsonl`, always go through `scripts/ledger-append.mjs`. Direct `echo >>` is forbidden and will drift again.
- Phase skills still own the task / objective / blocker sections of `workboard.md`. They MUST NOT hand-write phase-status rows — the renderer owns that region.
- The `TaskCreate` bridge is startup-only and completion-only. Do NOT create harness tasks for specialists or sub-packets.
- Bump version in **both** `plugins/xlfg-engineering/.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` for every behavior change.
- Keep plugin and standalone packs in sync. `test_standalone_agent_pack_matches_plugin_agents` + new `test_standalone_stop_guard_matches_plugin` + `test_standalone_renderer_matches_plugin` enforce this at CI time.

Intentionally not done in 3.1.0 (known-open):
- Phase B from the plan (CONTEXT_DIGEST per phase + shared delegation-rules doc) — user deferred.
- O1 scale-tier redesign (XS/S/M/L, SKIPPED terminal state, specialist "lite" variants) — belongs in its own RFC.
- Cost observability (tokens / wall-time / specialist count) and auto run-summary.

## Previous state (3.0.0) — for reference

The main 3.0.0 change was removal of the `xlfg` Python CLI package. The repo is plugin-only — no `pip install`, no console-script entrypoints. Install exclusively via the Claude Code marketplace manifest.

What changed:
- `xlfg/` directory (13 Python source files, ~4700 LoC) deleted entirely
- `pyproject.toml` deleted — no Python packaging surface remains
- `/xlfg-audit` and `/xlfg-init` plugin commands deleted (CLI wrappers)
- `docs/benchmarking.md` and `evals/intent/` deleted (CLI-fed fixtures)
- "prefer the local xlfg helper CLI" wording removed from all commands and phase skills
- `tests/test_xlfg.py` pruned to ~20 plugin/standalone shape tests; `test_versions_are_synced` rewritten to read from plugin.json only
- Version tracking: canonical version is now `plugins/xlfg-engineering/.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`; `xlfg/__init__.py` and `pyproject.toml` are gone

Why this matters:
- Single authoritative install path; no dual-track CLI-or-manual ambiguity in run flow
- Phase skills own the scaffold, recall, and verify work directly via Read/Grep/Glob/Write
- Test suite is leaner and honest; no CLI-import coupling

If you continue from here:
- Do **not** recreate a Python package or pyproject.toml. The plugin-only architecture is intentional.
- Bump version in **both** `plugins/xlfg-engineering/.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` for every behavior change. The `CLAUDE.md` versioning checklist has been updated to reflect these paths.
- Keep plugin and standalone packs in sync (skills, agents, hooks, scripts).

## Previous state (2.9.0) — for reference

2.8.2 closes two residual risks from the 2.8.1 follow-up work:

- `phase-gate.mjs` (both plugin and standalone copies) now exits 0 immediately on empty stdin. Before this change, the hook would read the cwd-relative `.xlfg/phase-state.json` even when no stop-event payload was present, which caused `test_allows_on_empty_stdin` to flake inside an active /xlfg run and, more importantly, let the hook block legitimate non-xlfg invocations that happened to share the cwd.
- The phase-gate fix (2.8.2) and xlfg-debug alias (2.8.1) remain in effect.

2.8.1 added the `/xlfg-debug` short alias. 2.8.1 also introduced `xlfg-ui-designer` (conditional plan-phase + verify-phase specialist for UI-related work).

The main 2.8.0 change (still in effect) is **hardening the conductor itself** — the 2.7.x arc hardened specialists, but the conductor could still silently drop later phases.

What changed:
- a Stop hook (`phase-gate.mjs`) now blocks the conductor from ending before all 8 phases complete
- `.xlfg/phase-state.json` tracks which phases have completed; the Stop hook reads this file to decide block/allow
- verify-fix and review-fix loopback cycles are now capped at 2 iterations to prevent unbounded context growth
- the Stop hook is registered in both plugin `hooks.json` and standalone/plugin conductor frontmatter
- audit module detects `conductor_stop_gate` as a new feature flag

Why this matters:
- production runs were sometimes dropping later phases (review, compound) because the model could stop at any time with no enforcement
- unbounded loopback cycles between verify and implement consumed context without advancing to later phases
- the phase-state file survives context compaction, giving the Stop hook a reliable source of truth

If you continue from here:
- preserve the **one public conductor + hidden phase skills + separated specialists** architecture
- do not flatten back into one monolithic prompt
- do not reintroduce duplicated intent docs
- keep plugin and standalone packs synchronized on conductor frontmatter, hooks, and scripts
- the phase-gate hook has a safety valve (max 3 blocks) — do not remove it or the model may hang when it genuinely cannot make progress


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.

## 2.7.3 note

- Production run found agents exhausting maxTurns: 8 on speculative reads, never writing artifacts. Root cause: bloated "Read first" lists (14 files), no turn budget guidance, and stopHookActive escape hatch letting agents bypass the guard.
- Fix: maxTurns raised to 12 for review + heavy-analysis agents. "Turn budget rule" added to all 26 specialists. Review agents get lean "Context sources" (3+3 files). stopHookActive escape removed. CONTEXT_DIGEST added to review-phase dispatch.
- If you continue from here: preserve the turn budget rule in all new agents, keep maxTurns proportional to workload, and always embed context digests in dispatch packets for read-heavy specialists.

## 2.8.0 note

- Stop hook (`phase-gate.mjs`) reads `.xlfg/phase-state.json` and blocks the conductor from stopping before all 8 phases complete. Safety valve: allows after 3 consecutive blocks or on `max_tokens`.
- Conductor now writes phase-state JSON after startup and updates it after each phase. `block_count` resets to 0 on each phase advance.
- Loopback cap: verify-fix and review-fix loops limited to 2 iterations. After that, escalate to user.
- Registered in plugin `hooks.json` (Stop section) and both conductor frontmatter files.

## 2.7.5 note

- A later drift had plugin specialists back at `maxTurns: 100` while the standalone pack still had bounded budgets. This patch restores parity and adds tests so that mismatch is easier to catch.
- Conductors and phase skills now say the quiet rule out loud: specialists are leaf workers, nested delegation is not allowed, and lean fan-out wins by default.
