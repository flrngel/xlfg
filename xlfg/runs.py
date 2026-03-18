from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Optional

from .util import ensure_dir, safe_write, slugify


CONTEXT_MD_TEMPLATE = """# Context

## Request

{request}

## Source context
- user request / issue / ticket text:
- follow-up clarifications already given:
- repo / service area likely involved:

## Product / user intent
- who is this for?
- what problem is changing?
- what friction or failure is happening now?
- what false success would still disappoint the user?

## Constraints
- environment / OS:
- performance:
- security / privacy:
- UX / accessibility:
- delivery constraints:

## Open questions
- ...
"""

QUERY_CONTRACT_TEMPLATE = """# Query contract

This file keeps the run honest about **what the request actually means**.

## Work kind
- `build` | `bugfix` | `research` | `multi`

## Raw request
- ...

## Objective groups
- `O1`: ...
- `O2`: ...

## Direct asks
- `Q1`: ...

## Implied asks
- `I1`: ...

## Functionality and quality requirements
- `R1`: ...

## General solution constraints
- ...

## Specific solution constraints
- ...

## Expected behavior / acceptance criteria
- `A1`: ...

## Reproduction / baseline notes
- ...

## Non-goals / explicitly not requested
- ...

## Developer / product intention
- ...

## Prohibited shallow fixes
- one-entry-point patch
- test-only green without real behavior proof
- disabling / weakening checks to get green
- local symptom masking that leaves alternate paths broken

## Open ambiguities
- ...

## Carry-forward anchor
- direct asks to keep visible after long trajectories:
- implied asks that must not be dropped:
- quality bar that must survive implementation:
- most dangerous monkey-fix trap:
"""

WHY_TEMPLATE = """# Why

This file keeps the run anchored to the user and product reason for the work.

## Why this work matters now
- ...

## User / operator pain today
- ...

## Better state after this run
- ...

## Non-negotiable quality bar
- ...

## Things we must not optimize for
- superficial green tests
- a symptom-hiding patch
- unnecessary fan-out
- “works on my machine” proof

## Non-goals
- ...
"""

MEMORY_RECALL_TEMPLATE = """# Memory recall

Summarize only the smallest relevant slice of prior knowledge before planning. This file must make it obvious what was queried, what matched, and what was *not* reused.

## Queries / sources used
- current-state.md:
- typed query or lexical query:
- scopes checked:

## Strong matches
- ...

## Rules carried into this run
- ...

## Rejected near-matches / why they do not apply
- ...

## Explicit no-hit statement
- If nothing relevant matched, say it plainly here.
"""

DIAGNOSIS_TEMPLATE = """# Diagnosis

## Problem summary
- ...

## Current behavior / baseline
- ...

## Causal chain
1. ...
2. ...
3. ...

## Root cause / missing capability
- ...

## Evidence
- ...

## Tempting shortcuts to reject
- ...

## Unknowns
- ...

## Quick validation probes
- ...
"""

SOLUTION_DECISION_TEMPLATE = """# Solution decision

## Options considered

### Option A
- How it works:
- Pros:
- Cons:

### Option B
- How it works:
- Pros:
- Cons:

## Chosen solution
- ...

## Why this is the root solution
- ...

## Rejected shortcuts
- ...

## Disconfirming evidence to watch for
- What result would prove this design is wrong?

## Subagent evidence used
- repo-map.md:
- diagnosis.md:
- flow-spec.md:
- test-contract.md:
- env-plan.md:

## Testing / rollout implications
- ...

## Task decomposition hints
- ...
"""

HARNESS_PROFILE_TEMPLATE = """# Harness profile

This file chooses the minimum harness intensity that still gives honest proof.

## Selected profile
- `quick` | `standard` | `deep`

## Why this profile fits
- ...

## Work shape
- single-flow build | bugfix | multi-task | research-heavy

## Planning fan-out
- required agents:
- optional agents only if triggered:

## Execution budget
- max ordered tasks:
- max checker loops per task:
- max parallel subagents:

## Verification recommendation
- recommended verify mode: `fast` | `full`
- scenario classes that must get smoke or e2e:

## Required review lenses
- ...

## Escalation rules
- What conditions force this run to step up to a deeper profile?
"""

