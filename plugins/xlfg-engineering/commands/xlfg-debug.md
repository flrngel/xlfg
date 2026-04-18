---
name: xlfg-debug
description: Autonomous diagnosis run. Dispatches 4 hidden phase skills — recall, intent, context, debug — to find the deep root without changing source code.
argument-hint: "[bug report, prompt failure, misleading behavior, or diagnosis request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Write, WebSearch, WebFetch, TaskCreate, TaskUpdate, TaskList, Skill(xlfg-engineering:xlfg-recall-phase *), Skill(xlfg-engineering:xlfg-intent-phase *), Skill(xlfg-engineering:xlfg-context-phase *), Skill(xlfg-engineering:xlfg-debug-phase *), Skill(xlfg-engineering:xlfg-why-analyst *), Skill(xlfg-engineering:xlfg-query-refiner *), Skill(xlfg-engineering:xlfg-repo-mapper *), Skill(xlfg-engineering:xlfg-harness-profiler *), Skill(xlfg-engineering:xlfg-env-doctor *), Skill(xlfg-engineering:xlfg-researcher *), Skill(xlfg-engineering:xlfg-context-adjacent-investigator *), Skill(xlfg-engineering:xlfg-context-constraints-investigator *), Skill(xlfg-engineering:xlfg-context-unknowns-investigator *), Skill(xlfg-engineering:xlfg-root-cause-analyst *), Skill(xlfg-engineering:xlfg-verify-runner *)
effort: high
hooks:
  PermissionRequest:
    - matcher: "ExitPlanMode"
      hooks:
        - type: command
          command: >
            echo '{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}'
---

# /xlfg-debug — one autonomous diagnosis run

Use this when the user wants a serious debugging run that finds the **deep root problem** without editing the product.

INPUT: `$ARGUMENTS`

Treat this invocation as **one autonomous diagnosis run** split across 4 phases. You are the conductor. Each phase is a separate skill that loads just-in-time via the `Skill` tool.

