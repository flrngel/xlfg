---
name: xlfg-debug
description: Run xlfg's diagnosis-only workflow in Codex: recall, resolve intent, gather context, and produce an evidence-backed root-cause report without source edits.
---

# xlfg-debug

Use this skill only when the user explicitly invokes `$xlfg-debug` or asks for an xlfg diagnosis run in Codex.

Treat the invocation as one autonomous diagnosis run. Do not edit product source, tests, fixtures, migrations, or configs. Only write run artifacts, evidence logs, and scratch notes under `docs/xlfg/runs/<RUN_ID>/` and `.xlfg/runs/<RUN_ID>/`.

## Invocation

- Public Codex invocation: `$xlfg-debug "what is broken"`
- Plugin-scoped invocation may also be used by the client when needed: `@xlfg-engineering $xlfg-debug`
- Do not promise slash-command parity in Codex. This surface is a Codex skill.

## Run Contract

- Create `RUN_ID` as `<YYYYMMDD>-<HHMMSS>-<slug>`.
- Create `docs/xlfg/runs/<RUN_ID>/`, `.xlfg/runs/<RUN_ID>/`, `docs/xlfg/knowledge/`, and `.xlfg/` when missing.
- Seed the core run files: `context.md`, `memory-recall.md`, `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`.
- Keep a single `spec.md` as the source of truth for intent, objective groups, diagnosis, likely repair surface, and proof status.
- Run deterministic recall first, then resolve intent before broad fan-out.
- Find the smallest honest reproducer, compare failing and passing cases, trace the first wrong state, and keep falsifiable hypotheses.
- Record verification evidence for every claim. A green command without a stable explanation is not a diagnosis.

## Phase State

Write `.xlfg/phase-state.json` after startup:

```json
{
  "run_id": "<RUN_ID>",
  "phases": ["recall", "intent", "context", "debug"],
  "completed": [],
  "loopback_count": 0,
  "max_loopbacks": 1,
  "block_count": 0
}
```

After each phase completes, append its phase name to `completed`, reset `block_count` to `0`, and update the `## Phase status` block in `workboard.md`. This Codex v1 surface uses a prompt-level barrier: do not finish while phases remain incomplete unless the run is explicitly `BLOCKED` or `FAILED` in `spec.md` and `workboard.md`.

## Phase References

Load only the current phase reference from `../../references/phases/` as needed:

1. `recall.md`
2. `intent.md`
3. `context.md`
4. `debug.md`

## Specialist Work

Invoking `$xlfg-debug` is an explicit request to use bounded Codex subagents where the runtime supports them; if subagents are unavailable, the conductor performs the lane inline and records that fallback in `workboard.md`.

Use a specialist only for a bounded diagnostic lane with one required artifact. Before starting specialist work, preseed the artifact with YAML frontmatter:

```yaml
---
status: IN_PROGRESS
---
```

Dispatch or perform the lane with this packet shape:

```text
PRIMARY_ARTIFACT: <exact path>
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only
```

A lane is complete only when the artifact exists, has `status: DONE`, `status: BLOCKED`, or `status: FAILED`, and contains concrete findings, checks, logs, reproduction steps, or cited facts. Progress notes are not completion.

## Loop Rules

- If intent is `needs-user-answer`, stop before context gathering and ask only the blocking questions.
- If the debug phase has a plausible explanation but weak evidence, return once to context, then rerun debug.
- Cap diagnosis re-context loopbacks at 1.
- Keep repair ideas as likely repair surfaces only. Do not move into implementation.

## Completion

Finish with `RUN_ID`, the deep root problem, strongest evidence, likely repair surface, fake fixes rejected, the no-code-change guarantee, residual unknowns, and the next safest proof step.
