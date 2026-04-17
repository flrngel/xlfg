---
description: Internal xlfg phase skill. Use only during /xlfg-debug runs to reproduce the failure, separate symptom from mechanism, and write an evidence-backed diagnosis without changing source code.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write, WebSearch, WebFetch, Agent, SendMessage
---

# xlfg-debug-phase

Use only during `/xlfg-debug` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Produce an evidence-backed root-cause report and likely repair surface without modifying source code.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read:
   - `context.md`
   - `memory-recall.md`
   - `spec.md`
   - `test-contract.md`
   - `test-readiness.md`
   - `workboard.md`
   - optional `repo-map.md`, `why.md`, `diagnosis.md`, `research.md`, `harness-profile.md`, `debug-report.md`
   - `docs/xlfg/knowledge/current-state.md`
3. Treat the intent contract in `spec.md` as canonical. For prompt or agent debugging, treat the prompt text, tool permissions or contracts, context windows, evaluation criteria, and false-success traps as first-class diagnosis surfaces. Do not collapse everything into one suspicious line too early.
4. Use specialists as lane owners for diagnosis quality:
   - always run `xlfg-repo-mapper` unless a fresh same-run `repo-map.md` already exists and clearly covers the failing surface
   - always run `xlfg-why-analyst`
   - always run `xlfg-root-cause-analyst`
   - run `xlfg-harness-profiler` when any runnable harness, failing command, or log stream exists
   - run `xlfg-env-doctor` when environment, local server health, race timing, infra, or dependency drift may be causal
   - run `xlfg-test-strategist` when the reproducer or disproof probes are still vague after first-pass diagnosis
   - run `xlfg-researcher` only when freshness or external docs materially change the diagnosis
5. Keep the default specialist budget lean and sequential. Run one active artifact-producing specialist at a time, then load the next specialist only if the previous artifact leaves a concrete unresolved gap. Do not ask diagnosis specialists to spawn more specialists.
6. Keep these specialists foregrounded, short-lived, and leaf-only. After each specialist returns, verify its expected artifact exists, begins with `Status:`, and contains real findings instead of preparation notes. If it does not, use `SendMessage` with the returned agent ID to resume the same specialist once before treating the lane as failed. If no agent ID is available, re-dispatch the exact same packet once.
7. Follow the debugging method in this order and record it in artifacts:
   - make the expected correct behavior explicit
   - verify the bug or user pain is real
   - create the **smallest honest reproducer**
   - simplify until irrelevant variables drop out
   - compare failing vs passing inputs, prompts, states, environments, or commits
   - form **falsifiable hypotheses** and try to disprove them
   - trace the **first wrong state** or bad assumption, not just the final crash site
   - use history search, `git bisect`, trace replay, targeted instrumentation, or log slicing when they materially shorten origin search
   - ask "why" until the broken invariant or missing capability is clear, not merely the symptom
8. Update `test-contract.md` so it becomes a diagnosis proof contract:
   - at least one primary reproduction card
   - at least one comparison or guard card
   - exact `fast_check` or manual steps
   - at least one `anti_monkey_probe` that would still fail under a shallow patch
   - mark a command as `GUESS` when the repo evidence is not strong enough to claim certainty
9. Update `spec.md` as the **single source of truth**:
   - `Outcome / why`
   - `Research and context`
   - `Execution shape` for a diagnosis-only run
   - `Solution summary`, where `chosen solution` becomes the likely repair surface only — no code changes
   - `Task map` with diagnosis tasks only
   - `Proof summary` with reproduction, disproof, confidence, and remaining unknowns
10. Write `diagnosis.md` with the causal chain and rejected shortcuts.
11. Write `debug-report.md` as the final diagnosis artifact.
12. Update the blockers and next-safest-repair sections of `workboard.md`. Mark implementation-oriented stages as `SKIPPED (/xlfg-debug)` when that improves clarity. The `## Phase status` block is rendered by the conductor from `.xlfg/phase-state.json`.
13. Create optional docs only when they change the evidence surface: `repro-notes.md`, `probe-log.md`, `history-findings.md`, `env-plan.md`, `research.md`. Do not create implementation tasks.

## Required output shape

`debug-report.md` must open with YAML frontmatter declaring `status: DONE`, `status: BLOCKED`, or `status: FAILED` and contain:

```markdown
# Debug report

## Problem summary
- ...

## Expected vs observed
- ...

## Smallest honest reproduction
- ...

## Causal chain
1. ...
2. ...
3. ...

## Deep root problem
- ...

## Strongest evidence
- ...

## Fake fixes to reject
- ...

## Likely repair surface (no edits made)
- ...

## Unknowns / confidence
- ...

## Next safest proof step
- ...
```

## Delegation packet rules

- Preseed the target artifact before dispatch. The parent conductor should create the file named in `PRIMARY_ARTIFACT` with YAML frontmatter `status: IN_PROGRESS`, the scoped mission, and a short checklist so the specialist is resuming a concrete work item instead of starting from an empty chat turn.
- Every specialist packet must begin with machine-readable headers:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only

CONTEXT_DIGEST:
- <quoted excerpt or bullet from spec.md / context.md / repo-map.md the specialist actually needs>

PRIOR_SIBLINGS:
- <path/to/sibling-artifact.md>: <one-line summary of what it already covered, or `none`>
```

- `CONTEXT_DIGEST` and `PRIOR_SIBLINGS` are mandatory. See `agents/_shared/output-template.md` for the canonical shape. The digest replaces the agent's "you will receive these N files" reads. Siblings is how `xlfg-root-cause-analyst` builds on `xlfg-why-analyst` instead of re-deriving the same expectation contract — and how each subsequent diagnosis specialist refines rather than restarts.
- Pass objective context, not just a naked query. Include the exact ask, nearby constraints, and why the artifact matters to the next phase.
- Only the phase conductor may delegate. Never ask a debug specialist to spawn nested subagents or to hand off the lane to another worker.
- Default to **sequential** dispatch for artifact-producing diagnosis work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Guardrails

- Do not edit product source, tests, fixtures, migrations, prompts, or configs as part of this phase. Evidence artifacts only.
- Do not stop at the first suspicious line; keep going until you can explain the mechanism that makes the symptom inevitable.
- A green command without a stable explanation is not a diagnosis.
- Do not call something a root cause if you cannot say what invariant is broken or missing.
- Reject gimmicks: retry inflation, timeout padding, logging-only patches, silent catches, one-example special cases, or blaming the model, user, or environment without proof.
- If the issue appears prompt-related, inspect instruction order, objective splitting, missing context, evaluation mismatch, and tool affordance mismatch before blaming the model.
- If evidence remains weak after one repair loop, say so explicitly and name the smallest missing proof.
