---
description: Internal xlfg phase skill. Use only during /xlfg runs to implement the plan, update tests, and keep the run card truthful without asking the user to code.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, Agent, SendMessage
---

# xlfg-implement-phase

Use only during `/xlfg` orchestration.

Input: `$ARGUMENTS` (`RUN_ID` or `latest`)

## Objective

Implement the planned change with one conductor, specialist task owners, aligned tests, and truthful run-state updates.

## Process

1. Resolve `RUN_ID`, `DOCS_RUN_DIR`, and `DX_RUN_DIR`.
2. Read first:
   - `spec.md`
   - `test-contract.md`
   - `test-readiness.md`
   - `workboard.md`
   - any optional decision docs that actually exist
   - `docs/xlfg/knowledge/current-state.md`
3. If `test-readiness.md` is not `READY`, stop implementing and return control to planning immediately.
4. Keep one conductor, but let specialist implementers own the work lanes. Dispatch one atomic task packet at a time:
   - for each non-trivial task, run `xlfg-task-implementer` explicitly with `TASK_ID`, bounded `scope`, one required artifact, and one done check
   - when tests or proof artifacts must change, run `xlfg-test-implementer` with the same task packet discipline
   - before marking a task done, run `xlfg-task-checker` against that exact task packet
5. Keep these specialists foregrounded, short-lived, and leaf-only. Treat a missing report or a prep-only response as incomplete work, not success. Use `SendMessage` with the returned agent ID to resume the same specialist once before falling back to repair or re-splitting the task. If no agent ID is available, re-dispatch the exact same packet once.
6. The main conductor should coordinate task order, integrate specialist artifacts, and resolve conflicts; it should not bypass the specialist lanes unless the task is truly trivial or the specialist failed twice.
7. Implement the smallest coherent set of code and test changes that satisfy the run card.
8. Run targeted task-level checks as you go. Do not close a task until its packet artifact exists and the done check is honestly addressed.
9. Update `spec.md` and `workboard.md` when scope, task status, or chosen solution changes.
10. If the diagnosis or proof contract changes materially, return to planning instead of pushing through a patch.

## Delegation packet rules

- Preseed the target artifact before dispatch. The parent conductor should create the file named in `PRIMARY_ARTIFACT` with YAML frontmatter `status: IN_PROGRESS`, the scoped mission, and a short checklist so the specialist is resuming a concrete work item instead of starting from an empty chat turn.
- Every specialist packet must begin with machine-readable headers:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only

OWNERSHIP_BOUNDARY:
- Own: the assigned task's code surface, test surface, or checker verdict exactly as named in the task packet
- Do not redo: planning decisions, proof strategy, sibling task changes, or verification-phase run truth
- Consume: `task-brief.md`, `spec.md`, `test-contract.md`, same-task implementer/test reports, and same-phase sibling artifacts listed below

CONTEXT_DIGEST:
- <quoted excerpt or bullet from spec.md / task-brief.md / test-contract.md the specialist actually needs>

PRIOR_SIBLINGS:
- <path/to/sibling-artifact.md>: <one-line summary of what it already covered, or `none`>
```

- `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, and `PRIOR_SIBLINGS` are mandatory. See `agents/_shared/output-template.md` for the canonical shape. The digest replaces the agent's "you will receive these N files" reads. Siblings is how `xlfg-task-checker` reuses the implementer-report.md instead of re-deriving the diff, and how `xlfg-test-implementer` builds on the implementer's report rather than re-reading raw source.
- Implementation ownership boundaries:
  - `xlfg-task-implementer` owns product/source changes for the task. It edits tests only when the packet explicitly includes test files in its ownership boundary or no separate `xlfg-test-implementer` lane will run.
  - `xlfg-test-implementer` owns test/proof file changes. It consumes `implementer-report.md` and must not make product/source changes except explicit test fixtures or helpers named in FILE_SCOPE.
  - `xlfg-task-checker` owns the task-local ACCEPT/REVISE verdict. It must cite implementer/test reports, inspect only targeted source when needed, and must not rerun full scenario proof or edit product/test files.
- Pass objective context, not just a naked query. Include the exact ask, nearby constraints, and why the artifact matters to the next phase.
- Only the phase conductor may delegate. Never ask an implementation specialist to spawn nested subagents or create its own fan-out.
- Default to **sequential** dispatch for artifact-producing planning/context work. Parallelize only when packets are truly independent, small, and read-mostly.
- When a specialist hits a nonfatal tool failure, resume the same lane instead of accepting a stop. Common recoveries: use `LS` or `Glob` instead of `Read` on directories; use `Grep` plus chunked `Read` windows instead of loading an oversized file in one shot.

## Guardrails

- Do not ask the user to code, wire the repo, or run major local verification when the agent can do it.
- Do not weaken tests to get green.
- Do not accept a shallow symptom patch when the run card says the root problem lives elsewhere.
- Keep the implementation aligned to the false-success trap in `spec.md`. If a task packet grows vague or multi-output in flight, send it back to planning for re-splitting instead of accepting a half-finished specialist return.
