---
name: xlfg-debug
description: Autonomous diagnosis run. Dispatches 2 phase skills (intent, debug) and 2 phase agents (recall, context) to find the deep root without editing source.
argument-hint: "[bug report, prompt failure, misleading behavior, or diagnosis request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Write, WebSearch, WebFetch, TaskCreate, TaskUpdate, TaskList, Agent, Skill(xlfg-engineering:xlfg-intent-phase *), Skill(xlfg-engineering:xlfg-debug-phase *)
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

Treat this invocation as **one autonomous diagnosis run** split across 4 phases. You are the conductor. The pipeline mixes two dispatch mechanisms:

- **Phase skills** (intent, debug) load just-in-time via the `Skill` tool and run in your own context. They drive the diagnosis reasoning.
- **Phase agents** (recall, context) dispatch via the `Agent` tool and run in their own sub-contexts. They explore heavily and return a distilled synthesis via a mandatory `## Return format` section.

Allowed-tools **intentionally excludes `Edit` and `MultiEdit`**. You cannot modify product source, tests, fixtures, migrations, or configs. `Write` is granted, but its **only sanctioned use** is the debug skill creating `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Writing to any other path is a contract violation.

## What `/xlfg-debug` is (and isn't) in this version

This is `/xlfg` with the plan / implement / verify / review / compound phases removed, leaving the diagnosis-relevant pipeline recall → intent → context → debug. The product stays frozen. You are not shipping — you are explaining, and writing that explanation to disk so it survives the session.

xlfg v6.5 is a **conductor-plus-phase-skills-and-agents architecture**. The 2 skill phases live under `plugins/xlfg-engineering/skills/xlfg-*-phase/`; the 2 agent phases live under `plugins/xlfg-engineering/agents/`. This conductor dispatches them in order. There is **no v5 coordination layer** — no `spec.md`, `workboard.md`, `phase-state.json`, or `verification.md` files. The run lives in your context plus the 2 agent sub-contexts, and in the real repo.

The durable archive is minimal and debug-specific:

- `docs/xlfg/current-state.md` — optional, tracked, one-page living summary of the project's load-bearing truths. Read by the recall phase-agent. Never written by a debug run.
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

## Batch pipeline

Dispatch these 4 phases in this exact order. The mechanism differs per phase:

1. **Agent: `xlfg-recall`** — dispatch via the `Agent` tool with `subagent_type: "xlfg-recall"`.
2. **Skill: `xlfg-engineering:xlfg-intent-phase`** — load via the `Skill` tool.
3. **Agent: `xlfg-context`** — dispatch via the `Agent` tool with `subagent_type: "xlfg-context"`.
4. **Skill: `xlfg-engineering:xlfg-debug-phase`** — load via the `Skill` tool.

Skill phases load just-in-time from their `SKILL.md` body. Agent phases run in their own sub-contexts; brief each agent with a self-contained prompt (see §Briefing agents) and read only its `## Return format` block from the returned message.

## Briefing agents

Each agent dispatch needs a hand-written brief. Do not paste `$ARGUMENTS` raw — synthesize from what you already know.

For `xlfg-recall` (first phase): brief includes RUN_ID and the raw user ask. No prior phase synthesis to attach.

For `xlfg-context` (after intent): brief includes RUN_ID, the intent-phase synthesis (resolved bug claim in the falsifiable "when X, system should Y, actually does Z, observed at boundary B" shape), and the recall synthesis. Emphasize the debug-specific framing — smallest repro, suspect path, determinism question.

Skill dispatches (`xlfg-intent-phase`, `xlfg-debug-phase`) must pass `args: "<RUN_ID>"`. Both skill bodies rely on that arg, not on conversation memory; a mid-run loopback re-passes the same RUN_ID so `diagnosis.md` lands at the original path rather than a slightly different slug.

You read each agent's final message, which must match its declared Return format. Summarize into your own working notes and dispatch the next phase.

## Between phases

After any phase (skill or agent) returns, your very next tool call is the dispatch for the next phase in the pipeline. Not a progress note, not a user-facing confirmation, not a pause for review — the next `Skill` or `Agent` call, in the same turn.

A phase's `## Done signal` (skills) or `## Return format` (agents) means *that phase* finished its work and handed you its conclusion. It does not mean the run ended. The run ends only after phase 4 (debug skill) has written `diagnosis.md` and you've written the completion-summary pointer.

The only valid mid-run turn boundaries are:

- The intent skill returns with `needs-user-answer` → ask at most three numbered blocking questions and stop.
- Loopback cap hit (2 context-debug cycles, see below) → escalate with a one-line failure summary.
- Phase 4 (debug) returned → write the completion-summary pointer. This is the sole end-of-run exit.

