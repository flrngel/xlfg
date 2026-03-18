# NEXT_AGENT_CONTEXT

Read this before touching the repo. This document is the bundle-level handoff so the next intelligent agent can continue without extra explanation.

## 1. Mission

`xlfg` is not trying to be a generic CLI product. The real product is the **agent skill / harness** that helps Claude Code or similar coding agents build **production-grade services** with less fake-green output, less terminal thrash, and better retained operational knowledge.

The harness should make good engineering behavior easier than bad engineering behavior.

## 2. Non-negotiables from the user

- `/xlfg` must be a macro composed of explicit subcommands.
- `/xlfg` must **use recall**. A recall system that only exists in a side CLI is meaningless.
- Planning and implementation must prevent bad output; review is not the cleanup crew.
- The workflow must prefer the **root solution**, not temporal patches.
- Testing must be defined from concrete **UX / behavior flows** before coding.
- Environment / harness failures must be learned and compounded so the same failure does not keep happening.
- The harness must preserve **what the query actually asked for** and must not drop implied asks after several steps.
- The harness must reject **monkey fixes / temp fixes** that only patch the obvious symptom.
- Every delivered bundle should include a high-signal handoff document so the next agent can pick up immediately.
- Do **not** push vector-search / RAG / HyDE / reranking as a required core dependency.
- Normal evolution bumps **patch version only**.

## 3. What changed in 2.0.8

This patch strengthens xlfg at the exact weak spot the user called out: request drift and monkey fixes.

### Main changes

1. New planning agent: `xlfg-query-refiner`.
2. New required run artifact: `query-contract.md`.
3. Planning now writes `query-contract.md` before broad repo fan-out.
4. `query-contract.md` separates:
   - direct asks
   - implied asks
   - functionality + quality requirements
   - general solution constraints
   - specific solution constraints
   - developer / product intention
   - prohibited shallow fixes
   - a short carry-forward anchor
5. `flow-spec.md`, `spec.md`, `plan.md`, `test-contract.md`, `proof-map.md`, and `scorecard.md` now trace back to query / intent IDs.
6. Implementation, verification, and review must re-read the carry-forward anchor.
7. `test-contract.md` now requires counterexample / anti-monkey probes for changed primary scenarios.
8. Verification and review now treat uncovered direct asks / non-negotiable implied asks as a real failure, not a minor note.
9. This bundle now includes `docs/query-understanding-and-root-solution.md` as the design note for this patch.

## 4. Why this patch exists

The user found that xlfg:
- often omitted what the query implied
- forgot the request after several steps
- often chose a monkey fix / temp fix

The harness already had `why.md`, `diagnosis.md`, `flow-spec.md`, and `test-contract.md`, but it still lacked a single durable request contract that every later phase had to keep honoring.

So 2.0.8 adds that contract rather than adding a bigger memory system or a heavier runtime.

## 5. Research synthesis behind 2.0.8

The important takeaways were:

- **CodeScout (Mar 2026):** refine underspecified requests into actionable problem statements before execution.
- **Prompt Triangle / RE framing (Mar 2026):** separate requirements from solution guidance.
- **OpenDev / terminal-agent lessons (Mar 2026):** long trajectories suffer attention decay, so use small reminders rather than trusting the initial prompt forever.
- **Canonical path deviation (Feb 2026):** many failures are drift from the task’s successful path, not raw capability gaps.
- **Patch validation (Mar 2026):** false-correct patches happen when root cause, spec adherence, and developer intention are weak.
- **SWE-Skills-Bench (Mar 2026):** narrow, context-compatible skill changes beat bigger generic skill piles.

The patch translates those ideas into a small concrete change set instead of importing speculative mechanisms.

## 6. Design direction now

The desired shape is:

1. **Prepare fast** — check scaffold version, migrate only on drift.
2. **Recall first** — read the smallest relevant prior context before wide repo scanning.
3. **Refine the query** — make direct asks, implied asks, and quality expectations explicit.
4. **Why first** — anchor the run to the user / operator value and false-success rejection.
5. **Diagnose** — identify the real capability gap or fault chain.
6. **Contract** — define behavior, tests, and environment up front.
7. **Profile** — choose the minimum honest harness intensity.
8. **Implement with bounded loops** — task-scoped work, explicit checks, anti-shortcut discipline.
9. **Verify honestly** — layered proof with environment-state awareness and query-coverage gates.
10. **Review as confirmation** — not as rescue.
11. **Compound** — promote only small, verified lessons; keep runs local by default.
12. **Refresh the handoff** — keep a concise tracked context document for the next agent.

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
- a second heavy knowledge retrieval system

The point is to improve request fidelity and root-solution behavior with the smallest real harness change.

## 9. Current weak spots

These remain high-value follow-ups:

- repo-specific stack profiles are still thin; command detection is still heuristic in unknown repos
- reviewer specialization can improve further for framework-specific systems
- `current-state.md` needs disciplined curation so it stays short and useful
- plugin prompts still rely on the lead agent to honestly maintain `workboard.md`, `proof-map.md`, and `query-contract.md`; stronger mechanical enforcement could help later

## 10. Editing rules for the next agent

If you continue evolving this repo:

- bump **patch only**
- update version in all required files
- update `plugins/xlfg-engineering/CHANGELOG.md`
- update this `NEXT_AGENT_CONTEXT.md`
- prefer improving `/xlfg` and its subcommands over polishing the CLI
- do not add experimental retrieval as a core dependency
- keep `docs/xlfg/runs/` local by default unless there is a very strong reason not to

## 11. Suggested immediate first reads

If continuing from 2.0.8, inspect these first:

- `docs/query-understanding-and-root-solution.md`
- `plugins/xlfg-engineering/commands/xlfg.md`
- `plugins/xlfg-engineering/commands/xlfg-plan.md`
- `plugins/xlfg-engineering/commands/xlfg-implement.md`
- `plugins/xlfg-engineering/commands/xlfg-verify.md`
- `xlfg/runs.py`
- `xlfg/scaffold.py`
- `tests/test_xlfg.py`

## 12. Success criterion

The user should be able to install the plugin, run `/xlfg`, and get a workflow that:

- remembers relevant past failures and harness rules up front
- preserves what the query actually asked for
- defines why, behavior, and proof before coding
- picks an honest harness intensity instead of wasting time by default
- avoids the same bad dev-server / port / stale-build loops
- prefers root fixes over temporal patches
- rejects monkey fixes that only patch the most obvious path
- leaves behind a clear tracked handoff for the next agent

## 13. Merge-friendly knowledge reminder

The bundle still follows the simple 2.0.7 merge-friendly model:

- append-only shared knowledge files are protected with `.gitattributes` `merge=union` rules
- `current-state.md` is not meant to be rewritten on every feature branch
- feature branches/worktrees should write `docs/xlfg/runs/<RUN_ID>/current-state-candidate.md` instead and let recall read it as local branch context

This keeps retrieval simple and reduces PR conflicts without a second heavy knowledge system.
