---
name: xlfg
description: Autonomous proof-first SDLC run. Dispatches 4 phase skills (intent, plan, implement, compound) and 4 phase agents (recall, context, verify, review) in order.
argument-hint: "[feature, bugfix, investigation, or delivery request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, WebSearch, WebFetch, TaskCreate, TaskUpdate, TaskList, Agent, Skill(xlfg-engineering:xlfg-intent-phase *), Skill(xlfg-engineering:xlfg-plan-phase *), Skill(xlfg-engineering:xlfg-implement-phase *), Skill(xlfg-engineering:xlfg-compound-phase *)
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

Treat this invocation as **one autonomous run** split across 8 phases. You are the conductor. The pipeline mixes two dispatch mechanisms:

- **Phase skills** (intent, plan, implement, compound) load just-in-time via the `Skill` tool and run in your own context. They drive decisions; you need their full reasoning to brief the next step.
- **Phase agents** (recall, context, verify, review) dispatch via the `Agent` tool and run in their own sub-contexts. They explore heavily and return a distilled synthesis via a mandatory `## Return format` section. You receive the conclusion, not the tool-call log.

Do not try to hold every phase body in context simultaneously — that's exactly what this split is designed to prevent.

## What xlfg is (and isn't) in this version

xlfg v6.5 is a **conductor-plus-phase-skills-and-agents architecture**. The 4 decision-driving phases are skills under `plugins/xlfg-engineering/skills/xlfg-*-phase/`; the 4 exploration-heavy phases are agents under `plugins/xlfg-engineering/agents/`. This conductor dispatches both in one canonical pipeline order. There is **no v5 coordination layer** — no `spec.md`, `workboard.md`, `phase-state.json`, `verification.md`, or `test-contract.md` files. The run lives in your context plus the 4 agent sub-contexts, and in the real repo.

The durable archive convention stays:

- `docs/xlfg/current-state.md` — optional, tracked, one-page living summary of the project's load-bearing truths. Read by the recall phase-agent. Updated sparingly by the compound skill when a run earns promotion.
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

## Batch pipeline

Dispatch these 8 phases in this exact order. The mechanism differs per phase:

1. **Agent: `xlfg-recall`** — dispatch via the `Agent` tool with `subagent_type: "xlfg-recall"`.
2. **Skill: `xlfg-engineering:xlfg-intent-phase`** — load via the `Skill` tool.
3. **Agent: `xlfg-context`** — dispatch via the `Agent` tool with `subagent_type: "xlfg-context"`.
4. **Skill: `xlfg-engineering:xlfg-plan-phase`** — load via the `Skill` tool.
5. **Skill: `xlfg-engineering:xlfg-implement-phase`** — load via the `Skill` tool.
6. **Agent: `xlfg-verify`** — dispatch via the `Agent` tool with `subagent_type: "xlfg-verify"`.
7. **Agent: `xlfg-review`** — dispatch via the `Agent` tool with `subagent_type: "xlfg-review"`.
8. **Skill: `xlfg-engineering:xlfg-compound-phase`** — load via the `Skill` tool.

Skill phases load just-in-time from their `SKILL.md` body — do NOT inline skill instructions from memory. Agent phases run in their own sub-contexts; you cannot load their bodies into your own context. Brief each agent with a self-contained prompt (see §Briefing agents) and read only its `## Return format` block from the returned message.

## Briefing agents

Each of the 4 agent dispatches needs a hand-written brief. Do not paste `$ARGUMENTS` raw — synthesize from what you already know. A good brief includes:

- `RUN_ID`
- The user's resolved ask (after intent, for context/verify/review; the raw ask for recall)
- The prior-phase synthesis the agent actually needs (recall's output for context; plan's proof contract for verify; implement's file list + verify's evidence for review)
- Any loopback reason, if this is a re-dispatch

Example for `xlfg-context` dispatch (schematic — adapt to the real run):

```
Agent(
  subagent_type: "xlfg-context",
  description: "Context phase",
  prompt: "RUN_ID: <id>\nUser ask (resolved): <intent synthesis>\nRecall synthesis: <recall result>\n\nGather the context needed to plan a change that satisfies the above. Focus surfaces on what the plan will need to touch, not the whole repo.\n\nReturn in the CONTEXT MAP format declared in your agent body."
)
```

You read the agent's final message, which must match its declared Return format. Summarize into your own working notes and dispatch the next phase.

## Between phases

After ANY phase returns, your VERY NEXT tool call MUST be the dispatch for the next phase. NOT a progress note. NOT a confirmation. NOT a pause. The next `Skill` or `Agent` call, in the SAME turn.

