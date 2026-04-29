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

After any phase (skill or agent) returns, your very next tool call is the dispatch for the next phase in the pipeline. Not a progress note, not a user-facing confirmation, not a pause for review — the next `Skill` or `Agent` call, in the same turn.

A phase's `## Done signal` (skills) or `## Return format` (agents) means *that phase* finished its work and handed you its conclusion. It does not mean the run ended. The run ends only after phase 8 (compound) returns and you've executed the end-of-run commit step and written the completion summary.

The only valid mid-run turn boundaries are:

- The intent skill returns with `needs-user-answer` → ask at most three blocking questions using the §Question template below and stop.
- Loopback cap hit → escalate to the user with a summary of what failed.
- Phase 8 (compound) returned → run the end-of-run commit step, then write the completion summary. This is the sole end-of-run exit.

**Anti-pattern to avoid:** outputting a natural-sounding transition like *"Plan is READY. Proceeding to implement."*, *"Context gathered, moving to plan."*, *"Verify GREEN, moving to review."*, or *"Review APPROVE, moving to compound."* and then ending the turn. "Proceeding", "moving", "next up" all describe your *next action* — that action must be the tool call you just described, not an end-of-turn. If you wrote a transition sentence, the very next thing you emit must be the dispatch. Better still: dispatch without the transition sentence.

Do not wait for the user to say "continue", "ok", or anything else to resume between phases. The user invoked `/xlfg` once; that is your authorization for the whole run.

## Operating contract

- **One run, one conductor turn.** All 8 dispatches + the end-of-run commit + the completion summary happen in a single continuous conductor turn. Do not end your turn between phases. Do not ask the user to invoke any internal skill, agent, or re-run a phase. You own the whole run.
- **Human-only blockers only.** Ask the user only for things you cannot ground from the repo or current research: missing secrets, destructive external approvals, true product ambiguity that changes correctness. If the intent skill returns with `needs-user-answer`, stop the pipeline and ask at most three blocking questions using the §Question template.
- **Repo truth first, then targeted web research.** Read the code before you theorize. Reach for WebSearch / WebFetch when freshness matters (new APIs, recent vulns, shifting semantics) or the repo is insufficient.
- **Scope discipline.** Do only what was asked. A bug fix does not need surrounding cleanup. No speculative refactors, no "while I'm here" expansions.
- **No broken-window fixes.** Do not suppress errors, widen retries to green, mute tests, hand-wave "env issue", or special-case a failing example. Find the root cause.
- **Proof before claim.** You have not shipped anything until verify came back GREEN. The verify agent's GREEN classification is the only thing that qualifies.
- **Trust Opus-class reasoning, but trust proof more.** The test suite, the live run, and the real repo are the final arbiters.

## Question template (intent halt only)

When the intent skill returns `needs-user-answer`, stop the pipeline and emit the questions in exactly this shape — no opening framing, no closing prose:

```
Need <n> answers:

1. <≤80-char question>  [A) <option>  B) <option>]
2. <≤80-char question>

Blocking: <≤80-char reason — what breaks if I guess wrong>
```

Hard rules:

- **≤80 chars per question.** One clause. No compound sentences.
- **Always offer A/B/C options when the answer space is finite** (binary, enum, short list). The user types `1A 2B`. Skip brackets only when the answer is genuinely free-form.
- **One `Blocking:` footer** covers all questions. Not one per question.
- **No opening line.** No "To make sure I build the right thing…", no "I have a few clarifying questions…". The `Need <n> answers:` lead is the entire preamble.
- **n ≤ 3.**

Target: ≤6 lines for 2 questions, ≤9 for 3.

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

Once the commit is done (or correctly skipped), finish the run with a markdown table. The full record is in `run-summary.md`; chat output is a pointer, not the document. Use exactly this shape:

```
|         |                                          |
|---------|------------------------------------------|
| Shipped | <one short clause, ≤80 chars>            |
| Proof   | <command> → GREEN                        |
| Commit  | <short SHA> <subject>                    |
| Archive | docs/xlfg/runs/<RUN_ID>/run-summary.md   |
```

Optional rows `Risk` and `Next` are inserted **only when there is something concrete to say**; otherwise the row is omitted entirely. Do not write `Risk: none` or `Next: n/a`.

Hard rules — these are not suggestions:

- **≤80 chars per cell.** One short clause. If detail does not fit in 80 chars, the cell says `see archive` and the user opens `run-summary.md` for the full version.
- **One clause per cell. No compound sentences.** No semicolons. No em-dash splitting one cell into two ideas. No nested parentheticals. If you have two things to say, you have two rows or one of them goes to the archive.
- **No `Files` row.** `git show <sha>` and `run-summary.md` both list files. Repeating them in the terminal is noise.
- **No durable-lesson row.** The compound skill writes the lesson into `run-summary.md`. The terminal does not repeat it.
- **No closing prose.** No "let me know if…", no recap of the xlfg process, no reassurance about your own work. The table is the message.

Variants (each is a single line that replaces the whole table):

- **Investigation-only** (commit was correctly skipped): `No product changes. <one short clause>. Archive: docs/xlfg/runs/<RUN_ID>/run-summary.md`
- **Loopback escalation** (cap hit before GREEN): `Stopped after 2 loopbacks. <command> failed: <one short clause>. Archive: docs/xlfg/runs/<RUN_ID>/run-summary.md`

Target: ≤8 lines on screen for the success case. User reads it in 3 seconds and opens the archive only if they want detail.
