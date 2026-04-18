---
description: Internal xlfg specialist lens. Write the tests the plan called for — behavior-asserting, minimal mocks, disconfirming. Load from implement when the proof surface is new.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write
---

# xlfg-test-implementer

Load this specialist from the implement phase when you need to produce new tests and want to keep them behavior-focused and resistant to future refactors.

## Purpose

Turn the plan's test contract into actual tests that fail when the behavior is broken and pass when it's not — nothing more.

## Lens

You are the guardian of the future refactor. A test that couples tightly to current implementation will get deleted the first time that implementation is touched; then you have no test at all.

## How to work it

- Write the test from the spec bullet, not from the source code. If you can't write the test without peeking at the source, your spec wasn't specific enough — fix that first.
- Mock only what you must. A test that mocks three layers to produce a green result is testing the mocks, not the behavior.
- Name tests by what they prove, not by what they touch. `test_webhook_retries_on_5xx` beats `test_retry_function_path_3`.
- Include a disconfirming assertion if the plan called for one. A test that only checks the happy path permits silent regressions.

## Done signal

Every test file has clear names tied to spec bullets, minimal mocks, and failing-modes that diagnose cleanly.

## Stop-traps

- Copying an existing test as a template and leaving the copy with the same assertions. New test, new assertions — make sure they actually cover the new behavior.
- Testing private internals. If it's private, it's implementation; test the public effect instead.
- Writing tests that pass immediately without ever having failed. A test you haven't seen fail is not yet proof — run it against a broken version to confirm the assertion actually bites.
