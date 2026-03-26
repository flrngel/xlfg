# NEXT_AGENT_CONTEXT

## Current state (2.5.0)

The main 2.5.0 fix is **making intent resolution first-class without reintroducing duplicated planning files**.

2.4.0 restored the public-entrypoint + hidden-phase-skills architecture, but it was still weak on messy prompts: bundled asks, missing context, and hidden acceptance criteria could slip through before planning hardened around the wrong interpretation.

2.5.0 keeps the good 2.4.0 shape while fixing that weakness:

- the plugin still exposes one public command at `/xlfg-engineering:xlfg`
- the standalone pack still exposes one public short-name skill at `/xlfg`
- both entrypoints now batch hidden phase skills in this order:
  1. recall
  2. intent
  3. context
  4. plan
  5. implement
  6. verify
  7. review
  8. compound
- `spec.md` is now the only active home for the intent contract and objective groups
- runtime prompts no longer depend on a separate intent file
- the hidden intent phase can mark `proceed`, `proceed-with-assumptions`, or `needs-user-answer`
- messy requests are split into stable objective groups (`O1`, `O2`, ...) before broad repo fan-out
- the repo now ships `xlfg eval-intent` plus bundled fixtures for artifact-graded intent evaluation

## What xlfg should be

A serious but lean SDLC exoskeleton for Claude Code:

- one public invocation
- hidden phase skills loaded just in time
- one run card (`spec.md`)
- deterministic recall
- mandatory intent resolution before broad fan-out
- explicit proof
- optional research
- proportional review
- durable compounding only when verified

## Product truths to preserve

- `/xlfg` should execute the entire workflow itself. Do not make the user run phase commands or hidden skills.
- The right structure is **public entrypoint + hidden phase skills**, not a public command chain and not a single giant prompt.
- `spec.md` is the single source of truth; do not reintroduce a separate active intent file.
- The helper CLI is optional but valuable. When available, the main entrypoint should prefer it for scaffold sync, run creation, recall, verification, audit, and intent grading.
- The intent gate belongs in the main run flow before broad repo/context fan-out.
- For bundled asks, objective groups must remain legible all the way through tasks and proof.
- The plugin form is for team reuse and therefore namespaced.
- The standalone `.claude/skills/` pack is the best short-name UX and must include the hidden phase skills too.

## Main files to understand first

1. `plugins/xlfg-engineering/commands/xlfg.md`
2. `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md`
3. `plugins/xlfg-engineering/agents/planning/xlfg-query-refiner.md`
4. `standalone/.claude/skills/xlfg/SKILL.md`
5. `xlfg/runs.py`
6. `xlfg/intent_eval.py`
7. `xlfg/audit.py`
8. `tests/test_xlfg.py`

## Regression triggers

Treat any of the following as regressions:

- `/xlfg` asking the user to run or sequence internal phase commands or hidden skills
- removing the hidden phase skills and collapsing everything back into one monolithic prompt
- broad repo/context fan-out starting before the intent contract exists
- reintroducing a separate active intent file that competes with `spec.md`
- losing objective-group mapping between `spec.md`, `test-contract.md`, and `workboard.md`
- commands or skills that reference repo-relative plugin paths as if they exist inside the target repo
- reintroducing the stale `Task` tool naming in entrypoints
- plugin support skills cluttering the slash menu instead of staying hidden helpers
- claiming green without scenario-targeted proof
