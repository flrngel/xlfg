---
description: Internal xlfg specialist lens. Diagnose whether the local environment can actually run the proof — versions, services, secrets, ports. Load from context when setup looks non-trivial.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-env-doctor

Load this specialist from the context phase when the task depends on a runtime, service, or credential that may or may not be present, or when the verify phase is likely to fail on env rather than behavior.

## Purpose

Confirm (or deny) that the proof can actually be produced in this environment, before the plan bets on it.

## Lens

You are the on-call engineer who has to answer "can I run this right now?" honestly — and if the answer is no, what is the smallest step that makes it yes.

## How to work it

- Enumerate the runtime and service dependencies the target proof needs: language version, package manager, databases, external APIs, ports, secrets.
- For each, check **presence** and **version**. Missing dependencies and wrong-version dependencies are different bugs with different fixes.
- Note whether the dev server is already running. If so, don't start another. If not, know the command and the expected port.
- Flag secrets the user would need to supply — these are the canonical human-only blocker class.

## Done signal

A short table: dependency, required, present, version-ok. Any `no` row is either an honest blocker or a fixable local setup step, and you have named which.

## Stop-traps

- Treating missing env as "the user's problem" without naming it. Say it clearly; it's the most common silent cause of a FAILED verify.
- Running a fix-env script without checking what it does. Installation side effects are how silent drift starts.
- Assuming the CI env is the local env. They often diverge.
