# Implement Phase

## Objective

Implement the planned change without drifting from `spec.md`, while keeping tests and run artifacts truthful.

## Required Artifacts

Update source/test files as needed, plus `workboard.md` and `spec.md` proof/task sections.

## Process

- Work task by task from `workboard.md`.
- Keep edits scoped to the files and behavior named in the plan.
- Add or update tests in proportion to risk and public behavior.
- Preserve user changes and unrelated repo state.
- Use bounded Codex subagents only when a lane has one artifact, one file scope, and one done check.
- If subagents are unavailable, perform the lane inline and record the fallback in `workboard.md`.
- Keep source, test, and checker ownership separate. Source implementers do not duplicate test lanes when one exists; test implementers do not rewrite product source; checkers do not rerun full verification.

## Done Check

Planned implementation tasks are complete or honestly blocked, and `workboard.md` reflects the actual state of each objective.
