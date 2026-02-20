# Philosophy

xlfg is built around a few non-negotiable ideas:

## The repo is the system of record

Long-horizon agentic work fails when knowledge lives only in chat history.
xlfg writes specs, plans, risks, and verification evidence into the repository so future work can start with a map.

## Map-reduce > monolithic prompts

We use independent subagents to produce structured artifacts (repo map, spec, test plan, risks, reviews). The lead agent reduces those into a plan and implements with verification gates.

## Evidence-first shipping

A change is only "done" when tests/lint/build are green and the evidence is written down. No silent claims.

## Parallelism only where safe

We parallelize research, review, and test planning. We avoid parallel edits to the same files unless the toolchain provides explicit isolation (e.g., git worktrees).

## Quality gates

Risky work requires explicit approval, rollback planning, and extra verification.
