# Next agent context

## Current state (2.6.0)

The main 2.6.0 change is **subagent hardening after the 2.5.x intent-contract work**.

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
