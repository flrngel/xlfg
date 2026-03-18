# Testing before coding and practical proof (2.0.9)

This document is the context handoff for why xlfg 2.0.9 changed, what external systems/papers informed it, and what the next intelligent agent should preserve.

## 1. Why this patch exists

Observed user pain:

- xlfg often planned vaguely and then coded before the proof contract was real.
- `test-contract.md` could exist but still be too vague to drive implementation honestly.
- verification sometimes ran only generic repo checks or skipped meaningful scenario proof.
- in practice that made xlfg worse than vanilla Claude Code on some repos because it added overhead without increasing trust.
- “green” often meant “commands passed” rather than “the changed task actually works.”

That breaks the product goal.

The goal is not to generate more process. The goal is:

1. understand the request deeply
2. preserve that understanding across long trajectories
3. decide the root solution before coding
4. define clear, concise, practical test scenarios before coding
5. implement with bounded task loops
6. prove the changed work actually works
7. compound the reusable lesson

## 2. What recent external work changed the design

### A. Official Claude Code updates

Relevant direction from recent Claude Code updates:

- plugin-shipped agents can now use more frontmatter control, including `effort`, `maxTurns`, and `disallowedTools`
- earlier updates added stronger subagent lifecycle/status events and agent memory support
- worktree loading reliability was improved, which matters because xlfg is frequently used in worktrees and long sessions

What xlfg took from that:

- key planning/checker/review agents now have explicit `effort` and `maxTurns`
- non-implementation agents now disallow code-editing tools where appropriate
- the harness tries harder to bound subagent behavior instead of letting every agent over-explore

### B. Open SWE pattern

Open SWE’s useful lesson is not “become a giant runtime.” It is:

- use isolated execution boundaries
- keep a curated toolset
- keep repo-specific context in files like `AGENTS.md`
- use deterministic middleware / state transitions rather than vague hidden orchestration
- keep PR-opening / validation / queue-checking logic explicit

What xlfg took from that:

- predeclared contracts before coding
- scenario-first proof before broad verification
- explicit stage and proof state in `workboard.md` and `proof-map.md`
- do not let later phases improvise the meaning of the task

What xlfg intentionally did **not** take:

- a mandatory service runtime / gateway architecture
- a larger always-on orchestration stack

### C. Claude HUD pattern

Claude HUD’s useful lesson is visibility:

- users benefit from seeing active tools, running agents, todo progress, and context pressure in real time
- status should be cheap and obvious

What xlfg took from that indirectly:

- `workboard.md` is now even more important as the explicit run-truth ledger
- `proof-map.md` and `scorecard.md` are the visible proof state
- the harness is biased toward a few explicit files instead of hidden state

### D. Recent 2026 papers (theory direction)

#### CodeScout

Main lesson:

- input / problem statement quality changes downstream SWE agent success materially
- a refined problem statement can reduce wasteful exploration and repeated failed fixes

What xlfg changed because of that:

- query refinement remains mandatory before broad repo fan-out
- planning now adds stronger objective grouping and carry-forward anchors

#### Prompt Triangle

Main lesson:

- keep requirements separate from solution constraints
- make functionality + quality explicit, then track solution constraints explicitly

What xlfg changed because of that:

- `query-contract.md` continues to separate asks/requirements/constraints
- scenario contracts in `test-contract.md` now trace back to objective/query IDs more explicitly

#### Patch Validation

Main lesson:

- many patches that basic validation accepts fail stronger validation that captures developer intent and root cause

What xlfg changed because of that:

- verification is now RED if changed primary scenarios lack practical proof
- ship success requires scenario-targeted proof, not only generic repo checks

#### TDAD / behavioral-spec work

Main lesson:

- behavior specs should be executable and should evolve against hidden/stronger checks, not stay vague prose

What xlfg changed because of that:

- `flow-spec.md` and `test-contract.md` are now treated as executable planning artifacts
- `test-readiness.md` exists to reject weak scenario contracts before coding starts

#### OpenDev / long-horizon terminal-agent work

Main lesson:

- long sessions drift unless the harness explicitly preserves semantic continuity and reminds the system what matters
- minimal sufficient context is better than giant context blobs

What xlfg changed because of that:

- keep the carry-forward anchor small and mandatory
- keep scenario contracts concise (1–5 required cards)
- keep verification targeted before broad

#### AGENTS.md / context-file evaluations

Main lesson:

- more context is not automatically better; large generic context files can reduce success and increase cost

What xlfg changed because of that:

- avoid dumping giant test catalogs into the plan
- prefer a small set of practical scenario cards and one explicit readiness gate

## 3. Core design decision in 2.0.9

The biggest change is simple:

> implementation may not start until the test contract is both written and judged READY.

That means:

