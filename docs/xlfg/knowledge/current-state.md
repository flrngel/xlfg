# xlfg current state

Read this file first when entering a repo that uses xlfg. It is the shortest tracked handoff for the next agent.

## Service / product context
- xlfg is an autonomous SDLC harness for Claude Code and Codex (v3.2.0)
- `/xlfg` batches 8 hidden phase skills: recall → intent → context → plan → implement → verify → review → compound
- `$xlfg` is the Codex skill surface for the same run shape; `$xlfg-debug` is the Codex diagnosis-only sibling

## Current high-signal truths
- The conductor has a Stop hook (`phase-gate.mjs`) that blocks premature pipeline termination by reading `.xlfg/phase-state.json`
- Verify-fix and review-fix loopback cycles are capped at 2 iterations
- Specialists are leaf workers with a generous safety ceiling (maxTurns ≤ 150), foregrounded, and bounded by artifact completion barriers plus the prompt-side write-first / leaf-worker rules. The ceiling is a budget cap, not a target — most lanes finish in far fewer turns; needing many turns is a signal the lane was scoped wrong, not a signal to raise the cap further
- The repo ships exactly one install surface: the Claude Code plugin in `plugins/xlfg-engineering/` (also wired for Codex via `.codex-plugin/` and Cursor via `.cursor-plugin/`). The `standalone/` pack was removed in v4.0.0 after repeated drift; "plugin loader unavailable" is no longer a supported install story now that the Claude Code marketplace is GA
- The Codex surface is intentionally separate under `plugins/xlfg-engineering/codex/` because Codex public skills require `name` and `description` frontmatter

## Active UX / behavior contracts
- The phase-state file uses the fixed path `.xlfg/phase-state.json` — the Stop hook reads it from `cwd`
- Safety valve: 3 consecutive blocks → allow stopping (prevents infinite loop)
- `max_tokens` stop reason → always allow (model physically can't continue)

## Current harness / verification rules
- Tests: `python3 -m unittest discover tests/` — no dev server needed
- Tests cover entrypoint structure, version sync, Codex plugin shape, and specialist hardening (CLI-module tests removed in v3.0.0)

## Repeated failures to avoid
- Do not register the same hook in both command frontmatter AND hooks.json — it double-fires (found in review, run 20260403)
- Plugin hooks live in `hooks.json` only; referenced via `${CLAUDE_PLUGIN_ROOT}/scripts/*.mjs`
- Codex v1 support uses prompt-level barriers and file-backed state rather than adding hard hook parity
- A version bump touches more than just the three `plugin.json` manifests: any hardcoded version string in `tests/test_codex_plugin.py` must move in lockstep (the v3.3.1 entry explicitly called this out; the delete-standalone-bump run still missed it at intent time). Grep `tests/` for the outgoing version string as part of every bump.
- Intent-phase scoping must grep the full repo (not just the curated test file list) for the term being removed. The delete-standalone run missed `docs/subagent-hardening-2026.md` and `docs/claude-code-2026-compatibility.md` because they were not in the initial test-file enumeration; verify-phase caught them via a broader rg sweep.

## Open risks / debts
- The loopback cap is prompt-instructed, not code-enforced — the Stop hook safety valve is the hard backstop

## Best starting recall queries
- `Grep "phase-gate" docs/xlfg/knowledge/` — conductor stop hook pattern
- `Grep "version sync" docs/xlfg/knowledge/` — full scope of version-bump maintenance (manifests + hardcoded test assertions)
