---
description: Internal xlfg phase skill. Write the per-run durable archive; sparingly promote load-bearing insights into docs/xlfg/current-state.md.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, Write
---

# xlfg-compound-phase

Use only during `/xlfg` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

Produce the durable artifacts of this run — the per-run archive future sessions can recall, and (rarely) a promotion to the project's living summary.

## Lens

You are a post-mortem author, talking to the next engineer who will touch this surface.

## How to work it

### 1. Write `docs/xlfg/runs/<RUN_ID>/run-summary.md` (mandatory)

This is mandatory for every `/xlfg` run. Create the directory if needed. Use this template exactly:

```markdown
# Run summary — <RUN_ID>

## Ask
<1–2 sentences restating what the user asked. Not a paste of $ARGUMENTS.>

## What changed
- `<path/to/file>`: <one line, why the change>
- `<path/to/file>`: <one line, why the change>

## Proof
- fast_check: `<exact command>` — <result: PASSED / FAILED / NOT RUN with justification>
- smoke_check: `<exact command>` — <result>
- ship_check: `<exact command>` — <result>

## Residual risk
<What you did not test, what might still be wrong, what you'd check next with another hour. 1–3 bullets.>

## Durable lesson
<1–3 sentences, ~50 words, capturing the non-obvious thing learned. Omit the section entirely if the run produced nothing durable — do not fabricate.>
```

Aim ~200 words total. It's an archive, not a narrative.

### 2. Consider promoting to `docs/xlfg/current-state.md`

This is the project's one-page "read this first" handoff. Promote only when the run learned something **a future run would regret not knowing** — a load-bearing invariant, an active constraint, a trap that already bit someone.

- If `current-state.md` doesn't exist and this run earned one, create it with the template below.
- If it exists, edit it in place. Keep the whole file under ~300 words.
- Promote sparingly: most runs should NOT update `current-state.md`. The signal is diluted if every run adds a line.

Template for `current-state.md`:

```markdown
# <project name> — current state

Read this first when entering this repo with xlfg.

## What this project is
<1–2 sentences>

## Load-bearing truths
- <fact a future run must know>
- <fact a future run must know>

## Known traps
- <failure mode that bit us before>

## Active constraints
- <deadline, compliance requirement, migration in flight>
```

## Done signal

`docs/xlfg/runs/<RUN_ID>/run-summary.md` exists and is complete. If you updated `current-state.md`, you can hand it to a teammate who wasn't on this run and they would act differently next time because of it.

## Stop-traps

- Skipping the run-summary write because "the chat already has it." Chat evaporates; disk doesn't.
- Promoting every run to `current-state.md`. Most runs don't earn it.
- Pasting the entire chat log into `run-summary.md`. The template is terse on purpose.
- Over-generalizing the durable lesson. A lesson that applies to "all code" applies to nothing.