FLOW_SPEC_TEMPLATE = """# Flow spec

This file is the shared **behavior contract** for implementation and verification.

## Summary
- goal:
- why this flow matters:
- non-goals:
- objective groups covered:
- query / intent IDs covered:

## State / transition model
- start state:
- key transitions:
- success terminal state:
- failure terminal state:

## Required scenario cards

### P0-1 — <primary flow name>
- objective: `O1`
- query_ids: `Q1 I1 A1`
- actor:
- preconditions:
- practical_steps:
  1. ...
  2. ...
  3. ...
- interaction_variants:
  - click path:
  - keyboard path:
  - enter vs button:
- expected_outcome:
- failure_states:
- accessibility:
- telemetry_or_logs:
- non_goals:

## Existing behavior to preserve
- ...
"""

SPEC_TEMPLATE = """# Spec

## Summary
- ...

## Objective coverage
- `O1`: ...
- `O2`: ...

## Query / intent coverage
- `Q1` / `I1` / `A1`: ...

## Why
- ...

## Root cause / missing capability
- ...

## Chosen solution
- ...

## Rejected shortcuts
- ...

## Acceptance criteria
- ...

## Non-goals
- ...

## Rollout / rollback notes
- ...

## Subagent decisions preserved
- which core agent outputs were adopted directly:
- any disagreement / override and evidence for it:
"""

PLAN_TEMPLATE = """# Plan

## Summary
- ...

## Objectives
- `O1`: ...
- `O2`: ...

## Ordered tasks
- [ ] T1 <task aligned to scenario IDs> | objectives: <O1> | query IDs: <Q1 I1 A1> | scenario IDs: <P0-1> | scope: <...> | checks: <fast_check / ship_check> | disproof probe: <...>

## Test-first rule
- each changed scenario must have a practical fast check and a ship proof before implementation begins
- if a task cannot name its proof, return to planning instead of coding

## Definition of done
- direct asks are covered or explicitly deferred
- non-negotiable implied asks still hold
- diagnosis confirmed or intentionally revised
- root solution implemented (or bounded workaround explicitly approved)
- why file still matches the shipped change
- flow spec satisfied
- test contract satisfied
- test-readiness verdict stayed READY or was consciously re-approved after plan changes
- proof map has concrete evidence links for required scenarios and query / intent IDs
- verification green
- review green
- compound completed
"""

TEST_CONTRACT_TEMPLATE = """# Test contract

Keep this file **short, concrete, and practical**. Prefer 1–5 required scenario contracts total.

## Required scenario contracts

### P0-1 — <primary flow name>
- objective: `O1`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q1 I1 A1`
- practical_steps:
  1. ...
  2. ...
  3. ...
- fast_check: <single fastest honest command or NONE>
- ship_phase: `fast` | `smoke` | `e2e` | `manual`
- ship_check: <single command or NONE>
- regression_check: <single command or NONE>
- manual_smoke: <precise manual steps when automation is not practical>
- anti_monkey_probe: <what would still fail under a shallow patch>
- notes: <GUESS if command inference is uncertain>

### G1 — <existing behavior to preserve>
- objective: `O1`
- requirement_kind: `P2P`
- priority: `P1`
- query_ids: `I1`
- practical_steps:
  1. ...
- fast_check: <single guard command or NONE>
- ship_phase: `fast` | `smoke` | `e2e` | `manual`
- ship_check: <single command or NONE>
- regression_check: <single command or NONE>
- manual_smoke: <precise manual steps>
- anti_monkey_probe: <what a narrow regression would miss>
- notes:

## Why these scenarios are enough
- ...

## Wrong-green traps
- ...
"""

TEST_READINESS_TEMPLATE = """# Test readiness

## Verdict
- `READY` | `REVISE`

## Required scenario coverage
- which direct asks / implied asks are covered by the scenario contracts:
- which scenarios are still vague or missing:

## Practicality check
- are the checks cheap enough for iteration?
- is there a single honest ship proof per changed primary scenario?
- is the plan relying on “run everything later” instead of concrete proof?

## Under-testing risks
- ...

## Over-testing risks
- ...

## Missing commands / manual proof gaps
- ...

## Required fixes before implementation
- ...
"""

ENV_PLAN_TEMPLATE = """# Environment plan

## Install
- ...

## Dev server
- command:
- port:
- healthcheck:
- reuse if healthy:
- startup timeout:

## Verification harness rules
- avoid watch mode
- capture logs under `.xlfg/`
- do not start duplicate dev servers
- check actual environment state, not just process start
- call out stale-version or stale-bundle traps

## Known failure patterns to watch for
- port already in use
- stale server / old bundle
- missing seed / missing env vars
"""

