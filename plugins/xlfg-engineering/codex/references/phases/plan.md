# Plan Phase

## Objective

Turn intent plus context into a lean run card, task map, and proof contract. Implementation may not begin until `test-readiness.md = READY`.

## Required Artifacts

Update `spec.md`, `test-contract.md`, `test-readiness.md`, and `workboard.md`.

## Process

- Choose the smallest architecture that satisfies the objective groups.
- Define scenario proof for changed behavior, not just generic checks.
- Map each task to objectives, files, expected artifacts, and a done check.
- Mark `test-readiness.md` as `READY` only when proof is practical, targeted, and executable.
- If proof is not ready, repair context or planning before implementation.
- Keep lane ownership explicit: diagnosis owns cause, solution owns option choice, flow/UI own behavior/design contracts, test strategy owns proof commands, readiness owns only the gate verdict, and task division owns task packets.

## Done Check

`test-readiness.md` is `READY`, `test-contract.md` names scenario proof, and `workboard.md` has executable tasks tied to objectives.
