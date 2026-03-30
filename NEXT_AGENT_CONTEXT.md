# Next agent context

## Current state (2.7.1)

The main 2.7.1 change is **subagent hardening after the 2.5.x intent-contract work**.

What changed:
- specialist agents now have explicit tool allowlists instead of mostly inheriting tools
- descriptions now include **use proactively** so Claude is more likely to delegate to them
- phase-critical agents now set `background: false`
- each agent now has a stronger specialist identity plus execution contract
- review specialists now write lane artifacts under `docs/xlfg/runs/<run>/reviews/`
- the standalone pack now mirrors plugin agents under `.claude/agents/`
- `/xlfg` and the phase skills now tell the conductor to treat specialists as lane owners and to retry / classify prep-only early exits as incomplete work

Why this matters:
- production testing found subagents were often stopping after preparation without doing the actual lane work
- the main conductor also was not relying on them strongly enough, especially in review
- recent Claude Code docs and issues suggest that proactive descriptions, explicit tool scoping, and foreground execution are all important when you want reliable specialist delegation

If you continue from here:
- preserve the **one public conductor + hidden phase skills + separated specialists** architecture
- do not flatten back into one monolithic prompt
- do not reintroduce duplicated intent docs
- if you add more hardening, prefer evals and artifact checks over more prose


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.

## 2.7.3 note

- Production run found agents exhausting maxTurns: 8 on speculative reads, never writing artifacts. Root cause: bloated "Read first" lists (14 files), no turn budget guidance, and stopHookActive escape hatch letting agents bypass the guard.
- Fix: maxTurns raised to 12 for review + heavy-analysis agents. "Turn budget rule" added to all 26 specialists. Review agents get lean "Context sources" (3+3 files). stopHookActive escape removed. CONTEXT_DIGEST added to review-phase dispatch.
- If you continue from here: preserve the turn budget rule in all new agents, keep maxTurns proportional to workload, and always embed context digests in dispatch packets for read-heavy specialists.
