# Intent Phase

## Objective

Resolve intent before broad fan-out. Keep a single `spec.md` as the run card and source of truth.

## Required Artifact

Update `spec.md`.

## Process

- Preserve direct asks, implied asks, constraints, and non-goals separately.
- Split bundled requests into objective groups such as `O1`, `O2`, and `O3`.
- Mark resolution as `proceed`, `proceed-with-assumptions`, or `needs-user-answer`.
- Ask only questions that materially change correctness and cannot be grounded from the repo or current evidence.
- Name false-success traps so later phases do not optimize for shallow green checks.

## Done Check

`spec.md` contains an intent contract, objective groups, acceptance criteria, assumptions, and any blocking ambiguities.
