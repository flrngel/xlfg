# Verify Phase

## Objective

Run layered proof for the changed behavior and reduce results into explicit pass/fail evidence.

## Required Artifact

Write `verification.md`.

## Process

- Run the scenario proof named in `test-contract.md`.
- Run supporting checks only when they add confidence for touched behavior.
- Capture command names, outcomes, and meaningful excerpts without dumping noisy logs.
- Mark failures RED when they are actionable and name the first repair surface.
- Do not rely on a generic green suite when the changed scenario was not exercised.

## Done Check

`verification.md` contains verification evidence for each objective and states PASS, RED, BLOCKED, or FAILED.