- `test-contract.md` must name the changed scenarios before coding
- each changed primary scenario must have a practical `fast_check`
- each changed primary scenario must have a ship proof (`fast`, `smoke`, `e2e`, or an honestly justified manual proof)
- each changed primary scenario must have an anti-monkey probe
- `test-readiness.md` must explicitly say `READY`

This is intentionally **simple**. It is a harness rule, not an experimental retrieval system.

## 4. New file responsibilities

### `test-contract.md`

This is now the **practical proof contract**.

It must stay short.

Expected style:

- 1–5 required scenario cards total
- each scenario card has:
  - objective
  - requirement kind (`F2P` or `P2P`)
  - query IDs
  - practical steps
  - `fast_check`
  - `ship_phase`
  - `ship_check`
  - `regression_check`
  - `manual_smoke`
  - `anti_monkey_probe`

### `test-readiness.md`

This is the new gate.

Its only job is to answer:

- are these scenario contracts concrete enough to code against?
- are they practical enough for iteration?
- are they honest enough to stop monkey fixes?
- are they small enough to avoid overwork?

Verdict options:

- `READY`
- `REVISE`

If `REVISE`, implementation must stop and planning must improve the contract.

## 5. Verification policy after 2.0.9

Verification now compiles commands from `test-contract.md` first.

Only after that does it add supplemental repo-level checks.

That order matters.

Old weak pattern:

1. run generic lint/test/build
2. if green, feel done

New pattern:

1. run practical scenario proof from the declared contract
2. then run the repo checks that matter for confidence/regression
3. keep the run RED if scenario proof is missing or weak

So verification now rejects these bad states:

- no scenario-targeted checks executed
- F2P scenario without a passing `fast_check`
- full mode without passing ship proof for changed primary scenarios
- readiness verdict missing or `REVISE`

## 6. New subagent introduced

### `xlfg-test-readiness-checker`

Why it exists:

- `xlfg-test-strategist` writes the contract
- a second planning-stage specialist decides whether that contract is actually good enough to code against

That separation matters because the harness should respect subagents, not let one agent silently over-certify its own work.

## 7. What was intentionally *not* added

Not added on purpose:

- vector search / RAG as a dependency
- giant runtime orchestration
- mandatory browser overlays or dashboards
- a huge graph of testing memory
- forced e2e for every task

Reason:

The user asked for a production harness skill, not experimental retrieval or a research demo.

## 8. Current expected workflow

`/xlfg` should now mean:

1. prepare
2. recall
3. plan
   - query contract
   - why
   - diagnosis
   - solution decision
   - flow spec
   - test contract
   - test readiness
   - harness profile
   - env plan
   - reduced plan/workboard/proof map/scorecard
4. implement
5. verify
6. review
7. compound

The crucial rule is between 3 and 4:

> do not code until the test contract is READY.

## 9. First things to inspect if this still fails in practice

If xlfg still underperforms in real repos, inspect these in order:

1. did `query-contract.md` miss or under-specify the actual task?
2. did `flow-spec.md` miss the practical interaction variants?
3. did `test-contract.md` define only generic repo checks instead of scenario proof?
4. did `test-readiness.md` incorrectly allow a vague contract to pass?
5. did implementation change the shape of the solution without returning to planning?
6. did verification fall back to generic commands because command discovery was wrong?
7. did the repo need stack-specific commands in `docs/xlfg/knowledge/commands.json`?

## 10. Files most relevant to this patch

- `plugins/xlfg-engineering/commands/xlfg.md`
- `plugins/xlfg-engineering/commands/xlfg-plan.md`
- `plugins/xlfg-engineering/commands/xlfg-implement.md`
- `plugins/xlfg-engineering/commands/xlfg-verify.md`
- `plugins/xlfg-engineering/agents/planning/xlfg-test-strategist.md`
- `plugins/xlfg-engineering/agents/planning/xlfg-test-readiness-checker.md`
- `plugins/xlfg-engineering/agents/implementation/xlfg-test-implementer.md`
- `xlfg/runs.py`
- `xlfg/contracts.py`
- `xlfg/verify.py`
- `tests/test_xlfg.py`

## 11. Source URLs used for this patch

Official / code references:
- https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- https://docs.anthropic.com/en/docs/claude-code/sub-agents
- https://github.com/langchain-ai/open-swe
- https://github.com/jarrodwatts/claude-hud

Recent paper references used in reasoning:
- https://arxiv.org/abs/2603.05744
- https://arxiv.org/abs/2603.11456
- https://arxiv.org/abs/2603.06289
- https://arxiv.org/abs/2603.15401
- https://arxiv.org/abs/2602.14337
- https://arxiv.org/abs/2603.14631

## 12. Preserve these invariants in future patches

- patch version only
- `/xlfg` stays a macro of explicit subcommands
- the plugin workflow is the product; the CLI is support only
- deterministic file-based memory stays the source of truth
- tests-before-code stays mandatory
- verification must prove changed behavior, not merely run commands
