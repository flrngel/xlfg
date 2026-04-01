# Next agent context

## Current state (2.7.5)

The main 2.7.5 change is **making the 2.7.x subagent hardening internally consistent again**.

What changed:
- plugin agent `maxTurns` budgets are back in sync with the standalone pack instead of drifting to `100`
- `/xlfg` and all delegating phase skills now say specialists are **leaf workers**; only the conductor may delegate
- conductor guidance now explicitly ties waiting to preseeded artifacts plus `RETURN_CONTRACT`
- review fan-out is leaner by default, and context / planning guidance now prefers one active artifact-producing lane at a time
- audit + tests now enforce short-lived budgets, leaf-worker tools, atomic packet headers on delegating entrypoints, and lean review fan-out

Why this matters:
- production drift left plugin specialists with effectively unbounded turn budgets, which made a stuck lane look like a hang
- nested delegation remains a bad fit for current Claude Code specialist orchestration, so xlfg now says that explicitly instead of relying only on tool scoping
- smaller default fan-out keeps context pressure and coordination failures lower on real runs

If you continue from here:
- preserve the **one public conductor + hidden phase skills + separated specialists** architecture
- do not flatten back into one monolithic prompt
- do not reintroduce duplicated intent docs
- if you add more hardening, prefer evals and artifact checks over more prose
- keep plugin and standalone agent packs synchronized on `maxTurns` and delegation shape


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.

## 2.7.3 note

- Production run found agents exhausting maxTurns: 8 on speculative reads, never writing artifacts. Root cause: bloated "Read first" lists (14 files), no turn budget guidance, and stopHookActive escape hatch letting agents bypass the guard.
- Fix: maxTurns raised to 12 for review + heavy-analysis agents. "Turn budget rule" added to all 26 specialists. Review agents get lean "Context sources" (3+3 files). stopHookActive escape removed. CONTEXT_DIGEST added to review-phase dispatch.
- If you continue from here: preserve the turn budget rule in all new agents, keep maxTurns proportional to workload, and always embed context digests in dispatch packets for read-heavy specialists.

## 2.7.5 note

- A later drift had plugin specialists back at `maxTurns: 100` while the standalone pack still had bounded budgets. This patch restores parity and adds tests so that mismatch is easier to catch.
- Conductors and phase skills now say the quiet rule out loud: specialists are leaf workers, nested delegation is not allowed, and lean fan-out wins by default.