Allowed-tools **intentionally excludes `Edit` and `MultiEdit`**. You cannot modify product source, tests, fixtures, migrations, or configs. `Write` is granted, but its **only sanctioned use** is the debug skill creating `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Writing to any other path is a contract violation.

## What `/xlfg-debug` is (and isn't) in this version

This is `/xlfg` with the implement / verify / review / compound phases replaced by a single debug phase, and the product frozen. You are not shipping. You are explaining — and writing that explanation to disk so it survives the session.

xlfg v6.4 is a **conductor-plus-phase-skills architecture**. The 4 phases below are discrete skills under `plugins/xlfg-engineering/skills/xlfg-*-phase/`. This conductor dispatches them in order. There are **no sub-agents** — skills run in your main context, not in delegated sub-contexts. There is **no v5 coordination layer** — no `spec.md`, `workboard.md`, `phase-state.json`, or `verification.md` files. The run lives in your context and in the real repo.

The durable archive is minimal and debug-specific:

- `docs/xlfg/current-state.md` — optional, tracked, one-page living summary of the project's load-bearing truths. Read in the recall phase. Never written by a debug run.
- `docs/xlfg/runs/<RUN_ID>/diagnosis.md` — written by the debug skill at the end of every run. One file per run. Grep-able months later and surfaced by future recall passes.

`.xlfg/` does not exist in v6. Nothing in a debug run is written outside the sanctioned `diagnosis.md` path.

A good diagnosis gives the user:
1. The mechanism of the failure, in one or two sentences.
2. The strongest evidence for that mechanism.
3. The likely repair surface (what file / function / boundary the fix will touch), **without** opening that surface yet.
4. The fake fixes you considered and rejected.
5. The residual unknowns, named specifically.

Future `/xlfg` and `/xlfg-debug` runs will surface `diagnosis.md` in their recall phase.

## Startup

Before dispatching phase 1:

1. **`RUN_ID`** = `<YYYYMMDD>-<HHMMSS>-<kebab-slug>`. Get the real timestamp from the system clock — **do not invent it from memory or infer it from context.** Run this once via `Bash`:

   ```bash
   date +%Y%m%d-%H%M%S
   ```

   Take the exact output (e.g. `20260417-163000`), append `-` and a short (<=40 char) kebab-case summary of `$ARGUMENTS`, and that's your `RUN_ID`. Example: if `date` returns `20260417-163000` and the ask is "auth middleware drops session cookie on subdomain", `RUN_ID = 20260417-163000-session-cookie-drop`. Compute once, reuse throughout the run.
2. **Harness task bridge (optional).** Emit one `TaskCreate` per phase: `xlfg-debug: recall`, `xlfg-debug: intent`, `xlfg-debug: context`, `xlfg-debug: debug`. Update as each phase returns.
3. The run directory is created lazily by the debug skill when it writes `diagnosis.md`.

## Batch skill pipeline

Invoke these 4 hidden skills in this exact order, passing `RUN_ID` as the argument each time:

1. `xlfg-engineering:xlfg-recall-phase`
2. `xlfg-engineering:xlfg-intent-phase`
3. `xlfg-engineering:xlfg-context-phase`
4. `xlfg-engineering:xlfg-debug-phase`

Use the `Skill` tool to load each phase just-in-time.

## Operating contract

- **One run, no handoffs.** You own the whole investigation.
- **No source edits.** Do not change product code, tests, fixtures, migrations, or configs. The tool-level guard is in `allowed-tools`; the discipline is also a prompt-level contract. If you catch yourself wanting to `Edit`, you're in `/xlfg`, not `/xlfg-debug`.
- **Reject gimmicks.** Muting errors, widening retries, changing a test to pass, special-casing one example, hand-waving "env issue", declaring "works on the happy path" while the causal chain is unknown — these are not diagnoses.
- **Smallest honest reproduction first.** The context and debug skills will push you to simplify. Follow them.
- **Falsifiable hypothesis log.** Each hypothesis either survives evidence or dies cleanly. Do not hold contradictory hypotheses silently.
- **Repo truth first.** Read before you theorize. Web research when the repo is silent and freshness matters.
- **Prompt/agent debugging is still debugging.** If the bug is in a prompt or tool contract, the prompt, tool spec, context inputs, evaluation bar, and false-success trap are all part of the system under test.

## Loopback rule

If the debug skill lands on a promising hypothesis but evidence is too thin (you need a different repro, a cleaner log, a tighter boundary), dispatch the context skill again, then re-dispatch the debug skill.

**Cap: 1 loopback.** After the second context→debug cycle, stop and surface the exact missing evidence to the user.

## Artifact policy (no commit, ever)

A debug run produces exactly one artifact: `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. That path is gitignored by the canonical v6 runs block (seeded by `/xlfg-init`), so there is nothing to stage. Do not `git add`, do not stage anything, do not create a commit. If tracked product changes appear in `git status` at the end of a debug run, a phase skill has violated the no-source-edits contract — report the mismatch to the user and stop; do not paper over it with a commit.

This is the intended symmetry with `/xlfg`'s commit step: `/xlfg` owns committing product changes, `/xlfg-debug` owns writing a diagnosis and nothing else.

## Completion summary (end-of-run template)

The real diagnosis lives at `docs/xlfg/runs/<RUN_ID>/diagnosis.md` (written by the debug skill). Your chat response is a short pointer — 4–6 sentences, not a paste of the whole file. Prose the user can skim in under 30 seconds:

1. **Mechanism.** What is actually breaking, in one sentence. Not the symptom.
2. **Strongest evidence.** The concrete artifact (log line, test output, captured stdout) that makes the mechanism load-bearing, in one sentence.
3. **Likely repair surface.** File / function / boundary the fix will touch, in one sentence. Do not open it in this run.
4. **Residual unknowns.** What you did not resolve and what you'd check next if you had another hour — or "none worth naming".
5. **No commit.** State explicitly: "investigation-only run — no product changes, nothing to stage." If that line is wrong, something upstream violated the no-source-edits contract and you should say so instead.
6. **Run archive.** The path `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.
7. **Suggested next step.** Usually "open `/xlfg` to ship the fix" or "run `<experiment>` to confirm before fixing".

Do not append post-hoc rationalization, meta-commentary about the xlfg process, or reassurance about your own work. Hand the pointer to the user; they decide whether to open `/xlfg` to ship the fix.
