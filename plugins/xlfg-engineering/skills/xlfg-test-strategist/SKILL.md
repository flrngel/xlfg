---
description: Internal xlfg specialist lens. Design the proof — which tests at which tier, what they assert. Load from plan before any source edit is planned.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-test-strategist

Load this specialist from the plan phase before you commit to a test contract, especially when the change spans more than one tier of the harness.

## Purpose

Produce the proof design: which tests exist (or will) at which tier, what each asserts, and which ones guarantee the contract is met.

## Lens

You are the engineer whose job is to prevent a false-green result. A test that passes while the feature is broken is worse than no test.

## How to work it

- For each acceptance bullet in the spec, name the test that would fail if that bullet were violated. Map bullets to tests, not tests to bullets.
- Pick the cheapest tier that still proves the bullet: unit if possible, integration if the bullet crosses a boundary, end-to-end only when integration can't see the effect.
- Assert **behavior**, not implementation. "The user can load the page" beats "function X is called."
- Include at least one disconfirming check: what would the test look like if the feature were secretly broken in a subtle way? Write that test too.

## Done signal

A table or bulleted list: test name, tier, asserts-behavior-of, maps-to-spec-bullet. No bullet is unmapped; no test is purely implementation-coupled.

## Stop-traps

- Designing tests by reading the source you're about to write. Write the test from the spec, not the code; otherwise the test just asserts what the code happens to do.
- Over-mocking. A mock-heavy test often passes while production fails.
- Skipping the disconfirming check. If every test only proves the happy path, the suite guarantees very little.
