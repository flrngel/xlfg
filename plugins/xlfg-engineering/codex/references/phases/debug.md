# Debug Phase

## Objective

Produce an evidence-backed root-cause report and likely repair surface without source edits.

## Required Artifact

Write `debug-report.md`.

## Process

- Find the smallest honest reproducer.
- Compare failing vs passing cases.
- Trace the first wrong state.
- Keep falsifiable hypotheses and retire them with evidence.
- Reject fake fixes such as muting errors, widening timeouts, changing tests to green, or calling an unexplained failure an environment issue.
- Record verification evidence for the diagnosis, not just command output.

## Done Check

`debug-report.md` names the deep root problem, strongest evidence, fake fixes rejected, likely repair surface, residual unknowns, and next safest proof step.
