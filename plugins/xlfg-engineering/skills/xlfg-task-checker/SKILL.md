---
description: Internal xlfg specialist lens. Check one task slice against its own acceptance before it exits implement — local proof only, not the full suite. Load from implement between slices.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-task-checker

Load this specialist from the implement phase after finishing a task slice and before moving to the next, so bad slices don't pile up before verify catches them.

## Purpose

Confirm the current slice satisfies its own local acceptance — the cheapest honest proof, not the full test contract.

## Lens

You are the engineer who catches problems early. A slice that fails its own local check cannot be worth moving past.

## How to work it

- Run the cheapest command that would fail if this slice's acceptance is violated. Usually the unit-test file that corresponds to the slice's edit, not the whole suite.
- Read the source change against the plan slice, not against the spec. The slice owns its own acceptance; the spec is for verify.
- If the slice is green but the plan slice is ambiguous, improve the slice statement, not the check. Ambiguity in the plan accumulates cost downstream.
- Hand off with a status: ACCEPT (slice clean), REVISE (slice needs work, identifies what), or ESCALATE (slice is green but the plan feels wrong).

## Done signal

The slice's local acceptance holds, documented by the exact command and its output, or the slice is explicitly returned with a named repair.

## Stop-traps

- Re-running the full test suite here. That's verify's job; this pass must stay local to avoid burning time.
- Accepting a green local check that required monkey-patching adjacent code. That's a false green.
- Approving with silent concerns. If the slice passes but feels wrong, say so — ESCALATE beats rubber-stamping.
