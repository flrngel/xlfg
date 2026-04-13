# Next agent context

## Current state (2.8.2)

2.8.2 closes two residual risks from the 2.8.1 follow-up work:

- `phase-gate.mjs` (both plugin and standalone copies) now exits 0 immediately on empty stdin. Before this change, the hook would read the cwd-relative `.xlfg/phase-state.json` even when no stop-event payload was present, which caused `test_allows_on_empty_stdin` to flake inside an active /xlfg run and, more importantly, let the hook block legitimate non-xlfg invocations that happened to share the cwd.
- `xlfg verify` now annotates unittest exit 5 with a one-line hint when the planned command combines `python -m unittest` / `unittest discover` with pytest-style `-k "not ..."` negation. unittest's `-k` is substring-match only, so those commands collect zero tests and exit 5 (NO TESTS RAN); the hint makes that diagnosable instead of opaque. Pytest commands with the same filter are never annotated (pytest supports real negation).

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