WORKBOARD_TEMPLATE = """# Workboard

This is the run-level task and stage ledger.

## Stage status
- prepare: DONE
- recall: TODO
- plan: TODO
- implement: TODO
- verify: TODO
- review: TODO
- compound: TODO

## Current next action
- ...

## Carry-forward anchor
- re-read `query-contract.md` before each major phase and each task handoff
- do not drop direct asks or non-negotiable implied asks
- do not ship a monkey fix as if it were the root solution

## Objectives
| Objective | Status | Direct asks | Scenarios | Notes |
|---|---|---|---|---|
| O1 | TODO | Q1 | P0-1 |  |

## Tasks
| Task | Status | Objectives | Query IDs | Scenario IDs | Owner | Checks | Notes |
|---|---|---|---|---|---|---|---|
| T1 | TODO | O1 |  |  |  |  |  |

## Scenario coverage
| Scenario | Status | Fast proof | Ship proof | Evidence |
|---|---|---|---|---|
| P0-1 | UNASSESSED |  |  |  |

## Blockers / escalations
- ...
"""

PROOF_MAP_TEMPLATE = """# Proof map

This file links every required scenario and query / intent clause to concrete evidence.

## Required scenarios
| Scenario ID | Objective | Query / intent IDs | Requirement kind | Fast proof | Ship phase | Ship proof | Regression guard | Evidence path | Status |
|---|---|---|---|---|---|---|---|---|---|
| P0-1 | O1 | Q1 A1 | F2P |  | smoke |  |  |  | UNASSESSED |

## Proof gaps
- Record any scenario or query / intent clause that is still not honestly proven.
"""

SCORECARD_TEMPLATE = """# Scorecard

## Objective status
- `O1`: UNASSESSED | proof: <command or artifact>

## F2P status
- `P0-1` / `Q1` / `A1`: UNASSESSED | fast: <command> | ship: <command or artifact>

## P2P status
- `G1` / `I1`: UNASSESSED | proof: <command or artifact>

## Notes
- Update this after verification and review.
"""


def generate_run_id(request: str, now: Optional[_dt.datetime] = None) -> str:
    now = now or _dt.datetime.now()
    ts = now.strftime("%Y%m%d-%H%M%S")
    slug = slugify(request)
    return f"{ts}-{slug}"


def create_run(root: Path, request: str, run_id: Optional[str] = None) -> dict:
    """Create a new xlfg run folder and write initial context."""

    rid = run_id or generate_run_id(request)

    docs_dir = root / "docs" / "xlfg" / "runs" / rid
    dx_dir = root / ".xlfg" / "runs" / rid

    ensure_dir(docs_dir)
    ensure_dir(dx_dir)
    ensure_dir(docs_dir / "context")
    ensure_dir(docs_dir / "tasks")

    safe_write(docs_dir / "context.md", CONTEXT_MD_TEMPLATE.format(request=request.strip()))
    safe_write(docs_dir / "query-contract.md", QUERY_CONTRACT_TEMPLATE)
    safe_write(docs_dir / "why.md", WHY_TEMPLATE)
    safe_write(docs_dir / "memory-recall.md", MEMORY_RECALL_TEMPLATE)
    safe_write(docs_dir / "diagnosis.md", DIAGNOSIS_TEMPLATE)
    safe_write(docs_dir / "solution-decision.md", SOLUTION_DECISION_TEMPLATE)
    safe_write(docs_dir / "harness-profile.md", HARNESS_PROFILE_TEMPLATE)
    safe_write(docs_dir / "flow-spec.md", FLOW_SPEC_TEMPLATE)
    safe_write(docs_dir / "spec.md", SPEC_TEMPLATE)
    safe_write(docs_dir / "plan.md", PLAN_TEMPLATE)
    safe_write(docs_dir / "test-contract.md", TEST_CONTRACT_TEMPLATE)
    safe_write(docs_dir / "test-readiness.md", TEST_READINESS_TEMPLATE)
    safe_write(docs_dir / "env-plan.md", ENV_PLAN_TEMPLATE)
    safe_write(docs_dir / "workboard.md", WORKBOARD_TEMPLATE)
    safe_write(docs_dir / "proof-map.md", PROOF_MAP_TEMPLATE)
    safe_write(docs_dir / "scorecard.md", SCORECARD_TEMPLATE)

    return {
        "run_id": rid,
        "docs_run_dir": str(docs_dir),
        "dx_run_dir": str(dx_dir),
    }


def latest_run_id(root: Path) -> Optional[str]:
    runs_dir = root / "docs" / "xlfg" / "runs"
    if not runs_dir.exists():
        return None
    candidates = [p.name for p in runs_dir.iterdir() if p.is_dir()]
    if not candidates:
        return None
    return sorted(candidates)[-1]
