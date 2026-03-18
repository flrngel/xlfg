# NEXT_AGENT_CONTEXT

Read this before touching the repo. This is the bundle-level handoff so the next intelligent agent can continue without extra explanation.

## 1. Mission

`xlfg` is not trying to be a generic CLI product. The real product is the **agent skill / harness** that helps Claude Code or similar coding agents build **production-grade services** with less fake-green output, less terminal thrash, better retained operational knowledge, and less long-horizon request drift.

The harness should make good engineering behavior easier than bad engineering behavior.

## 2. Non-negotiables from the user

- `/xlfg` must be a macro composed of explicit subcommands.
- `/xlfg` must **use recall**. A recall system that only exists in a side CLI is meaningless.
- Planning and implementation must prevent bad output; review is not the cleanup crew.
- The workflow must prefer the **root solution**, not temporal patches.
- Testing must be defined from concrete **UX / behavior flows** before coding.
- Test scenarios must be **clear, concise, and practical**.
- The run must know **what it will prove before implementation starts**.
- Environment / harness failures must be learned and compounded so the same failure does not keep happening.
- The harness must preserve **what the query actually asked for** and must not drop implied asks after several steps.
- The harness must reject **monkey fixes / temp fixes** that only patch the obvious symptom.
- The harness should respect subagent results and only override them with explicit evidence.
- The harness should not overwork or over-fan-out by default.
- Every delivered bundle should include a high-signal handoff document so the next agent can pick up immediately.
- Do **not** push vector-search / RAG / HyDE / reranking as a required core dependency.
- Normal evolution bumps **patch version only**.

## 3. What changed in 2.0.9

This patch fixes the next major weakness the user found in real usage: xlfg sometimes did not test the changed work properly, sometimes skipped meaningful tests, and sometimes added harness overhead without beating vanilla Claude Code.

### Main changes

1. Added a new planning-stage agent: `xlfg-test-readiness-checker`.
2. Added a new required run artifact: `test-readiness.md`.
3. `test-contract.md` is now explicitly a **concise practical scenario contract**, not a loose future wish list.
4. Planning now requires each changed primary scenario to have:
   - objective / query traceability
   - practical steps
   - a practical `fast_check`
   - a ship proof (`fast`, `smoke`, `e2e`, or an honestly justified manual proof)
   - an anti-monkey probe
5. `/xlfg:plan` now hard-gates implementation on `test-readiness.md = READY`.
6. `/xlfg:implement` now refuses to proceed when readiness is missing or `REVISE`.
7. `/xlfg:verify` now compiles scenario-targeted checks from `test-contract.md` **before** falling back to generic repo commands.
8. Verification now stays RED when:
   - no scenario-targeted proof ran
   - changed primary scenarios lack passing fast proof
   - full mode lacks passing ship proof for changed primary scenarios
   - `test-readiness.md` is missing or `REVISE`
9. Key planning/checker/review agents now use Claude Code frontmatter controls (`effort`, `maxTurns`, `disallowedTools`) to reduce overwork and keep non-implementation agents from editing code casually.
10. New design note added: `docs/testing-before-coding-and-practical-proof.md`.

## 4. Why this patch exists

The user’s real-world report was:

- xlfg often did **not** test properly
- sometimes it didn’t really test the changed behavior at all
- the test scenarios were not practical enough to drive implementation
- the harness overhead made it worse than vanilla Claude Code in some sessions

The root diagnosis is:

- xlfg had improved request understanding and root-cause discipline in 2.0.8
- but it still did not enforce a strong enough **pre-implementation proof contract**
- so later verification could still drift into generic checks and fake greens

2.0.9 fixes that with the smallest real harness change:

> no coding until the scenario contract is written and judged READY.

## 5. Research synthesis behind 2.0.9

The patch was shaped by four current themes:

1. **Problem statement quality matters** — recent SWE-agent work shows better problem statements cut wasted exploration and repeated wrong fixes.
2. **Requirements must stay distinct from solution guesses** — recent requirement/prompt framing work reinforces xlfg’s query-contract direction.
3. **Basic validation is too weak** — recent patch-validation work shows many seemingly-correct patches fail stronger tests tied to root cause and developer intent.
4. **Long-horizon agents need explicit state and minimal sufficient context** — recent harness/terminal-agent work favors small explicit artifacts over giant context blobs.

The most important implementation consequence was:

- add a hard readiness gate
- keep the scenario contract concise
- compile verification from that contract first
- bound subagent behavior more explicitly

## 6. Design direction now

The desired shape is:

