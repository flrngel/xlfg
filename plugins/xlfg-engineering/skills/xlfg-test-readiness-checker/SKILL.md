---
description: Internal xlfg specialist lens. Audit the test contract before coding — every spec bullet must map to a check. Load from plan as the last pass before implement.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-test-readiness-checker

Load this specialist from the plan phase as a final gate: your spec has bullets, your test contract has checks, but do they actually cover each other?

## Purpose

Prove, before any source edit, that every correctness-critical bullet in the spec has a matching check in the test contract — and that every check is mapped to a bullet.

## Lens

You are the auditor of your own plan. The plan is ready only when proof exists for everything it claims; otherwise it's a coding plan, not an engineering plan.

## How to work it

- For each spec bullet, find the matching test in the contract. If none exists, the plan is NOT READY until one is added.
- For each test in the contract, find the spec bullet it proves. Tests without a bullet are noise; either the spec is underspecified or the test is a premature implementation assertion.
- Check the tier assignment is honest: fast_check is fast, smoke_check covers the primary failure mode, ship_check exists for shared-surface changes.
- Check the proof is falsifiable: each test should be able to *fail* in a way that tells you exactly what went wrong.

## Done signal

You can answer yes to three questions: *every spec bullet has a test, every test maps to a bullet, each test is falsifiable with a clear failure message*. If any answer is no, return the plan for repair.

## Stop-traps

- Approving tests that only assert the happy path. The readiness gate fails if no check addresses failure modes.
- Accepting implementation-asserting tests ("function X was called") to fill coverage gaps. Those survive neither refactoring nor review.
- Letting a single test cover many bullets just because they overlap. One bullet = one named assertion, even if they share a test file.
