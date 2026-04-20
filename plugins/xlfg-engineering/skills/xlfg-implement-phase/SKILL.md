---
description: Internal xlfg phase skill. Make the change honestly — edit don't rewrite, tests alongside source, failure-mode check each edit, no out-of-scope patches.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, Skill(xlfg-engineering:xlfg-task-implementer *), Skill(xlfg-engineering:xlfg-test-implementer *), Skill(xlfg-engineering:xlfg-task-checker *)
---

# xlfg-implement-phase

Use only during `/xlfg` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

Make the change. Make it honestly.

## Lens

You are the engineer writing the code, and you are the reviewer reading over your own shoulder. Both at once.

## How to work it

- **Edit, don't rewrite.** Prefer `Edit` over `Write` for existing files. Touch the minimum number of lines that satisfies the plan.
- **Follow the plan.** If the plan was wrong, stop and repair the plan, then resume. Do not silently drift.
- **No comments-as-narration.** Do not write comments that describe what the code does — well-named identifiers do that. Write a comment only when the *why* is non-obvious: a hidden constraint, a subtle invariant, a workaround for a specific bug.
- **Tests alongside source.** Write the tests the plan called for. If you find yourself wanting to "just ship the source and add tests later," that is a signal you are not confident in the source. Fix that first.
- **Failure-mode check.** After each meaningful edit, ask: "What has to be true for this to work, and is each of those things actually true in the code I just wrote?" This is the cheapest bug catch you have.
- **No out-of-scope patches.** If a failing test is caused by a file outside your packet's surface, you have two honest options: widen the packet scope intentionally, or report the failure and stop. Do not monkey-patch adjacent code to make a green bar appear.

## Done signal

All planned edits exist, all planned tests exist, and nothing outside the planned scope changed.

This is a handoff cue to the conductor, not an end-of-run marker. The conductor's very next action is dispatching the verify phase — not pausing to show a diff or wait for the user.

## Stop-traps

- Writing "clever" code for a straightforward problem. If the reviewer has to think, the code is wrong.
- Adding error handling for cases that cannot happen. Trust internal code and framework guarantees; validate only at system boundaries (user input, external APIs).
- Leaving partial implementations. If you can't finish a function in this run, don't start it.
- Over-generous error messages with stack traces in user-facing surfaces. Log the detail server-side; show the user what they can act on.

## Optional specialist skills

Load these hidden lens skills via the `Skill` tool when the implementation is non-trivial enough to benefit from a focused pass. For a one-line edit, load none.

- `xlfg-engineering:xlfg-task-implementer` — source-edit discipline when the change spans several files or touches stylistically tricky code.
- `xlfg-engineering:xlfg-test-implementer` — test authoring when the proof surface is new and you want to stay behavior-focused.
- `xlfg-engineering:xlfg-task-checker` — local acceptance check between slices, before verify runs the declared contract.
