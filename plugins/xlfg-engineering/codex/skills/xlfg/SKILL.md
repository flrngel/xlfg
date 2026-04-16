---
name: xlfg
description: Run xlfg's proof-first SDLC workflow in Codex: resolve intent, plan, implement, verify, review, and compound with file-backed artifacts.
---

# xlfg

Use this skill only when the user explicitly invokes `$xlfg` or asks for an xlfg SDLC run in Codex.

Treat the invocation as one autonomous run. Do not ask the user to run internal phases. Keep the repo as the system of record and keep the final answer short.

## Invocation

- Public Codex invocation: `$xlfg "what you want built"`
- Plugin-scoped invocation may also be used by the client when needed: `@xlfg-engineering $xlfg`
- Do not promise slash-command parity in Codex. This surface is a Codex skill.

## Run Contract

- Create `RUN_ID` as `<YYYYMMDD>-<HHMMSS>-<slug>`.
- Create `docs/xlfg/runs/<RUN_ID>/`, `.xlfg/runs/<RUN_ID>/`, `docs/xlfg/knowledge/`, and `.xlfg/` when missing.
- Seed the core run files: `context.md`, `memory-recall.md`, `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`.
- Keep a single `spec.md` as the source of truth for intent, objective groups, chosen solution, task map, and proof summary.
- Run deterministic recall first, then resolve intent before broad fan-out.
- Require `test-readiness.md = READY` before implementation.
- Verify with scenario proof and record verification evidence before review or success claims.
- Optional files exist only when they change a decision, proof obligation, or durable lesson.

## Phase State

Write `.xlfg/phase-state.json` after startup:

```json
{
  "run_id": "<RUN_ID>",
  "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
  "completed": [],
  "loopback_count": 0,
  "max_loopbacks": 2,
  "block_count": 0
}
```

After each phase completes, append its phase name to `completed`, reset `block_count` to `0`, and update the `## Phase status` block in `workboard.md`. This Codex v1 surface uses a prompt-level barrier: do not finish while phases remain incomplete unless the run is explicitly `BLOCKED` or `FAILED` in `spec.md` and `workboard.md`.

## Phase References

Load only the current phase reference from `../../references/phases/` as needed:

1. `recall.md`
2. `intent.md`
3. `context.md`
4. `plan.md`
5. `implement.md`
6. `verify.md`
7. `review.md`
8. `compound.md`

## Specialist Work

Invoking `$xlfg` is an explicit request to use bounded Codex subagents where the runtime supports them; if subagents are unavailable, the conductor performs the lane inline and records that fallback in `workboard.md`.

Use a specialist only for a bounded lane with one required artifact. Before starting specialist work, preseed the artifact with YAML frontmatter:

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

A lane is complete only when the artifact exists, has `status: DONE`, `status: BLOCKED`, or `status: FAILED`, and contains concrete edits, findings, checks, logs, or cited facts. Progress notes are not completion.

## Loop Rules

- If intent is `needs-user-answer`, stop before context gathering and ask only the blocking questions.
- If `test-readiness.md` is not `READY`, repair context and planning before implementation.
- If verification is RED with an actionable fix, return to implementation, then rerun verification. Cap verify-fix and review-fix loopbacks at 2.
- If review finds a must-fix issue, return to implementation, then rerun verification and review.

## Completion

Finish with `RUN_ID`, what changed, objective status, proof status, residual risk, and follow-ups. Do not claim success unless verification evidence exists for the scenario proof.
