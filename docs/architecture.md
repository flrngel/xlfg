# Architecture

xlfg ships two complementary layers:

1. **A Claude Code plugin** (commands / agents / skills)
2. **A lightweight CLI** (`xlfg`) that creates the same run structure and can run doctor + verification loops

They share the same artifact model:

- Durable artifacts live in `docs/xlfg/` (commit these)
- Ephemeral logs live in `.xlfg/` (gitignore these)

## Artifact model

Each run is organized around four pre-implementation contracts:

- `context.md` — request, constraints, assumptions, open questions
- `flow-spec.md` — shared UX / behavior contract
- `test-contract.md` — scenario-to-test mapping for F2P and P2P
- `env-plan.md` — exact harness rules: install, dev server, port, healthcheck, cleanup

And four post-implementation artifacts:

- `plan.md` — ordered work aligned to scenario IDs
- `verification.md` — evidence of layered verification runs
- `scorecard.md` — step-level status for new behavior and regressions
- `reviews/` + `run-summary.md` + `compound-summary.md`

## Knowledge model

`docs/xlfg/knowledge/` contains:

- `quality-bar.md`
- `decision-log.md`
- `patterns.md`
- `testing.md`
- `ux-flows.md`
- `failure-memory.md`
- `harness-rules.md`
- `commands.json`

These files are intentionally separated by **durability**:

- **Patterns / decisions / UX flows** = reusable product or architecture knowledge
- **Failure memory / harness rules** = reusable operational knowledge
- **commands.json** = deterministic execution contract for future runs

## File-based subagent protocol

Subagents should:

1. Read canonical run inputs (`context.md`, `flow-spec.md`, `test-contract.md`, `env-plan.md`)
2. Write exactly one owned output file unless explicitly told otherwise
3. Avoid editing shared canonical files unless they are the designated reducer

This keeps multi-agent work deterministic and auditable.

## Verification pipeline

xlfg verification is layered:

1. **Fast** — lint / typecheck / static checks
2. **Smoke** — targeted scenario checks tied to the flow contract
3. **E2E / real-flow** — only for the required P0/P1 paths
4. **Full regression** — broader suites and build / packaging checks

Before smoke or e2e, xlfg may run an **environment doctor** that:

- checks whether a healthy server already exists
- reuses it if safe
- avoids starting duplicate `yarn dev` / `npm run dev` processes
- writes a doctor report into `.xlfg/`

## Compounding model

A run compounds into knowledge only after verification + review.

Verified lessons are appended into the durable knowledge files, especially:

- `testing.md`
- `failure-memory.md`
- `harness-rules.md`
- `ux-flows.md`

This keeps the system improving from real failures rather than vague summaries.
