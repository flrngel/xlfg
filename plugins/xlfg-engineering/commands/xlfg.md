---
name: xlfg
description: Autonomous proof-first SDLC run. Dispatches 8 hidden phase skills in order — recall, intent, context, plan, implement, verify, review, compound.
argument-hint: "[feature, bugfix, investigation, or delivery request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, WebSearch, WebFetch, TaskCreate, TaskUpdate, TaskList, Skill(xlfg-engineering:xlfg-recall-phase *), Skill(xlfg-engineering:xlfg-intent-phase *), Skill(xlfg-engineering:xlfg-context-phase *), Skill(xlfg-engineering:xlfg-plan-phase *), Skill(xlfg-engineering:xlfg-implement-phase *), Skill(xlfg-engineering:xlfg-verify-phase *), Skill(xlfg-engineering:xlfg-review-phase *), Skill(xlfg-engineering:xlfg-compound-phase *), Skill(xlfg-engineering:xlfg-why-analyst *), Skill(xlfg-engineering:xlfg-query-refiner *), Skill(xlfg-engineering:xlfg-spec-author *), Skill(xlfg-engineering:xlfg-brainstorm *), Skill(xlfg-engineering:xlfg-repo-mapper *), Skill(xlfg-engineering:xlfg-harness-profiler *), Skill(xlfg-engineering:xlfg-env-doctor *), Skill(xlfg-engineering:xlfg-researcher *), Skill(xlfg-engineering:xlfg-context-adjacent-investigator *), Skill(xlfg-engineering:xlfg-context-constraints-investigator *), Skill(xlfg-engineering:xlfg-context-unknowns-investigator *), Skill(xlfg-engineering:xlfg-solution-architect *), Skill(xlfg-engineering:xlfg-root-cause-analyst *), Skill(xlfg-engineering:xlfg-test-strategist *), Skill(xlfg-engineering:xlfg-task-divider *), Skill(xlfg-engineering:xlfg-risk-assessor *), Skill(xlfg-engineering:xlfg-ui-designer *), Skill(xlfg-engineering:xlfg-test-readiness-checker *), Skill(xlfg-engineering:xlfg-task-implementer *), Skill(xlfg-engineering:xlfg-test-implementer *), Skill(xlfg-engineering:xlfg-task-checker *), Skill(xlfg-engineering:xlfg-verify-runner *), Skill(xlfg-engineering:xlfg-verify-reducer *), Skill(xlfg-engineering:xlfg-architecture-reviewer *), Skill(xlfg-engineering:xlfg-security-reviewer *), Skill(xlfg-engineering:xlfg-performance-reviewer *), Skill(xlfg-engineering:xlfg-ux-reviewer *)
effort: high
hooks:
  PermissionRequest:
    - matcher: "ExitPlanMode"
      hooks:
        - type: command
          command: >
            echo '{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}'
---

# /xlfg — one autonomous SDLC run

Use this when the user wants a serious engineering run with PM, UX, engineering, QA, and release discipline all in one pass.

INPUT: `$ARGUMENTS`

Treat this invocation as **one autonomous run** split across 8 phases. You are the conductor. Each phase is a separate skill that loads just-in-time — you invoke it with the `Skill` tool, the skill's body fills your context for that phase, and when it returns you move to the next one. Do not try to hold all 8 phase bodies in context simultaneously; that is exactly what the skill split is designed to prevent.

## What xlfg is (and isn't) in this version

xlfg v6.2 is a **conductor-plus-phase-skills architecture**. The 8 phases below are discrete skills under `plugins/xlfg-engineering/skills/xlfg-*-phase/`. This conductor dispatches them in order. There are **no sub-agents** — the skills run in your main context, not in delegated sub-contexts. There is **no v5 coordination layer** — no `spec.md`, `workboard.md`, `phase-state.json`, `verification.md`, or `test-contract.md` files. The run lives in your context and in the real repo.

There is, however, a **minimal durable archive** so a future session can recall what past runs did:

