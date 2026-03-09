# DeerFlow review for xlfg 2.0.5

This document exists so the next agent can understand why this patch happened, what was borrowed, what was rejected, and where xlfg should go next.

## Why DeerFlow mattered

DeerFlow is interesting because it treats a harness as **runtime infrastructure** rather than as a single oversized agent prompt. Its public docs describe it as a “super agent harness” that orchestrates sub-agents, memory, sandboxes, and extensible skills, and DeerFlow 2.0 is described as a ground-up rewrite. The README also emphasizes progressive skill loading, execution modes, scoped sub-agents, and isolated sandboxes. Useful detail from its backend docs includes explicit thread state, TodoList-based plan mode, a middleware chain, bounded subagent concurrency (`MAX_CONCURRENT_SUBAGENTS = 3`), and a 15-minute subagent timeout.

The important lesson for xlfg was not “copy DeerFlow.” The important lesson was that a real harness needs:

- explicit execution state
- bounded work
- selective capability loading
- isolated role contexts
- durable memory separate from live run state

## Quick comparison

| Dimension | DeerFlow | xlfg 2.0.4 | xlfg 2.0.5 |
|---|---|---:|---:|
| Main product shape | multi-service super harness runtime | plugin-first SDLC harness | plugin-first SDLC harness |
| Runtime stack | LangGraph + Gateway + Frontend + Nginx + sandbox providers | none | none |
| Task state | explicit thread state + TodoList plan mode | partial | **explicit `workboard.md`** |
| Execution modes / budgets | flash / standard / pro / ultra plus subagent toggles | none | **`quick` / `standard` / `deep` harness profiles** |
| Capability loading | skills loaded progressively | partial | **optional agents loaded only when triggered** |
| Durable memory | built-in memory + injected facts | deterministic lexical memory | deterministic lexical memory + stronger role split |
| Proof linkage | broad harness, general-purpose | scorecard only | **`proof-map.md` + scorecard** |
| Local plugin simplicity | low | high | high |

## What xlfg should steal

### 1) Execution profiles, not one-size-fits-all intensity

DeerFlow exposes different execution modes and optional subagent delegation. xlfg should copy the idea, not the literal interface. That became `harness-profile.md` with `quick`, `standard`, and `deep`. The profile now selects the minimum honest harness intensity, including task budget, checker-loop budget, parallelism budget, verify mode, review lenses, and escalation rules.

### 2) Persistent task state

DeerFlow’s explicit thread state and TodoList plan mode are a strong signal that long tasks need visible execution state. xlfg now has `workboard.md` as the run-truth ledger for stages, tasks, blockers, and next action.

### 3) Progressive capability loading

DeerFlow loads skills progressively and keeps the context window lean. xlfg now adopts the same idea at the planning layer: optional planning agents should load only when the core diagnosis justifies them.

### 4) Bounded subagent execution

DeerFlow’s explicit concurrency limit and timeout are good reminders that “more agents” is not the same as “better.” xlfg now treats subagent budget as part of the harness profile rather than a constant hidden assumption.

## What xlfg should reject

### 1) A giant always-on runtime stack

DeerFlow’s multi-service runtime is real infrastructure, but xlfg is a plugin-first harness for local production work. Requiring a gateway, frontend, and reverse proxy would add weight without fixing the user’s core problem.

### 2) Semantic / injected memory as the main recall path

DeerFlow has configurable memory injection. xlfg should keep deterministic recall as the core because the user explicitly does not trust fuzzy retrieval enough for production harness memory.

### 3) Sandboxed generality over repo-local truth

DeerFlow’s sandbox is valuable for a general-purpose super harness. xlfg’s stronger advantage is repo-local contracts and proof files that survive agent turnover.

## Research that supported the patch

OpenAI’s Codex harness posts argue that the main engineering job is often making missing capabilities **legible and enforceable** for the agent, not just “trying harder.” They also describe the harness as reusable execution logic across multiple surfaces and note that Codex uses standard development tools directly, including repository-embedded skills. That strongly supports keeping xlfg as a repo-embedded harness with explicit files and subcommands.

LongCLI-Bench is directly aligned with the user’s pain. It introduces a dual-set testing protocol for requirement fulfillment (F2P) and regression avoidance (P2P), reports pass rates below 20% for current state-of-the-art agents, shows that many failures happen early, and finds that plan injection / human guidance helps more than naive self-correction. That supports shifting effort earlier into why / diagnosis / proof definition.

The subtask-level memory paper argues that instance-level memory has a granularity mismatch for SWE agents and reports average Pass@1 gains of +4.7 points when memory is aligned to subtasks instead of global trajectories. That supports xlfg’s role-specific memory and stage-aligned recall.

ESAA supports the append-only, replayable side of xlfg’s memory design: separate intention from state mutation, keep an append-only log, and project a verifiable materialized view. That is close to why xlfg keeps `ledger.jsonl`, local runs, and tracked knowledge as separate layers.

OpenDev reinforces several harness ideas that fit xlfg without turning it experimental: dual-agent separation between planning and execution, lazy tool discovery, adaptive context compaction, and event-driven reminders. xlfg already does not need the whole architecture, but it should keep moving toward bounded loops, selective loading, and context efficiency.

## What changed in this patch

- Added `xlfg-why-analyst`
- Added `xlfg-harness-profiler`
- Added run files: `why.md`, `harness-profile.md`, `workboard.md`, `proof-map.md`
- Reworked `/xlfg:plan` to be why-first and progressively load optional agents
- Reworked `/xlfg:implement` to use harness-profile budgets and maintain the workboard / proof map
- Reworked `/xlfg:verify` so proof gaps can keep the run RED even when commands are green
- Reworked `/xlfg:review` so required review lenses come from the harness profile
- Reworked `/xlfg:compound` so it compounds why / proof / profile lessons as durable memory
- Added role memory for `why-analyst` and `harness-profiler`

## Harness point of view going forward

The best next step is **not** “make xlfg more like DeerFlow.”

The best next step is:
- strengthen the contracts that already exist
- make more of them mechanically enforceable
- add stack-specific harness profiles where the environment is repetitive
- keep the plugin path simple
- keep memory deterministic and auditable

## What the next similar patch should consider

1. mechanically validating `proof-map.md` shape
2. profile-specific enforcement for task / checker limits
3. repo-specific harness profiles for common stacks (Next.js, Vite, Rails, FastAPI)
4. sharper framework-specific reviewers where repeated drift actually exists

## References

- DeerFlow README: https://raw.githubusercontent.com/bytedance/deer-flow/main/README.md
- DeerFlow backend CLAUDE guide: https://raw.githubusercontent.com/bytedance/deer-flow/main/backend/CLAUDE.md
- OpenAI, “Harness engineering: leveraging Codex in an agent-first world”: https://openai.com/index/harness-engineering/
- OpenAI, “Unlocking the Codex harness: how we built the App Server”: https://openai.com/index/unlocking-the-codex-harness/
- LongCLI-Bench: https://arxiv.org/abs/2602.14337
- Structurally Aligned Subtask-Level Memory for Software Engineering Agents: https://arxiv.org/html/2602.21611v1
- ESAA: Event Sourcing for Autonomous Agents in LLM-Based Software Engineering: https://arxiv.org/abs/2602.23193
- OpenDev: https://arxiv.org/abs/2603.05344
