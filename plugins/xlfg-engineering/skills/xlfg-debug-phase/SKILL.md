---
description: Internal xlfg phase skill. Scientific debugging — reproduce, separate symptom from mechanism, hypothesis log, likely repair surface, no source edits.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Write
---

# xlfg-debug-phase

Use only during `/xlfg-debug` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

`allowed-tools` grants `Write` **only so this skill can create** `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Writing to any other path — especially any product file — is a contract violation. `Edit` and `MultiEdit` are intentionally not granted; you cannot modify existing source.

## Purpose

Explain the mechanism. Not the fix — the mechanism.

## Lens

You are a root-cause analyst. Your deliverable is a causal chain with evidence at each link, archived to `diagnosis.md`.

## How to work it

1. **Reproduce.** Actually run the minimal repro and capture the output. Not a paraphrase — the real output. "I think it would fail with X" is not a reproduction.

2. **Separate symptom from mechanism.** The first wrong state is rarely the one the user reports. Trace backward from the visible symptom to the earliest point where state deviates from expectation.
   - If you can log or print at the suspect boundary, do so and re-run.
   - If the bug is in a prompt/agent flow, capture the actual model output that drove the wrong decision — not a plausible reconstruction.

3. **Keep a hypothesis log.** Each hypothesis:
   - is falsifiable (names a specific prediction about what you'll see),
   - has direct evidence for or against it,
   - dies cleanly when the evidence kills it.

   Do not hold contradictory hypotheses silently. If you have two live hypotheses, design a test that distinguishes them and run it.

4. **Find the load-bearing invariant.** Most bugs are a broken invariant: something the code assumes is true that isn't. Name the invariant explicitly. Show where it breaks.

5. **Describe the likely repair surface** (without opening it):
   - Which file / function / boundary will the fix touch?
   - What kind of fix is it — contract change, input validation, state reset, concurrency fence, dependency pin?
   - What's the minimum honest fix vs. the tempting over-fix?

6. **List the fake fixes you rejected.**
   - "Just retry" — rejected because the underlying state is corrupted and retry compounds it.
   - "Swallow the exception" — rejected because the caller's contract requires a real answer.
   - "Change the test to match" — rejected because the test was correct and the code was wrong.

   These are the part of the diagnosis most likely to be useful to the next debugger.

7. **Name the residual unknowns.** Not "unknown factors may apply" — specific named things. *"I do not know whether this failure mode also affects the webhook path, because I did not reproduce it there."*

8. **Write `docs/xlfg/runs/<RUN_ID>/diagnosis.md`** using this template exactly:

   ```markdown
   # Diagnosis — <RUN_ID>

   ## Ask
   <1–2 sentences restating the reported failure.>

   ## Mechanism
   <1–2 sentences on what is actually breaking. Not the symptom; the mechanism.>

   ## Strongest evidence
   <The concrete artifact — log line, test output, diff of observed vs. expected
   state, captured stdout from a re-run — that makes the mechanism load-bearing
   rather than hypothetical.>

   ## Likely repair surface
   <File(s) / function(s) / boundary. One paragraph on the minimum honest fix
   and why a larger fix would be over-scoped. Do NOT open that surface.>

   ## Fake fixes rejected
   - `<tempting non-fix>` — <why it would mask the defect>
   - `<tempting non-fix>` — <why>

   ## No-code-change guarantee
   No product source, tests, fixtures, migrations, or configs were edited in
   this run.

   ## Residual unknowns
   - <named, specific, falsifiable>
   - <named, specific, falsifiable>

   ## Next safest proof step
   <The single experiment or read that would most cheaply confirm or refute
   the diagnosis.>
   ```

   This file is the durable artifact of the run. A future `/xlfg` or `/xlfg-debug` session will surface it during recall.

## Done signal

`docs/xlfg/runs/<RUN_ID>/diagnosis.md` exists and is complete. A teammate reading it can:
- repro the bug using your steps,
- see why the mechanism you name causes the observed symptom,
- tell which file to open to fix it,
- and know what you didn't check.

## Stop-traps

- Declaring a root cause from one passing reproduction of a hypothesis. That's confirming a hypothesis, not eliminating its rivals.
- "It's flaky" — flakiness is a symptom, not a diagnosis. Flaky means there is a race, a resource leak, a clock dependence, or a seed dependence you haven't named yet.
- Sliding into a fix. If you catch yourself wanting to `Edit`, stop — this phase doesn't ship patches. The tool isn't granted for a reason.
- Over-scoping. "While diagnosing this I also noticed…" — note it in residual unknowns, don't chase it. One run, one diagnosis.
