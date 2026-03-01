# Philosophy

xlfg is built around a few non-negotiable ideas.

## 1) Define the behavior before the code

The fastest way to waste time is to implement first and decide the real user flow later.

xlfg requires a shared `flow-spec.md` before implementation starts. For user-facing work, this means explicit steps, alternates, failure states, and accessibility expectations.

## 2) Define the test contract before the test runner

"Run the tests" is not a strategy.

xlfg requires a `test-contract.md` that says:

- which scenarios are **new behavior** (Fail → Pass)
- which suites preserve **existing behavior** (Pass → Pass)
- which checks are the **fastest relevant loop**
- which flows truly deserve real e2e coverage

## 3) Environment failures are productively learnable

Repeated `yarn dev`, stale servers, watch-mode hangs, and port conflicts are not just noise.

They are operational failure modes that should be compounded into `failure-memory.md` and `harness-rules.md` so the next run gets better.

## 4) The repo is the system of record

Long-horizon agentic work fails when knowledge lives only in chat history.

xlfg writes contracts, plans, reviews, logs, and learnings into the repository so future runs start from a map instead of from scratch.

## 5) Compounding must be verified

Not every observation deserves to become durable knowledge.

xlfg only compounds lessons that are concrete, provenance-backed, and connected to real verification or review outcomes.

## 6) Big verify loops should be rare

The right default is:

- targeted checks during implementation
- full gate verification before shipping

This reduces wasted hackathon-style cycles where the agent spends 15–20 extra minutes fighting a brittle harness instead of moving the product forward.
