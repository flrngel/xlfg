# Subagent hardening notes for xlfg 2.6.0

This release responds to a real production failure mode: specialists were sometimes preparing but not finishing, and the main conductor was not relying on them strongly enough.

## What we now care about

- **Delegation signal quality**: specialist descriptions should clearly say when Claude should use them.
- **Structural capability boundaries**: agents should get explicit tool allowlists instead of broad inherited permissions.
- **Foreground completion**: phase-critical specialists should finish in the foreground so early stop, sync, and write failures are visible.
- **Artifact-backed authority**: specialists should write artifacts the conductor can verify and synthesize from.
- **Standalone parity**: the standalone `.claude/skills` pack should not silently lose the agent layer.

## Practical xlfg changes

- proactive `description` fields
- explicit `tools:` allowlists
- `background: false` on phase-critical specialists
- specialist identity + execution contract in each agent prompt
- review artifacts under `reviews/`
- stronger conductor rules in `/xlfg` and phase skills
- audit + tests for the hardening layer

## Recommended next measurement areas

- compare delegation rate before / after on real tasks
- measure artifact completeness rate by specialist and phase
- track how often the conductor has to retry a specialist or repair its lane manually
- add fixture-style evals for review quality and implementation-lane fidelity, not just intent quality
