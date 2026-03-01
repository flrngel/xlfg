# Research notes behind xlfg 1.0

This version was redesigned around a few recurring lessons from recent agent systems and long-horizon benchmarks:

- Long-horizon coding fails early when requirements are vague and when agents only discover real constraints during late execution.
- Dual-set verification matters: prove the new requirement and separately protect existing behavior.
- Better planning upfront is often cheaper than repeated self-correction after the agent has already gone down the wrong branch.
- Memory and compounding need verification gates and provenance, otherwise the system just accumulates noisy summaries.
- Environment control is part of correctness. Port conflicts, stale servers, and watch-mode hangs are agent failure modes, not just local annoyances.

xlfg turns those lessons into concrete artifacts:

- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `scorecard.md`
- `failure-memory.md`
- `harness-rules.md`

The goal is not maximum agent fan-out. The goal is **fast, correct, compounding execution**.
