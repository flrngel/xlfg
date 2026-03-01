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

## Constraints

- Environment / OS:
- Performance:
- Security / privacy:
- UX / accessibility:

## Open questions

- ...
"""

FLOW_SPEC_TEMPLATE = """# Flow spec

This file is the shared **behavior contract** for implementation and verification.

## Summary

- Goal:
- Non-goals:

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

## Acceptance criteria

## Non-goals
"""

PLAN_TEMPLATE = """# Plan

## Summary

## Ordered tasks
- [ ] T1 <task aligned to scenario IDs>

## Definition of done
- Flow spec satisfied
- Test contract satisfied
- Verification green
- Review green
- Compound completed
"""

TEST_CONTRACT_TEMPLATE = """# Test contract

This file defines **what to test** before implementation starts.

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

## Known failure patterns to watch for
- Port already in use
- Stale server / old bundle
- Missing seed / missing env vars
"""

SCORECARD_TEMPLATE = """# Scorecard

## F2P status
- `P0-1`: UNASSESSED

## P2P status
- Core regression suites: UNASSESSED

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
    safe_write(docs_dir / "flow-spec.md", FLOW_SPEC_TEMPLATE)
    safe_write(docs_dir / "spec.md", SPEC_TEMPLATE)
    safe_write(docs_dir / "plan.md", PLAN_TEMPLATE)
    safe_write(docs_dir / "test-contract.md", TEST_CONTRACT_TEMPLATE)
    safe_write(docs_dir / "env-plan.md", ENV_PLAN_TEMPLATE)
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
