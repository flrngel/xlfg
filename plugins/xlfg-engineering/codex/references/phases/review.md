# Review Phase

## Objective

Confirm quality after verification. Review does not create quality; it checks for missed correctness, security, performance, UX, maintainability, and proof risks.

## Required Artifact

Write `review-summary.md` when review changes a decision, records residual risk, or finds a must-fix issue.

## Process

- Start from the diff, `spec.md`, `verification.md`, and objective groups.
- Pick the smallest useful review surface: usually one lens, up to two when risk warrants it.
- Lead with concrete findings tied to files and behavior.
- If a must-fix issue exists, return to implementation, then rerun verification and review.
- If no must-fix issue exists, record residual risk honestly.

## Done Check

Review either records no must-fix findings with residual risk, or sends the run back to implementation with a precise finding.
