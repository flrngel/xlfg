# NEXT_AGENT_CONTEXT

This is the required handoff document for the next intelligent agent continuing work on this repo.

## 1. Current bundle version

- **xlfg version:** `2.2.0`
- this is a **minor** redesign because Claude Code compatibility, autonomy, and run-shape all changed materially

## 2. What changed in 2.2.0

This revision is focused on one harder problem:

> `/xlfg` should feel native to modern Claude Code instead of acting like an older command harness that makes the human schedule the work.

### Main changes

- `/xlfg` is now **skills-first** and ships a real `skills/xlfg/SKILL.md` entrypoint.
- a **standalone short-name pack** now ships under `standalone/.claude/skills/xlfg/` so users can get direct `/xlfg` without plugin namespacing.
- `/xlfg` now runs as **one autonomous SDLC flow** by default; phase commands remain escape hatches only.
- the run scaffold is now a **lean 6-file core**: `context.md`, `memory-recall.md`, `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`.
- `spec.md` is now the explicit **single source of truth** for PM / UX / Engineering / QA / Release state.
- internal consent friction was reduced with `allowed-tools`, `effort`, and a narrow `ExitPlanMode` auto-approval hook.
- the bundle now documents **plugin vs standalone** invocation clearly.
- high-impact internal memories (`CLAUDE.md`, `AGENTS.md`, scaffold docs, agent prompts) were updated so they no longer assume the old split artifact set is mandatory.
- the audit now reports a **Claude Code compatibility score** in addition to workflow load and SDLC coverage.
- plugin manifests, package metadata, docs, and tests were synced to `2.2.0`.

## 3. The most important conceptual change

The harness should now be understood as:

- **Claude Code = orchestrator**
- **xlfg = thin, skills-native SDLC layer**

If a future change makes xlfg feel like a permission-heavy project manager that asks the user to run `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, etc., treat that as a regression.

## 4. Planning doctrine now

- planning is still proof-first, but not document-heavy
- `spec.md` should absorb duplicated planning state whenever possible
- research is part of SDLC only when repo-local truth is insufficient or the user explicitly asks
- optional artifacts should stay optional and decision-driven
- one owner is the default; extra agents are trigger-based
- verification must remain the real quality gate

## 5. Files that matter most now

1. `plugins/xlfg-engineering/skills/xlfg/SKILL.md`
2. `standalone/.claude/skills/xlfg/SKILL.md`
3. `plugins/xlfg-engineering/commands/xlfg.md`
4. `plugins/xlfg-engineering/hooks/hooks.json`
5. `plugins/xlfg-engineering/README.md`
6. `docs/claude-code-2026-compatibility.md`
7. `docs/benchmarking.md`
8. `xlfg/runs.py`
9. `xlfg/audit.py`
10. `xlfg/verify.py`
11. `tests/test_xlfg.py`

## 6. What not to regress

- do not reintroduce user-managed phase choreography as the default
- do not make many split planning artifacts mandatory again
- do not let `spec.md` bloat into unreadable ceremony
- do not widen hooks or permissions recklessly; keep them narrow and transparent
- do not drift away from current Claude Code skill/plugin conventions
- do not let internal docs tell agents to require old files when `spec.md` already carries the truth
- do not let plugin/package versions drift again

## 7. Current known limitations

- the audit score is a transparent surrogate, not a direct token meter from Claude Code itself
- several deeper historical research docs still describe the old artifact-heavy model; they are now historical context, not the recommended workflow
- some optional agents still mention legacy files in detailed body text, but they now carry a compatibility note telling them to start from `spec.md` and treat legacy files as optional
- live A/B evaluation against real Claude Code still must be run outside this repo
