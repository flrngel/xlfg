from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Optional

from .util import ensure_dir, safe_write, slugify


def generate_run_id(request: str, now: Optional[_dt.datetime] = None) -> str:
    now = now or _dt.datetime.now()
    ts = now.strftime("%Y%m%d-%H%M%S")
    slug = slugify(request)
    return f"{ts}-{slug}"


CONTEXT_MD_TEMPLATE = """# Context

## Request

{request}

## Assumptions

- (fill as you learn)

## Constraints

- (env/OS/perf/security/UX)
"""


def create_run(root: Path, request: str, run_id: Optional[str] = None) -> dict:
    """Create a new xlfg run folder and write initial context."""

    rid = run_id or generate_run_id(request)

    docs_dir = root / "docs" / "xlfg" / "runs" / rid
    dx_dir = root / ".xlfg" / "runs" / rid

    ensure_dir(docs_dir)
    ensure_dir(dx_dir)

    context_path = docs_dir / "context.md"
    safe_write(context_path, CONTEXT_MD_TEMPLATE.format(request=request.strip()))

    # Optional stubs (do not overwrite)
    safe_write(docs_dir / "spec.md", "# Spec\n\n")
    safe_write(docs_dir / "plan.md", "# Plan\n\n")

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
