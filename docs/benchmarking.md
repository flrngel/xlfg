# Benchmarking xlfg

`/xlfg` now uses two layers of measurement:

1. **Deterministic harness audit** — what this repo can measure itself today
2. **Live Claude Code A/B evaluation** — what you should run when Claude Code is available directly

The repo cannot inspect Claude Code internals such as exact context packing, permission-cache reuse, or model-side routing choices. Because of that, `xlfg audit` is intentionally a transparent surrogate metric rather than a fake token meter.

## 1) Deterministic harness audit (`xlfg audit`)

`xlfg audit` measures the shape of the harness that Claude has to carry.

### Workflow-load inputs

- primary workflow words (primary entrypoint weight plus retained utility commands)
- seeded core-file count
- planning required-artifact count
- initial read counts for implement / verify / review
- default implementation and review budgets
- model-routing diversity (for example, whether lighter agents are available)
- Claude Code compatibility features (`skills`, `allowed-tools`, `hooks`, `effort`, standalone short-name pack)
- version-sync hygiene

### Main outputs

- `workflow_load_score` — lower is better
- `sdlc_coverage_score` — higher is better
- `claude_code_compatibility_score` — higher is better
- `efficiency_index` — coverage divided by load; higher is better

This is useful because it is deterministic, transparent, and comparable across xlfg revisions.

## 2) Live A/B evaluation protocol

When real Claude Code access is available, compare **vanilla Claude Code** against **Claude Code + xlfg 2.6.0** on the same task set.

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
- same model family and effort setting
- same permissions / hooks / MCP configuration
- same acceptance checks
- same evaluator

### Record per run

- solved / unsolved
- F2P coverage for changed scenarios
- P2P regression preservation
- time to first meaningful edit
- time to green verification
- number of user interventions
- number of restarts / replans
- review blockers found after green verification
- research usefulness (0–3)
- final human acceptance (pass / fail)

### Success criterion

A new xlfg revision is better only if it either:

- improves solve rate at similar effort, or
- holds solve rate while reducing effort, or
- materially improves proof / regression control on high-risk tasks

Do **not** accept higher workflow load unless it buys clearly better outcomes.


## 3) Intent-artifact evaluation (`xlfg eval-intent`)

`xlfg eval-intent` grades the artifacts from a real run against a fixture representing a messy or underspecified prompt.

### What it scores

- `work_kind_match`
- `direct_ask_recall`
- `implied_ask_recall`
- `acceptance_recall`
- `objective_split_recall`
- `false_assumption_rate`
- `blocking_question_budget_ok`
- `objective_scenario_coverage`
- `objective_task_coverage`
- `overall`

### Single-case usage

```bash
xlfg eval-intent   --fixture evals/intent/messy-bugfix-bundle.json   --run <RUN_ID>
```

### Suite usage

Bundled reference artifacts are included, so this works out of the box:

```bash
xlfg eval-intent   --suite-dir evals/intent
```

To score your own captured runs instead, pass an explicit artifacts root:

```bash
xlfg eval-intent   --suite-dir evals/intent   --artifacts-root path/to/captured-intent-artifacts
```

The suite mode expects one folder per fixture ID, each containing:

- `spec.md`
- `test-contract.md`
- `workboard.md`

This keeps the metric tied to the real run artifacts instead of asking humans to score the run from memory.
