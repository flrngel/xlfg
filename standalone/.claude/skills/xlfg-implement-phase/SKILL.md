---
description: Internal xlfg phase skill. Use only during /xlfg runs to implement the plan, update tests, and keep the run card truthful without asking the user to code.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, Agent
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
4. Keep one conductor, but let specialist implementers own the work lanes:
   - for each non-trivial task, run `xlfg-task-implementer` explicitly
   - when tests or proof artifacts must change, run `xlfg-test-implementer`
   - before marking a task done, run `xlfg-task-checker`
5. Keep these specialists foregrounded. Treat a missing report or a prep-only response as incomplete work, not success.
6. The main conductor should coordinate task order, integrate specialist artifacts, and resolve conflicts; it should not bypass the specialist lanes unless the task is truly trivial or the specialist failed twice.
7. Implement the smallest coherent set of code and test changes that satisfy the run card.
8. Run targeted task-level checks as you go.
9. Update `spec.md` and `workboard.md` when scope, task status, or chosen solution changes.
10. If the diagnosis or proof contract changes materially, return to planning instead of pushing through a patch.

## Guardrails

- Do not ask the user to code, wire the repo, or run major local verification when the agent can do it.
- Do not weaken tests to get green.
- Do not accept a shallow symptom patch when the run card says the root problem lives elsewhere.
- Keep the implementation aligned to the false-success trap in `spec.md`.
