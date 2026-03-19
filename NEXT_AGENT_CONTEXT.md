# NEXT_AGENT_CONTEXT

This is the required handoff document for the next intelligent agent continuing work on this repo.

## 1. Current bundle version

- **xlfg version:** `2.1.0`
- this is a **minor** redesign because the workflow philosophy changed materially

## 2. What changed in 2.1.0

This revision is focused on one harder problem:

> `/xlfg` could still be worse than strong vanilla Claude Code because it was too easy for the harness to become heavier than the value it added.

### Main changes

- `/xlfg` is now explicitly framed as a **thin SDLC macro**, not an attempt to replace Claude Code’s orchestration.
- `spec.md` is now treated as the **run card** for PM / Engineering / QA.
- research is now a first-class **conditional lane** inside planning.
- planning distinguishes **always-on** artifacts from **optional** artifacts.
- implementation now starts from a minimal brief and uses **adaptive agent budgets** instead of routine test+implement+checker fan-out on every task.
- review now has an explicit **lens budget** tied to the harness profile.
- new `/xlfg:audit` command and `xlfg audit` CLI measure workflow load, SDLC coverage, and benchmark readiness.
- added `docs/benchmarking.md` so xlfg has a live A/B evaluation protocol instead of only opinions.
- plugin manifests were synced back to the package version.
- several read-only/mapping agents were moved to lighter models.

## 3. The most important conceptual change

The harness should now be understood as:

- **Claude Code = orchestrator**
- **xlfg = thin SDLC guardrail layer**

If a future change makes xlfg feel like a heavy process manager that second-guesses Claude Code on routine tasks, treat that as a regression.

## 4. Planning doctrine now

- planning is still lead-owned
- research is part of SDLC, but only when external truth matters
- `spec.md` should be short enough to re-read often
- optional artifacts should stay optional
- specialist budgets should remain small and explicit
- proof is still mandatory before shipping

## 5. Files that matter most now

1. `docs/benchmarking.md`
2. `plugins/xlfg-engineering/commands/xlfg.md`
3. `plugins/xlfg-engineering/commands/xlfg-plan.md`
4. `plugins/xlfg-engineering/commands/xlfg-implement.md`
5. `plugins/xlfg-engineering/commands/xlfg-review.md`
6. `plugins/xlfg-engineering/commands/xlfg-audit.md`
7. `xlfg/audit.py`
8. `xlfg/runs.py`
9. `tests/test_xlfg.py`

## 6. What not to regress

- do not reintroduce many-agent routine fan-out
- do not make every optional artifact mandatory again
- do not let `spec.md` bloat into another unreadable dump
- do not let research become a fake ritual phase
- do not accept a better-looking process if it increases load without improving outcomes
- do not let plugin/package versions drift again

## 7. Current known limitations

- the audit score is a transparent surrogate, not a direct token meter
- the plugin still depends on planner honesty for artifact quality
- live A/B evaluation against real Claude Code still must be run outside this repo
- some optional agents could be tuned further once real task data accumulates