- `docs/xlfg/current-state.md` — optional, tracked, one-page living summary of the project's load-bearing truths. Read in the recall phase. Updated sparingly in compound when a run earns promotion.
- `docs/xlfg/runs/<RUN_ID>/run-summary.md` — written by the compound skill at the end of every run. One file per run. Grep-able months later.

`.xlfg/` does not exist in v6. Everything durable lives under `docs/xlfg/` and is committed.

## Startup

Before dispatching phase 1, establish the run identity and wire the task-pane bridge:

1. **`RUN_ID`** = `<YYYYMMDD>-<HHMMSS>-<kebab-slug>`. Get the real timestamp from the system clock — **do not invent it from memory or infer it from context.** Run this once via `Bash`:

   ```bash
   date +%Y%m%d-%H%M%S
   ```

   Take the exact output (e.g. `20260417-163000`), append `-` and a short (<=40 char) kebab-case summary of `$ARGUMENTS`, and that's your `RUN_ID`. Example: if `date` returns `20260417-163000` and the ask is "add a retry policy to the webhook consumer", `RUN_ID = 20260417-163000-webhook-retry`. Compute once, reuse throughout the run — do not re-invoke `date` mid-run (the timestamp should represent when the run started, not when each phase began).
2. **Harness task bridge (optional but recommended).** Emit one `TaskCreate` per phase so the Claude Code task pane mirrors the pipeline. Use these exact subjects: `xlfg: recall`, `xlfg: intent`, `xlfg: context`, `xlfg: plan`, `xlfg: implement`, `xlfg: verify`, `xlfg: review`, `xlfg: compound`. As each phase returns successfully, call `TaskUpdate` to mark the matching task completed.
3. **The run directory is created lazily.** The compound skill will `mkdir -p docs/xlfg/runs/<RUN_ID>/` before writing `run-summary.md`. Do not preseed it.

## Batch skill pipeline

Invoke these 8 hidden skills in this exact order, passing `RUN_ID` as the argument each time:

1. `xlfg-engineering:xlfg-recall-phase`
2. `xlfg-engineering:xlfg-intent-phase`
3. `xlfg-engineering:xlfg-context-phase`
4. `xlfg-engineering:xlfg-plan-phase`
5. `xlfg-engineering:xlfg-implement-phase`
6. `xlfg-engineering:xlfg-verify-phase`
7. `xlfg-engineering:xlfg-review-phase`
8. `xlfg-engineering:xlfg-compound-phase`

Use the `Skill` tool to load each phase just-in-time. Do NOT inline phase instructions from memory — read the actual skill body when you dispatch it. The phase skill's output is returned to your context; summarize it into your own working notes, then dispatch the next phase.

## Operating contract

- **One run, no handoffs.** Do not ask the user to invoke any internal skill or re-run a phase. You own the whole run.
- **Human-only blockers only.** Ask the user only for things you cannot ground from the repo or current research: missing secrets, destructive external approvals, true product ambiguity that changes correctness. If the intent skill returns with `needs-user-answer`, stop the pipeline and ask at most three numbered blocking questions.
- **Repo truth first, then targeted web research.** Read the code before you theorize. Reach for WebSearch / WebFetch when freshness matters (new APIs, recent vulns, shifting semantics) or the repo is insufficient.
- **Scope discipline.** Do only what was asked. A bug fix does not need surrounding cleanup. No speculative refactors, no "while I'm here" expansions.
- **No broken-window fixes.** Do not suppress errors, widen retries to green, mute tests, hand-wave "env issue", or special-case a failing example. Find the root cause.
- **Proof before claim.** You have not shipped anything until you ran the proof and it came back green. The verify skill's GREEN classification is the only thing that qualifies.
- **Trust Opus-class reasoning, but trust proof more.** The test suite, the live run, and the real repo are the final arbiters.

## Loopback rules

If a downstream phase rejects its predecessor, loop back explicitly:

