from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Optional

from .util import ensure_dir, safe_write, slugify


CONTEXT_MD_TEMPLATE = """# Context

## Request

{request}

## Product / user intent

- Who is this for?
- What problem is changing?
- What friction or failure is happening now?

## Constraints

- Environment / OS:
- Performance:
- Security / privacy:
- UX / accessibility:
- Delivery constraints:

## Open questions

- ...
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

- Goal:
- Why this flow matters:
- Non-goals:

## State / transition model

- Start state:
- Key transitions:
- Success terminal state:
- Failure terminal state:

## Scenarios

## Scenario P0-1: <primary flow name>
- **Actor**:
- **Preconditions**:
- **Primary steps**:
  1. ...
- **Alternate steps**:
  - A. ...
- **Failure / empty / loading states**:
- **Assertions**:
- **Accessibility / keyboard**:
- **Telemetry / observability**:

## Existing behavior to preserve
- ...
"""

SPEC_TEMPLATE = """# Spec

## Summary

## Why

## Root cause / missing capability

## Chosen solution

## Rejected shortcuts

## Acceptance criteria

## Non-goals

## Rollout / rollback notes
"""

PLAN_TEMPLATE = """# Plan

## Summary

## Ordered tasks
- [ ] T1 <task aligned to scenario IDs> | scenario IDs: <...> | scope: <...> | checks: <...> | disproof probe: <...>

## Definition of done
- Diagnosis confirmed or intentionally revised
- Root solution implemented (or bounded workaround explicitly approved)
- Why file still matches the shipped change
- Flow spec satisfied
- Test contract satisfied
- Proof map has concrete evidence links for required scenarios
- Verification green
- Review green
- Compound completed
"""

TEST_CONTRACT_TEMPLATE = """# Test contract

This file defines **what to test** before implementation starts.

## Flow-to-proof map
- `P0-1` → start state: ... | action variants: click / keyboard / enter / button | success proof: ... | failure proof: ...

## F2P (new / changed requirements)
- `P0-1` → fast check: ... | integration / e2e: ... | owner: ...

## P2P (existing behavior to preserve)
- Existing flow / suite: ...

## Layered execution order
1. Static / type / lint
2. Scenario-targeted smoke
3. Required e2e / real-flow checks
4. Broader regression suites

## Manual smoke checklist
- ...

## Wrong-green traps
- ...
"""

ENV_PLAN_TEMPLATE = """# Environment plan

## Install
- ...

## Dev server
- Command:
- Port:
- Healthcheck:
- Reuse if healthy:
- Startup timeout:

## Verification harness rules
- Avoid watch mode
- Capture logs under `.xlfg/`
- Do not start duplicate dev servers
- Check actual environment state, not just process start
- Call out stale-version or stale-bundle traps

## Known failure patterns to watch for
- Port already in use
- Stale server / old bundle
- Missing seed / missing env vars
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

## Tasks
| Task | Status | Scenario IDs | Owner | Checks | Notes |
|---|---|---|---|---|---|
| T1 | TODO |  |  |  |  |

## Blockers / escalations
- ...
"""

PROOF_MAP_TEMPLATE = """# Proof map

This file links every required scenario to concrete evidence.

## Required scenarios
| Scenario ID | Requirement kind | Required proof | Planned check | Evidence path | Status |
|---|---|---|---|---|---|
| P0-1 | F2P |  |  |  | UNASSESSED |

## Regression guards
| Guard | Planned check | Evidence path | Status |
|---|---|---|---|
| Existing behavior |  |  | UNASSESSED |

## Proof gaps
- Record any scenario that is still not honestly proven.
"""

SCORECARD_TEMPLATE = """# Scorecard

## F2P status
- `P0-1`: UNASSESSED | proof: <command or artifact>

## P2P status
- Core regression suites: UNASSESSED | proof: <command or artifact>

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
    safe_write(docs_dir / "why.md", WHY_TEMPLATE)
    safe_write(docs_dir / "memory-recall.md", MEMORY_RECALL_TEMPLATE)
    safe_write(docs_dir / "diagnosis.md", DIAGNOSIS_TEMPLATE)
    safe_write(docs_dir / "solution-decision.md", SOLUTION_DECISION_TEMPLATE)
    safe_write(docs_dir / "harness-profile.md", HARNESS_PROFILE_TEMPLATE)
    safe_write(docs_dir / "flow-spec.md", FLOW_SPEC_TEMPLATE)
    safe_write(docs_dir / "spec.md", SPEC_TEMPLATE)
    safe_write(docs_dir / "plan.md", PLAN_TEMPLATE)
    safe_write(docs_dir / "test-contract.md", TEST_CONTRACT_TEMPLATE)
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
