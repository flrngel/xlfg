# /xlfg-debug design notes

> **v6.5.3 update (2026-04):** The durable diagnosis artifact is `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. Earlier drafts of this document referenced a separate `spec.md`, `debug-report.md`, `repro-notes.md`, `probe-log.md`, and `history-findings.md` — none of those exist in v6. The "Single source of truth" and "New artifacts introduced by the command" sections below have been corrected to cite only `diagnosis.md`.

## Why a separate command exists

`/xlfg` is for full delivery: intent, plan, implementation, proof, review, and compounding.

`/xlfg-debug` exists for a different job: diagnose the **real failure mechanism** without touching product code. The output is not a patch. The output is an evidence-backed explanation of the deep root problem, the fake fixes to reject, and the likely repair surface.

## Non-goals

- no source-code edits
- no “green by paperwork” test edits
- no timeout inflation or retry inflation used as a fake success
- no one-example prompt band-aids
- no blaming the model, user, or environment without evidence

## Core design principles

1. **Conductor + hidden phases**
   - Keep the existing xlfg shape: one public entrypoint, hidden phases, single run state, and phase-gated completion.

2. **Diagnosis-only run shape**
   - Reuse `recall -> intent -> context`, then stop at a dedicated `debug` phase instead of flowing into plan/implement/verify/review.

3. **Single source of truth**
   - The run's durable artifact is `docs/xlfg/runs/<RUN_ID>/diagnosis.md`. That is the only file a debug run writes — no separate coordination file, no ledger, no per-phase scratch.

4. **Smallest honest reproducer first**
   - A big failing suite is not the diagnosis.
   - The command insists on a smallest honest reproducer, comparison cases, and anti-monkey probes.

5. **Mechanism over symptom**
   - “What line throws?” is not enough.
   - The output must explain the broken invariant, missing capability, or causal chain that makes the symptom appear.

6. **Prompt-aware debugging**
   - For prompt and agent issues, the prompt, tool contract, context selection, evaluation bar, and false-success trap are all first-class debug surfaces.

## External inspiration that shaped the design

### Skill-native and prompt-pack ecosystems

The add-only command shape, narrow specialist lanes, and hidden helper pattern fit the skill-pack direction seen across:

- `openclaw`
- `everything-claude-code`
- `awesome-claude-skills`
- `obsidian-skills`
- `ui-ux-pro-max-skill`
- `marketingskills`
- `oh-my-codex`

### Workflow orchestration and harness-first systems

The diagnosis run keeps explicit workflow state, artifacts, and human-readable outputs instead of relying on one long implicit chat turn. That is aligned with ideas surfaced by:

- `symphony`
- `humanlayer`
- `OpenHarness`
- `ruflo`
- `nanobot`
- `oh-my-agent`
- `oh-my-openagent`
- `hermes-agent`

### Context mapping and structural understanding

The debug phase insists on repo mapping, bounded context, and causal structure before solutioning. That direction was reinforced by:

- `serena`
- `graphify`
- `Understand-Anything`
- `openclaw` / `acpx`

### Operator surfaces and state visibility

The explicit diagnosis artifact, workboard clarity, and no-silent-success posture match lessons visible in operator-facing projects such as:

- `cherry-studio`
- `AionUi`
- `happy`
- `CodexBar`
- `cmux`
- `cc-switch`

### Protocols, bridges, and edge adapters

These repos helped keep transport / gateway / integration bugs in scope as real root-cause surfaces rather than afterthoughts:

- `CLIProxyAPI`
- `sub2api`
- `alphaclaw`
- `desloppify`
- `superset`

## Debugging method built into the phase

The debug phase encodes a compact version of scientific debugging:

1. state the expected correct behavior
2. verify the failure is real
3. create the smallest honest reproducer
4. simplify the setup until irrelevant variables disappear
5. compare failing vs passing inputs, states, prompts, or commits
6. form falsifiable hypotheses and try to disprove them
7. trace the first wrong state rather than stopping at the crash site
8. use history search, bisect, trace replay, or targeted instrumentation when they shorten origin search
9. ask “why” until the broken invariant or missing capability is explicit

## New artifacts introduced by the command

- `docs/xlfg/runs/<RUN_ID>/diagnosis.md` — the only file written by a `/xlfg-debug` run. Surfaced by future recall passes. No sibling artifacts.

## Why this stays add-only

The implementation adds a new public entrypoint and a new hidden phase.

It does **not** alter the existing `/xlfg` implementation path, which keeps the feature low-risk and easy to evaluate side-by-side.