1. **Prepare fast** — check scaffold version, migrate only on drift.
2. **Recall first** — read the smallest relevant prior context before wide repo scanning.
3. **Refine the query** — make direct asks, implied asks, and quality expectations explicit.
4. **Why first** — anchor the run to the user / operator value and false-success rejection.
5. **Diagnose** — identify the real capability gap or fault chain.
6. **Contract** — define behavior, tests, and environment up front.
7. **Readiness gate** — refuse coding until the scenario contract is practical and READY.
8. **Profile** — choose the minimum honest harness intensity.
9. **Implement with bounded loops** — task-scoped work, explicit checks, anti-shortcut discipline.
10. **Verify honestly** — scenario-targeted proof first, then broader checks, with environment-state awareness and query-coverage gates.
11. **Review as confirmation** — not as rescue.
12. **Compound** — promote only small, verified lessons; keep runs local by default.
13. **Refresh the handoff** — keep a concise tracked context document for the next agent.

## 7. Memory model

There are still four layers of memory:

1. **current-state.md** — the one tracked handoff doc a new agent should read first
2. **shared knowledge** — tracked repo-wide durable lessons
3. **role memory** — compact specialist heuristics for recurring failure classes
4. **local runs** — episodic evidence, usually gitignored

The bundle-level analogue of `current-state.md` is this file: `NEXT_AGENT_CONTEXT.md`. Keep it updated whenever the bundle meaningfully changes.

## 8. What this patch intentionally does not do

It does **not** add:
- vector search
- embedding stores
- HyDE / hypothetical query expansion
- mandatory reranking
- a giant new runtime service
- forced e2e on every task
- a huge testing ontology or experimental orchestration layer

The point is to improve practical proof and root-solution behavior with the smallest real harness change.

## 9. Current weak spots after 2.0.9

These remain high-value follow-ups:

- repo-specific stack profiles are still thin; command detection is still heuristic in unknown repos
- `test-readiness.md` is only as good as the planner + checker prompts and may still need stack-specific tuning
- reviewer specialization can improve further for framework-specific systems
- `current-state.md` needs disciplined curation so it stays short and useful
- the plugin still relies on the lead agent to honestly maintain `workboard.md`, `proof-map.md`, and scorecards; stronger mechanical enforcement could help later

## 10. Editing rules for the next agent

If you continue evolving this repo:

- bump **patch only**
- update version in all required files
- update `plugins/xlfg-engineering/CHANGELOG.md`
- update this `NEXT_AGENT_CONTEXT.md`
- prefer improving `/xlfg` and its subcommands over polishing the CLI
- do not add experimental retrieval as a core dependency
- keep `docs/xlfg/runs/` local by default unless there is a very strong reason not to
- preserve the rule that tests are defined and judged READY before implementation

## 11. Suggested immediate first reads

If continuing from 2.0.9, inspect these first:

- `docs/testing-before-coding-and-practical-proof.md`
- `plugins/xlfg-engineering/commands/xlfg.md`
- `plugins/xlfg-engineering/commands/xlfg-plan.md`
- `plugins/xlfg-engineering/commands/xlfg-implement.md`
- `plugins/xlfg-engineering/commands/xlfg-verify.md`
- `plugins/xlfg-engineering/agents/planning/xlfg-test-strategist.md`
- `plugins/xlfg-engineering/agents/planning/xlfg-test-readiness-checker.md`
- `xlfg/runs.py`
- `xlfg/contracts.py`
- `xlfg/verify.py`
- `tests/test_xlfg.py`

## 12. Success criterion

The user should be able to install the plugin, run `/xlfg`, and get a workflow that:

- remembers relevant past failures and harness rules up front
- preserves what the query actually asked for
- defines why, behavior, and proof before coding
- chooses concise practical test scenarios before implementation
- picks an honest harness intensity instead of wasting time by default
- avoids the same bad dev-server / port / stale-build loops
- prefers root fixes over temporal patches
- rejects monkey fixes that only patch the most obvious path
- actually proves the changed work in verification instead of only running generic repo checks
- leaves behind a clear tracked handoff for the next agent

## 13. Merge-friendly knowledge reminder

The bundle still follows the simple 2.0.7 merge-friendly model:

- append-only shared knowledge files are protected with `.gitattributes` `merge=union` rules
- `current-state.md` is not meant to be rewritten on every feature branch
- feature branches/worktrees should write `docs/xlfg/runs/<RUN_ID>/current-state-candidate.md` instead and let recall read it as local branch context

This keeps retrieval simple and reduces PR conflicts without a second heavy knowledge system.
