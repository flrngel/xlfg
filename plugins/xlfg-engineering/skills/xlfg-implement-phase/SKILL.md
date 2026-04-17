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
8. Run targeted task-level checks as you go. Do not close a task until its packet artifact exists and the done check is honestly addressed. A task `DONE_CHECK` should be the cheapest honest proof for that task; do not rerun a generic full build/full suite after every sibling task unless the current task changed shared type/schema/config surfaces that require it.
9. Update `spec.md` and `workboard.md` when scope, task status, or chosen solution changes.
10. If the diagnosis or proof contract changes materially, return to planning instead of pushing through a patch.

## Delegation packet rules

Follow `agents/_shared/dispatch-rules.md` for the full delegation contract (packet-size ladder, preseed rule, machine-readable headers with `PRIMARY_ARTIFACT` / `DONE_CHECK` / `RETURN_CONTRACT` / `OWNERSHIP_BOUNDARY` / `CONTEXT_DIGEST` / `PRIOR_SIBLINGS` / `Do not redo` / `Consume:`, micro-packet budget, proof budget, compaction, sequential-dispatch default, resume-same-specialist-before-fallback). Only the phase conductor may delegate.

Every implement-phase packet MUST begin with the machine-readable headers from `_shared/dispatch-rules.md §3`. `CONTEXT_DIGEST` carries decisions + rationale + path refs, replacing the agent's "you will receive these N files" reads. Siblings is how `xlfg-task-checker` reuses the implementer-report.md instead of re-deriving the diff, and how `xlfg-test-implementer` builds on the implementer's report rather than re-reading raw source.

### Implementation ownership boundaries

- `xlfg-task-implementer` owns product/source changes for the task. It edits tests only when the packet explicitly includes test files in its ownership boundary or no separate `xlfg-test-implementer` lane will run.
- `xlfg-test-implementer` owns test/proof file changes. It consumes `implementer-report.md` and must not make product/source changes except explicit test fixtures or helpers named in FILE_SCOPE.
- `xlfg-task-checker` owns the task-local ACCEPT/REVISE verdict. It must cite implementer/test reports, inspect only targeted source when needed, and must not rerun full scenario proof or edit product/test files.

If a task brief or packet has grown into an implementation script, compact it before dispatch: preserve behavior, constraints, scope, and proof; remove line-by-line recipes and full before/after snippets.

Keep broad proof in its lane. Use `DONE_CHECK` for task-local confidence and leave full build/full-suite/live acceptance to verify phase unless this packet is explicitly the final integration lane.

Compact implementer/checker artifacts before updating `spec.md` or `workboard.md`: carry forward status, changed files, commands/results, blockers, and next action only; do not paste full reports into canonical run files.

## Guardrails

- Do not ask the user to code, wire the repo, or run major local verification when the agent can do it.
- Do not weaken tests to get green.
- Do not accept a shallow symptom patch when the run card says the root problem lives elsewhere.
- Keep the implementation aligned to the false-success trap in `spec.md`. If a task packet grows vague or multi-output in flight, send it back to planning for re-splitting instead of accepting a half-finished specialist return.
