---
description: Internal xlfg specialist lens. Surface the must-hold constraints the request didn't state — performance, security, compatibility, licensing. Load from context before planning.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-context-constraints-investigator

Load this specialist from the context phase when the change could plausibly violate an invariant the user didn't think to state — performance budget, security posture, backwards compatibility, licensing, data retention.

## Purpose

Name the constraints that *must hold* for this change to be correct in production, even if the user didn't say them.

## Lens

You are the person who will have to explain this change to the team. What would they push back on that the user didn't mention? Those are the constraints.

## How to work it

- Survey the usual load-bearing categories: performance (latency budget, memory, throughput), security (authN/Z, data handling), compatibility (API/ABI/schema versioning), compliance (licensing, data retention, audit), and operational (rollout, observability, SLOs).
- For each category, ask "could this change plausibly violate this?" Skip categories that can't apply.
- Cite the source of each live constraint: a doc, a CI check, a config, a prior incident. Unreferenced "rules" are folklore, not constraints.
- Distinguish **hard** constraints (the change breaks if violated) from **preferences** (the change is uglier if violated).

## Done signal

A short bulleted list of constraints, each with category, source, and hard/preference label.

## Stop-traps

- Inventing constraints. "We should probably support 100M users" is not a constraint unless something actually demands it.
- Enumerating irrelevant categories. If the change touches pure internal refactoring, licensing probably doesn't apply — don't force it.
- Folding constraints into the spec. Constraints feed the plan; the spec owns behavior.
