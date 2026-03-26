# xlfg 2.0.10: planning + autonomy refresh from 2026 papers

This document is the context handoff for why xlfg 2.0.10 changed, what 2026 papers informed it, and what the next intelligent agent should preserve.

## The user complaints that drove this revision

1. `prepare` was being treated like a routine phase even though it is just scaffold maintenance.
2. Planning was weaker than vanilla Claude Code planning.
3. Plans sometimes quietly assumed the user would do implementation or major tests later.
4. Too much fan-out was making planning noisy instead of better.

The fix in 2.0.10 is not “more process.” It is **less routine ceremony, better planning structure, and clearer execution ownership**.

## 2026 paper takeaways that matter

### 1) Better problem statements before execution

**CodeScout (2026)** argues that many failures start from poorly specified requests. Its useful moves are:
- lightweight pre-exploration before execution
- targeted context scoping
- explicit reproduction steps / expected behavior / exploration hints
- better natural-language problem statements before the normal agent loop

xlfg keeps this as:
- the intent contract inside `spec.md`
- recall before wide fan-out
- a lead-owned plan that starts from request truth, not file edits

### 2) Long-horizon failures start early

**LongCLI-Bench (2026)** is the clearest software-agent warning in the bundle:
- failures cluster early
- requirement documents matter
- tests should be written from the requirement document, not the solution repo
- dual-set proof matters: **F2P** for changed behavior and **P2P** for preserved behavior
- human plan injection beats naive late self-correction

xlfg keeps this as:
- tests-before-code
- `flow-spec.md` + `test-contract.md`
- `proof-map.md` + `scorecard.md`
- a hard `test-readiness.md` gate before coding

### 3) Planning must track dependency and keep a reusable reasoning state

**QoT / Questions-of-Thoughts (2026)** says good reasoning needs:
- sequential dependency tracking
- stepwise self-verification
- an evolving reasoning knowledge base that accumulates intermediate decisions and constraints

xlfg keeps this as three explicit planning states:
- **semantic state** — the intent contract inside `spec.md`, `why.md`, `diagnosis.md`
- **structural state** — `repo-map.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`
- **execution state** — `plan.md`, `workboard.md`, `proof-map.md`, `scorecard.md`

### 4) Static tests hide brittle fixes

**SWE-CI (2026)** shows that brittle fixes can look correct in a one-shot functional evaluation but fail over long-term evolution. Its architect–programmer CI-loop framing matters.

xlfg keeps this as:
- a stronger planning/implementation split
- explicit rejection of monkey fixes / temp fixes
- future-evolution guard thinking in `solution-decision.md`

### 5) Emergent specification causes faithfulness loss

**When the Specification Emerges / SLUMP (2026)** shows that long interactions lose design faithfulness relative to having the full design upfront. It introduces a useful distinction between:
- **semantic project state** — what the system should do
- **structural project state** — where that design currently lives in the code

xlfg keeps this directly in its three-state planning model.

### 6) Too many agents can make the system worse

**Loosely-Structured Software (2026)** warns that scaling the number of agents amplifies context pressure, coordination errors, and drift.

xlfg keeps this as:
- a **lead-owned** planning pass
- a small default specialist budget
- optional specialist loading only when a real trigger fires

### 7) Most skills do not help much unless they fit tightly

**SWE-Skills-Bench (2026)** shows that most public SWE skills add little, and some hurt when their guidance mismatches project context.

xlfg keeps this as:
- fewer routine planning subagents
- stronger context compatibility requirements
- reluctance to add more always-on skill logic

### 8) Scaffolding and runtime harness are different things

**OpenDev (2026)** is important here. It separates:
- **scaffolding** — assembling the agent before the first prompt
- **harness** — runtime orchestration, context management, and safety

xlfg adopts that distinction directly:
- scaffold sync still exists
- but it is no longer treated as a routine workflow phase

## What changed in 2.0.10

### 1) `/xlfg` no longer starts with prepare

Normal workflow is now:
1. recall
2. plan
3. implement
4. verify
5. review
6. compound

`prepare` and `init` remain manual maintenance commands.

### 2) Planning is simpler and more opinionated

Planning is now a **lead-agent synthesis pass**.

Default planning budget:
- lead planner
- plus up to ~4 specialist passes unless a real trigger fires

The lead owns:
- `why.md`
- `harness-profile.md`
- `test-readiness.md`
- `spec.md`
- `plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`

### 3) Execution ownership is explicit

By default, the agent owns:
- implementation
- repo-local config changes needed for correctness
- tests and test harness updates
- dev-server orchestration
- major local verification

Human-only blockers are now narrow by design:
- unavailable secrets / credentials
- destructive external or production actions
- unresolved product decisions that change correctness

### 4) The run now has a clearer internal state model

The run should always be understandable through:
- semantic state
- structural state
- execution state

This is the simplest useful way to keep the request from drifting and the proof from becoming fake.

## What the next agent should preserve

1. Do **not** reintroduce `prepare` as a normal `/xlfg` stage.
2. Do **not** turn planning back into a many-agent swarm by default.
3. Keep execution ownership explicit and biased toward the agent doing the work.
4. Keep test scenarios concise, practical, and predeclared.
5. Preserve the semantic / structural / execution state split.
6. Preserve the intent contract inside `spec.md` as request truth, `workboard.md` as execution truth, and `proof-map.md` as proof truth.

## Remaining open questions

- stack-specific command inference still needs repo-specific tuning
- `test-readiness.md` is still only as good as the planner’s honesty
- stronger mechanical enforcement of workboard/proof-map consistency could help later
- there is still room for a better automatic decision of when `solution-architect` or `env-doctor` should trigger