The ONLY valid mid-run turn boundaries are exactly three:

1. **Intent skill returned `needs-user-answer`** → emit the question template below, stop. NEVER halt for any other reason — uncertainty mid-pipeline, ambiguous evidence, "feeling stuck" are NOT triggers.
2. **Loopback cap (2) hit** → escalate with one-line failure summary, stop.
3. **Phase 8 (compound) returned** → run the end-of-run commit step, then emit the completion summary. SOLE end-of-run exit.

**Question template — fires ONLY on (1) above.**

```
Need <n> answers:

1. <≤80-char question>  [A) <option>  B) <option>]
2. <≤80-char question>

Blocking: <≤80-char reason>
```

n ≤ 3. One clause per question. Options when answer space is finite. No preamble, no closing prose.

**NEVER** end the turn between phases. **NEVER** write a transition sentence ("Plan is READY. Proceeding to implement.", "Context gathered, moving to plan.", "Verify GREEN, moving to review.") and then stop. If you wrote a transition, the very next thing you emit MUST be the tool call.

**NEVER** wait for the user to say "continue" / "ok" / anything else. The user invoked `/xlfg` ONCE; that authorizes the WHOLE run.

## Operating contract

- **One run, one conductor turn.** All 8 dispatches + end-of-run commit + completion summary happen in ONE continuous turn. NEVER end the turn between phases. NEVER ask the user to invoke any internal skill or re-run a phase.
- **Human-only blockers only.** Ask ONLY for things you cannot ground from repo or current research: missing secrets, destructive external approvals, correctness-changing ambiguity. The ONLY trigger is intent returning `needs-user-answer`.
- **Repo truth first, then targeted web research.** Read code before theorizing. Reach for WebSearch / WebFetch only when freshness matters or the repo is insufficient.
- **Scope discipline.** Do ONLY what was asked. NO speculative refactors. NO "while I'm here" expansions.
- **No broken-window fixes.** NEVER suppress errors, widen retries to green, mute tests, or special-case a failure. Find the root cause.
- **Proof before claim.** Nothing is shipped until verify returned GREEN. The verify agent's GREEN classification is the ONLY thing that qualifies.
- **Trust Opus-class reasoning, but trust proof more.** Test suite, live run, real repo are the final arbiters.

## Loopback rules

If a downstream phase rejects its predecessor, loop back explicitly:

- **Verify RED → Implement → Verify.** The verify agent returns RED with an actionable fix; dispatch the implement skill again, then re-dispatch the verify agent. This counts as **+1 loopback**.
- **Review MUST-FIX → Implement → Verify → Review.** Same shape, triggered by the review agent. **+1 loopback.**
- **Verify exposes a diagnosis that needs a replan → Plan → Implement → Verify.** The replan happens inside the cycle; this is still **+1 loopback**, not two.

Loopbacks that do **not** count:
- Plan-phase repair after the plan skill's own readiness gate fails. Unlimited repairs within the plan phase itself.
- `APPROVE-WITH-NOTES` from the review agent (inline tiny fixes + `fast_check` re-run).
- Verify agent classified FAILED (harness broke) rather than RED (behavior broke). Repair the harness, then re-dispatch verify.

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

Emitted ONLY after the end-of-run commit step. Full record lives in `run-summary.md`; chat output is a pointer.

```
Shipped:
- <≤80-char clause>

Proof:
- <command> → GREEN

Commit:
- <short SHA> <subject>

Archive:
- docs/xlfg/runs/<RUN_ID>/run-summary.md
```

Add `Risk:` and/or `Next:` sections (same shape) ONLY when concrete content exists. Omit otherwise — NEVER write `Risk:\n- none`.

Rules:

- ≤80 chars per bullet, one clause. NEVER compound sentences, semicolons, em-dash splits, or nested parentheticals. `- see archive` if longer.
- `Label:` ALWAYS on its own line. NEVER `Label: value` inline. Always `Label:\n- value`.
- Blank line between sections.
- Bullets only. NO tables, NO prose paragraphs, NO `Files` section, NO durable-lesson section, NO closing prose.

Variants (single line, replaces the whole block):

- Investigation-only: `No product changes. <one clause>. Archive: docs/xlfg/runs/<RUN_ID>/run-summary.md`
- Loopback escalation: `Stopped after 2 loopbacks. <command> failed: <one clause>. Archive: docs/xlfg/runs/<RUN_ID>/run-summary.md`