**Anti-pattern to avoid:** outputting a natural-sounding transition like *"Recall done, proceeding to intent."*, *"Intent resolved, moving to context."*, or *"Context map in hand, entering debug."* and then ending the turn. "Proceeding", "moving", "next up", "handing off" describe your *next action* — that action must be the tool call you just described, not an end-of-turn. If you wrote a transition sentence, the very next thing you emit must be the dispatch.

Do not wait for the user to say "continue", "ok", or anything else to resume between phases. The user invoked `/xlfg-debug` once; that is your authorization for the whole run.

## Operating contract

- **One run, one conductor turn.** All 4 dispatches + the completion-summary pointer happen in a single continuous conductor turn. Do not end your turn between phases. You own the whole investigation.
- **No source edits.** Do not change product code, tests, fixtures, migrations, or configs. The tool-level guard is in `allowed-tools`; the discipline is also a prompt-level contract. If you catch yourself wanting to `Edit`, you're in `/xlfg`, not `/xlfg-debug`.
- **One sanctioned Write path.** The only path you may pass to `Write` is `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Any other path — especially a product file, a documentation file, or `docs/xlfg/current-state.md` — is a contract violation. Stop and report to the user instead of writing.
- **Reject gimmicks.** Muting errors, widening retries, changing a test to pass, special-casing one example, hand-waving "env issue", declaring "works on the happy path" while the causal chain is unknown — these are not diagnoses.
- **Smallest honest reproduction first.** The context agent and debug skill will push you to simplify. Follow them.
- **Falsifiable hypothesis log.** Each hypothesis either survives evidence or dies cleanly. Do not hold contradictory hypotheses silently.
- **Repo truth first.** Read before you theorize. Web research when the repo is silent and freshness matters.
- **Prompt/agent debugging is still debugging.** If the bug is in a prompt or tool contract, the prompt, tool spec, context inputs, evaluation bar, and false-success trap are all part of the system under test.

## Loopback rule

If the debug skill lands on a promising hypothesis but evidence is too thin (you need a different repro, a cleaner log, a tighter boundary), re-dispatch `xlfg-context` followed by the debug skill. You may do this **at most one additional time (total: 2 context-debug cycles).** After the second cycle finishes, stop regardless of whether the mechanism is nailed — surface the exact missing evidence to the user.

**Cap: 2 context-debug cycles.** That is the hard bound; do not extend it, and do not hand the cap decision back to the user before it's hit.

## Artifact policy (no writes beyond diagnosis)

A debug run produces exactly one artifact: `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. That path is gitignored by the canonical v6 runs block (seeded by `/xlfg-init`), so there is nothing to stage. Do not `git add`, do not stage anything, do not create a commit. If tracked product changes appear in `git status` at the end of a debug run, a phase has violated the no-source-edits contract — report the mismatch to the user and stop; do not paper over it.

This is the intended symmetry with `/xlfg`: `/xlfg` owns committing product changes, `/xlfg-debug` owns writing a diagnosis and nothing else.

## No-source-edits check (mandatory before completion summary)

After the debug skill returns and before you write the completion summary, verify the no-source-edits contract held. A run that quietly let a phase edit a tracked product file is not a diagnosis — it's a silent regression.

1. Run `git status --porcelain` once via `Bash`. Read the output yourself; don't assume.
2. **If the output is empty** (or lists only `docs/xlfg/runs/` or other gitignored paths), the contract held. Proceed to the completion summary, and cite the command in the "No writes beyond diagnosis" line.
3. **If the output lists any tracked non-gitignored path** (source, tests, fixtures, migrations, configs, manifests, docs outside the runs archive), a phase violated the no-source-edits contract. Stop. Do not commit, do not stage, do not paper over it. Report the violation to the user and name the offending path(s) so they can `git restore` or investigate.

This step mirrors `/xlfg`'s end-of-run-commit discipline, minus the commit — `/xlfg` owns committing product changes, `/xlfg-debug` owns writing a diagnosis and nothing else. Do not skip this check, and do not collapse it into the debug skill — the debug skill writes the archive, the conductor owns the verification.

## Completion summary (end-of-run template)

Real diagnosis lives at `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Chat output is the pointer — labeled bullet sections.

Six mandatory sections, in order: `Mechanism:`, `Evidence:`, `Repair:`, `Unknowns:`, `Verified:`, `Archive:`. Each: label on its own line, then `- <bullet>` lines (≤80 chars, one clause each), with a blank line before the next section. One clause per bullet — no compound sentences, semicolons, em-dash splits, or nested parentheticals. If detail does not fit, the bullet says `- see archive`.

The `Verified:` bullet is contract-bearing: it must cite `git status --porcelain`. On the success path, write `- git status --porcelain clean`. On a no-source-edits violation, replace the bullet with `- VIOLATION: <path>` (path only) and stop without suggesting next steps.

No closing prose.
