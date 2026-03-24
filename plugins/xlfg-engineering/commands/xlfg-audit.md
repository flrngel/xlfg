---
description: Audit xlfg workflow load, SDLC coverage, Claude Code compatibility, and benchmark readiness.
argument-hint: "[repo path | current repo]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash
effort: medium
---

# xlfg audit

Measure the harness itself.

If the local `xlfg` CLI is available, run `xlfg audit` and use its JSON as ground truth.

If the CLI is unavailable, inspect the repo manually and report:

- version sync across package + plugin manifests
- workflow load (`primary workflow words`, `seeded core files`, `initial read counts`, `default agent budgets`)
- SDLC coverage (`recall`, `research`, `run card`, `proof`, `review`, `compound`)
- Claude Code compatibility (`skills-first`, `standalone /xlfg pack`, `allowed-tools`, `hooks`, `effort`, plugin namespace clarity`)
- benchmark readiness (`docs/benchmarking.md`, live A/B plan)

## Output format

Provide:

1. a concise comparison table
2. the top load drivers
3. the top compatibility gaps
4. the best cost-to-confidence improvements
5. whether the current harness is lighter or heavier than a strong vanilla Claude Code path for small, medium, and large tasks

## Rules

- `workflow_load_score`: lower is better
- `sdlc_coverage_score`: higher is better
- `claude_code_compatibility_score`: higher is better
- `efficiency_index`: higher is better
