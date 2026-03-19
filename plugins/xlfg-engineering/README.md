# xlfg-engineering (Claude Code plugin)

`/xlfg` is an **adaptive research-to-release SDLC macro** for Claude Code.

It is designed for:

- long-horizon or multi-file work
- user-flow-sensitive product changes
- bugfixes where root cause matters
- tasks that need honest proof, not just green commands
- runs that benefit from lightweight PM / Engineering / QA coordination

## Commands

| Command | Purpose |
|---|---|
| `/xlfg` | Macro that runs recall → plan → implement → verify → review → compound |
| `/xlfg:prepare` | Manual scaffold/version check; maintenance only |
| `/xlfg:init` | Manual bootstrap / repair of `docs/xlfg/` + `.xlfg/` scaffolding |
| `/xlfg:recall` | Deterministic recall over current-state, knowledge, role memory, and local runs |
| `/xlfg:plan` | Build the run card, decide whether research is needed, choose the harness profile, and define proof before code |
| `/xlfg:implement` | Implement task-by-task with minimal read amplification and adaptive subagent use |
| `/xlfg:verify` | Run proof-first verification and update the scorecard / proof map |
| `/xlfg:review` | Run only the review lenses justified by the profile and changed surface |
| `/xlfg:compound` | Convert a run into durable knowledge, role memory, and a refreshed next-agent handoff |
| `/xlfg:audit` | Measure workflow load, SDLC coverage, and benchmark readiness |

## Core philosophy in 2.1.0

- **Claude Code stays the orchestrator.** xlfg should not try to become a bureaucracy that fights the base tool.
- **Research is first-class but conditional.** `research.md` exists only when external truth matters.
- **`spec.md` is the run card.** Implement / verify / review should start there, then dive deeper only when needed.
- **Subagents are adaptive.** The default is one lead planner and one task implementer, not routine fan-out.
- **PM / Engineering / QA are all represented, but in the same lean workflow.**
- **Benchmarking matters.** xlfg now includes an audit command plus a live evaluation protocol.

## Key artifact model

Always-on run contracts:

- `query-contract.md`
- `memory-recall.md`
- `why.md`
- `harness-profile.md`
- `spec.md` (run card)
- `plan.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`
- `proof-map.md`

Optional when the run needs them:

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`
- `research.md`
- `repo-map.md`
- `risk.md`
- `scorecard.md`

## The three planning states

- **Semantic state** — request truth and user outcome (`query-contract.md`, `why.md`)
- **Structural state** — where the solution fits (`diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `research.md` when needed)
- **Execution state** — how the run ships and proves it (`spec.md`, `plan.md`, `test-contract.md`, `test-readiness.md`, `workboard.md`, `proof-map.md`, `scorecard.md`)

## Adaptive agent model

Use read-only or mapping specialists only when they clearly save time. Prefer lighter models for low-stakes exploration.

Examples:

- repo mapping / context investigation / environment triage → lighter subagents
- planning synthesis / implementation / review reduction → stronger reasoning agents

## Skills

- `xlfg-file-context`
- `xlfg-quality-gates`
- `xlfg-recall`

## Installation

Point Claude Code at `plugins/xlfg-engineering` as a plugin directory.

## Versioning

This is version `2.1.0`.
