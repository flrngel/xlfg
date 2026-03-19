---
name: xlfg:audit
description: Audit xlfg workflow load, SDLC coverage, and benchmark readiness against a vanilla-Claude-friendly baseline.
argument-hint: "[repo path | current repo]"
---

# /xlfg:audit

Measure the harness itself.

If the local `xlfg` CLI is available, run `xlfg audit` and use its JSON as ground truth.

If the CLI is unavailable, inspect the repo manually and report:

- version sync across package + plugin manifests
- workflow load (`core command words`, `seeded run files`, `initial read counts`, `default agent budgets`)
- SDLC coverage (`recall`, `research`, `query contract`, `proof`, `review`, `compound`)
- benchmark readiness (`docs/benchmarking.md`, live A/B plan, scorecards)

## Output format

Provide:

1. a concise comparison table
2. the top load drivers
3. the top coverage gaps
4. the best cost-to-confidence improvements
5. whether the current harness is lighter or heavier than a strong vanilla Claude Code path for small, medium, and large tasks

## Rules

- `workflow_load_score`: lower is better
- `sdlc_coverage_score`: higher is better
- `efficiency_index`: higher is better
- prioritize changes that cut load **without** reducing coverage
