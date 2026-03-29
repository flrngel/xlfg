from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Optional

from .util import ensure_dir, safe_write, slugify


CONTEXT_MD_TEMPLATE = """# Context

## Request

{request}

## Repo / product context
- likely area involved:
- important files or services:
- current user or operator pain:

## Constraints
- environment / OS:
- performance / latency:
- security / privacy:
- UX / accessibility:
- delivery constraints:

## Known unknowns
- ...
"""

MEMORY_RECALL_TEMPLATE = """# Memory recall

Summarize only the smallest relevant slice of prior knowledge before planning.

## Queries / sources used
- current-state.md:
- lexical / typed query:
- scopes checked:

## Strong matches
- ...

## Rules carried into this run
- ...

## Rejected near-matches / why they do not apply
- ...

## Explicit no-hit statement
- Say plainly when nothing relevant matched.
"""

SPEC_TEMPLATE = """# Spec

Treat this file as the **single source of truth** for the run. Keep it lean enough that intent resolution, planning, implementation, verification, and review can all start here.

## Intent contract
- resolution: `proceed` | `proceed-with-assumptions` | `needs-user-answer`
- work kind: `build` | `bugfix` | `research` | `multi`
- raw request: ...
- direct asks:
  - `Q1`: ...
- implied asks:
  - `I1`: ...
- acceptance criteria:
  - `A1`: ...
- non-goals:
  - ...
- constraints actually requested:
  - ...
- assumptions to proceed:
  - ...
- blocking ambiguities:
  - ...
- carry-forward anchor: ...

## Objective groups
- `O1` — ...; covers: `Q1 I1`; depends_on: `none`; completion: ...
- `O2` — ...

## Outcome / why
- user or operator pain today: ...
- better state after this run: ...
- false success to avoid: ...
- non-negotiable quality bar: ...

## Research and context
- recall summary: ...
- repo findings: ...
- external findings: `repo-only` when none
- key constraints: ...

## Execution shape
- harness profile: `quick` | `standard` | `deep`
- research mode: `none` | `light` | `heavy`
- ownership: `agent unless human-only blocker`
- verify mode: `fast` | `full`
- review lenses: ...
- escalation triggers: ...
- specialist completion rule: `one atomic packet in, one required artifact out`

## Solution summary
- diagnosis / key risk: ...
- chosen solution: ...
- rejected shortcuts: ...

## Task map
- `T1` — ...; objectives: `O1`; scenarios: `P0-1`; owner: `xlfg-task-implementer`; scope: `app/login.ts tests/login.spec.ts`; primary_artifact: `tasks/T1/implementer-report.md`; done_check: `pytest tests/login -q`
- `T2` — ...

## Proof summary
- objective coverage:
  - `O1`: `P0-1 G1`
- fastest honest proof: ...
- ship proof: ...
- readiness target: `READY`

## PM / UX / Engineering / QA / Release
- PM: ...
- UX: ...
- Engineering: ...
- QA: ...
- Release / rollback: ...

## Deferrals / open questions
- ...
"""

TEST_CONTRACT_TEMPLATE = """# Test contract

Keep this file **short, concrete, and practical**. Prefer 1–5 required scenario contracts total.

## Execution ownership
- the agent runs repo-local fast checks and ship proofs itself unless a true human-only blocker is recorded
- ask the user only for secrets/credentials, destructive approvals, or unresolved product decisions that change correctness

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

## Why this verdict
- scenario coverage for direct and implied asks:
- missing or vague proof:

## Practicality check
- is there a cheap feedback loop for iteration?
- is there a real ship proof for changed behavior?

## Human-only blockers
- list only genuine blockers such as missing secrets or destructive external approvals

## Fixes required before implementation
- ...
"""

WORKBOARD_TEMPLATE = """# Workboard

This is the run-level status ledger.

## Stage status
- recall: TODO
- intent: TODO
- context: TODO
- plan: TODO
- implement: TODO
- verify: TODO
- review: TODO
- compound: TODO

## Current next action
- ...

## Single source of truth
- keep `spec.md` current instead of duplicating the same state across multiple planning files

## Execution reminder
- the agent owns implementation, repo-local config changes, and major local verification unless the blocker is truly human-only
- do not ask the user to sequence phase commands or carry the run state for you
- do not mark a specialist lane done from chat alone; require the promised artifact and done check
- do not claim GREEN unless changed behavior is actually proven
- if a bundled request is only partially complete, say exactly which objectives are done vs blocked

## Objective ledger
| Objective | Status | Covers asks | Depends on | Scenarios | Notes |
|---|---|---|---|---|---|
| O1 | TODO | Q1 | none | P0-1 |  |

## Tasks
| Task | Status | Objectives | Query IDs | Scenario IDs | Owner | Checks | Notes |
|---|---|---|---|---|---|---|---|
| T1 | TODO | O1 | Q1 A1 | P0-1 | agent |  |  |

## Risks / blockers
- ...
"""


def generate_run_id(request: str, now: Optional[_dt.datetime] = None) -> str:
    now = now or _dt.datetime.now()
    ts = now.strftime("%Y%m%d-%H%M%S")
    slug = slugify(request)
    return f"{ts}-{slug}"


def create_run(root: Path, request: str, run_id: Optional[str] = None) -> dict:
    """Create a new xlfg run folder and write the lean core docs."""

    rid = run_id or generate_run_id(request)

    docs_dir = root / "docs" / "xlfg" / "runs" / rid
    dx_dir = root / ".xlfg" / "runs" / rid

    ensure_dir(docs_dir)
    ensure_dir(dx_dir)
    ensure_dir(docs_dir / "tasks")

    safe_write(docs_dir / "context.md", CONTEXT_MD_TEMPLATE.format(request=request.strip()))
    safe_write(docs_dir / "memory-recall.md", MEMORY_RECALL_TEMPLATE)
    safe_write(docs_dir / "spec.md", SPEC_TEMPLATE)
    safe_write(docs_dir / "test-contract.md", TEST_CONTRACT_TEMPLATE)
    safe_write(docs_dir / "test-readiness.md", TEST_READINESS_TEMPLATE)
    safe_write(docs_dir / "workboard.md", WORKBOARD_TEMPLATE)

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
