# Benchmarking xlfg

`/xlfg` needs two layers of measurement:

1. **Deterministic harness audit** — what this repo can measure itself today
2. **Live A/B evaluation** — what you should run later inside real Claude Code

The repo cannot directly inspect Claude Code internals such as exact context packing or model-side routing decisions. Because of that, xlfg now treats benchmarking as a two-part system.

## 1) Deterministic harness audit (`xlfg audit`)

`xlfg audit` measures a transparent proxy for what the harness asks of an agent.

### Workflow-load inputs

- core command prompt words
- seeded run-file count
- planning required-artifact count
- initial read counts for implement / verify / review
- default implementation agent budget
- default review budget
- model-routing diversity (for example, whether lighter agents are available)
- version-sync hygiene

### Coverage inputs

- recall support
- research lane support
- query-contract discipline
- proof discipline (`test-contract`, `test-readiness`, `proof-map`, `verify`)
- review support
- compounding support
- benchmark / audit support
- explicit ownership discipline

### Main outputs

- `workflow_load_score` — lower is better
- `sdlc_coverage_score` — higher is better
- `efficiency_index` — coverage divided by load; higher is better

This is a **surrogate metric**, not a token meter. It is useful because it is deterministic, transparent, and comparable across xlfg revisions.

## 2) Live A/B evaluation protocol

When real Claude Code access is available, compare **vanilla Claude Code** against **Claude Code + /xlfg 2.1.0** on the same task set.

### Task mix

Use at least 12 tasks across:

- 3 bugfixes
- 3 feature additions
- 2 refactors
- 2 research-heavy changes
- 2 user-flow / QA-sensitive changes

### Controls

Keep these constant:

- same repo snapshot
- same model family / plan-mode setting
- same permissions / hooks / MCP configuration
- same acceptance tests
- same evaluator

### Record per run

- solved / unsolved
- fail-to-pass coverage for changed scenarios
- pass-to-pass regression preservation
- time to first meaningful edit
- time to green verification
- number of user interventions
- number of task restarts / replans
- review blockers found after “green” verification
- research usefulness (0–3)
- final human acceptance (pass / fail)

### Success criterion

A new xlfg revision is better only if it either:

- improves solve rate at similar effort, or
- holds solve rate while reducing effort, or
- meaningfully improves proof / regression control on high-risk tasks

Do **not** accept higher workflow load unless it buys clearly better outcomes.