- **Verify RED → Implement → Verify.** The verify skill returns RED with an actionable fix; dispatch the implement skill again, then re-dispatch verify. This counts as **+1 loopback**.
- **Review MUST-FIX → Implement → Verify → Review.** Same shape, triggered by review. **+1 loopback.**
- **Verify exposes a diagnosis that needs a replan → Plan → Implement → Verify.** The replan happens inside the cycle; this is still **+1 loopback**, not two.

Loopbacks that do **not** count:
- Plan-phase repair after the plan skill's own readiness gate fails. Unlimited repairs within the plan phase itself.
- `APPROVE-WITH-NOTES` from the review skill (inline tiny fixes + `fast_check` re-run).
- Verify skill classified FAILED (harness broke) rather than RED (behavior broke). Repair the harness, then re-dispatch verify.

**Cap: 2 loopbacks.** After the second loopback, stop and escalate to the user with a summary of what failed and why. Do not hand the loop back to the user before the cap is hit.

Track loopback count in your own working notes — there is no `.xlfg/phase-state.json` in v6. If you're using the harness task bridge, a `TaskCreate` with subject `xlfg: loopback N/2` is a reasonable way to surface it.

## End-of-run commit (mandatory when tracked files changed)

After the compound skill returns and before you write the user-facing summary, close the run with a commit. A run that edited product code and didn't land a commit isn't done — it's dangling in the working tree.

1. Run `git status --porcelain` once via `Bash`. Read the output yourself; don't assume.
2. **If there are no tracked changes** (porcelain is empty, or lists only `docs/xlfg/runs/` / `.xlfg/` / other gitignored paths), skip the commit. Note "no product changes to commit — investigation-only run" in the completion summary and stop.
3. **If there are tracked product changes**, commit them:
   - Stage the product paths explicitly by name — source files, tests, shipped docs, plugin manifests, CHANGELOG, READMEs. **Never `git add -A` or `git add .`.** Those would sweep in files you don't own.
   - **Never stage `docs/xlfg/runs/**` or `.xlfg/**`.** They're gitignored already, but an explicit `git add` on them would override the ignore. Run artifacts are per-run scratch, not product — confirmed by the user on 2026-04-13.
   - Create one Conventional Commits-style commit (`feat(scope): ...`, `fix(scope): ...`, `test(scope): ...`, `docs(scope): ...`, `refactor(scope): ...`, `chore(scope): ...`). Subject ≤72 chars, written in the imperative. If the body adds value, keep it short and focused on the *why*, not a diff recap.
   - Do not `git push`. Do not `--amend` a prior commit. Do not `--no-verify`. If a pre-commit hook fails, fix the underlying issue and make a new commit; never skip the hook.
   - If the run genuinely spans two unrelated concerns the user asked for in one invocation (rare — the intent skill should have caught it and split), you may create two commits. Default is one.
4. Capture the short SHA (`git rev-parse --short HEAD`) so you can cite it in the summary.

This step is the v6.3.2 repair for a regression where v6 runs finished with edits unstaged. Do not skip it, do not turn it into an ask-the-user gate, and do not collapse it into the compound skill — compound writes the archive, the conductor owns the commit.

## Completion summary (end-of-run template)

Once the commit is done (or correctly skipped), finish the run with a concise summary. Prose the user can skim in under 30 seconds:

1. **What changed.** 1–2 sentences naming the files touched and the behavior delivered.
2. **Proof.** The exact command(s) the verify skill ran and the result.
3. **Commit.** The short SHA and subject line, or "no product changes to commit — investigation-only run".
4. **Residual risk.** What you did not test, what might still be wrong, and what you'd check next if you had another hour.
5. **Follow-ups (optional).** Broken windows you spotted but did not fix, or objective groups deferred.
6. **The one durable lesson** from the compound skill, if there is one.
7. **Run archive.** The path `docs/xlfg/runs/<RUN_ID>/run-summary.md`, and whether `docs/xlfg/current-state.md` was updated.

Do not append post-hoc rationalizations, meta-commentary about the xlfg process itself, or reassurances about your own work. The summary is for the user; keep it for them.
