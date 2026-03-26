# xlfg current state

Read this file first when entering a repo that uses xlfg. It is the shortest tracked handoff for the next agent.

## Service / product context
- What is this repo / service trying to do right now?

## Current high-signal truths
- The most important facts that should shape new work immediately
- Any request-shaping rule that repeatedly prevents dropped implied asks or monkey fixes

## Active UX / behavior contracts
- Flows or invariants that repeatedly matter

## Current harness / verification rules
- Ports, healthchecks, non-interactive rules, dev-server reuse rules

## Repeated failures to avoid
- The recurring failure signatures and the proven first response

## Open risks / debts
- Things the next agent should keep in mind before touching risky areas

## Best starting recall queries
- One or two exact lexical or typed queries that load the right memory fast

Keep this document short, current, and biased toward actionable truths. Historical detail belongs in the ledger, shared knowledge files, or local runs.

Merge rule: prefer updating this file only on the default branch (`main`, `master`, or `trunk`) or when the user explicitly asks to promote a repo-wide handoff. Feature branches should usually write a local `current-state-candidate.md` inside the run folder instead.
