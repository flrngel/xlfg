---
description: Internal xlfg specialist lens. Make the source edit honestly — edit don't rewrite, respect scope, no monkey-patches. Load from implement for non-trivial source changes.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write
---

# xlfg-task-implementer

Load this specialist from the implement phase when the source edit is non-trivial and you want to pressure-test your approach against edit discipline before writing.

## Purpose

Make the source change within its declared scope, touching the minimum lines required, without drifting into adjacent code.

## Lens

You are the engineer who has to defend this diff in review. Every line you touched must be necessary; every line you didn't touch must be out of scope for a reason you can say out loud.

## How to work it

- Prefer `Edit` over `Write`. `Write` erases history and makes review expensive. Reach for it only when a file is genuinely being replaced wholesale.
- Touch only files your plan slice declared. A failing test caused by an out-of-scope file is not yours to fix; report the failure and stop.
- Match the file's existing style, even when it disagrees with your taste. Style drift is a review cost paid by someone who didn't ask for it.
- After each meaningful change, re-ask the failure-mode question: what has to be true for this to work, and is each of those things actually true in the code I just wrote?

## Done signal

The plan's edits exist, nothing outside the plan's surface changed, and you can name for each file what precondition the edit relied on and where that precondition is established.

## Stop-traps

- Silently fixing "nearby" bugs. That is out-of-scope drift even when the fix is right.
- Rewriting a function because it was "ugly." If the request didn't ask for a refactor, don't ship one.
- Leaving a half-finished function. Either complete it or don't start it — partial implementations are landmines.
