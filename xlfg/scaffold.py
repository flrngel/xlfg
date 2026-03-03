from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .util import append_unique_line, ensure_dir, safe_write

INDEX_MD = """# xlfg

This folder is the **file-based context** system-of-record for `/xlfg` runs.

## Structure

- `knowledge/` — durable patterns, decisions, flow contracts, and harness learnings (commit this)
- `runs/` — one folder per run containing diagnosis, solution decisions, contracts, plans, reviews, scorecards, and run summaries (commit this)

Ephemeral logs (do not commit):

- `.xlfg/runs/` — raw command outputs, screenshots, traces, doctor reports

## The core rule

Define **what the real problem is** and **what to build / test** *before* implementation:

1. `diagnosis.md` — root problem or missing capability
2. `solution-decision.md` — chosen solution and rejected shortcuts
3. `flow-spec.md` — UX / behavior contract
4. `test-contract.md` — F2P + P2P test mapping
5. `env-plan.md` — exact harness and dev-server plan
6. `scorecard.md` — step-level status for requirements and regressions

## How to use

- Run `xlfg start "your request"` (or `/xlfg` in Claude Code) to begin a new run.
- Each run writes artifacts to `docs/xlfg/runs/<run-id>/`.
- Verification logs land in `.xlfg/runs/<run-id>/`.
- Canonical repo commands and dev-server settings live in `docs/xlfg/knowledge/commands.json`.
"""

QUALITY_BAR_MD = """# xlfg quality bar

Nothing is "done" unless:

- **Diagnosis is explicit** (`diagnosis.md` exists)
- **The root solution is explicit** (`solution-decision.md` exists and records rejected shortcuts)
- **Behavior is contracted first** (`flow-spec.md` exists)
- **Test intent is shared** (`test-contract.md` exists and maps scenarios to checks)
- **Environment is controlled** (`env-plan.md` explains ports, healthchecks, and cleanup)
- **New behavior is proven** (Fail → Pass)
- **Existing behavior is preserved** (Pass → Pass)
- **Lint / typecheck / build** pass when applicable
- **User-facing flows are validated** (happy path, alternates, failure path, a11y)
- **Unexpected failures are compounded** into failure memory / harness rules
- **Operational plan exists** (monitoring + rollback notes)

Evidence should be recorded in each run's `verification.md` and `scorecard.md`.
"""

DECISION_LOG_MD = """# xlfg decision log

Record durable architectural and product decisions made during `/xlfg` runs.

## Template

- **Date**:
- **Decision**:
- **Context**:
- **Alternatives considered**:
- **Rejected shortcut**:
- **Consequences**:
- **Links**: (run folder, PR, issues)
"""

PATTERNS_MD = """# xlfg patterns

Reusable patterns discovered while shipping.

## Template

## Pattern: <name>

- **When to use**:
- **Why it works**:
- **Implementation notes**:
- **What shortcut it replaces**:
- **Pitfalls**:
- **Examples / links**:
"""

TESTING_MD = """# xlfg testing knowledge

Durable testing learnings captured from `/xlfg` runs.

## Template

## Scenario: <id> <name>

- **Requirement kind**: F2P | P2P
- **Failure that escaped**:
- **Why it escaped**:
- **Fastest check that catches it**:
- **Real-flow / integration check**:
- **Regression suite that must stay green**:
- **Root-cause proof note**:
- **Stabilization notes**:
- **Links**: (run folder, PR, issue)
"""

UX_FLOWS_MD = """# xlfg ux flows

Durable user-flow contracts that repeatedly matter across runs.

## Template

## Flow: <name>

- **Actor**:
- **Preconditions**:
- **Primary steps**:
- **Alternate steps**:
- **Failure path**:
- **Assertions**:
- **Accessibility / keyboard notes**:
- **Links**:
"""

FAILURE_MEMORY_MD = """# xlfg failure memory

Recurring unexpected failures and proven responses.

## Template

## Failure signature: <short name>

- **Observed symptom**:
- **Detection signal**:
- **Likely root cause**:
- **Immediate fix**:
- **Prevention rule**:
- **Verification after fix**:
- **Links**:
"""

HARNESS_RULES_MD = """# xlfg harness rules

Rules for running reliable local verification.

## Template

## Rule: <name>

- **Applies to**:
- **Why**:
- **Required command / flag**:
- **Healthcheck / readiness rule**:
- **Cleanup rule**:
- **Wrong-green trap to avoid**:
- **Links**:
"""

COMMANDS_JSON = """{
  "install": null,
  "verify_fast": [],
  "smoke": [],
  "e2e": [],
  "verify_full": [],
  "dev": {
    "command": null,
    "cwd": ".",
    "port": null,
    "healthcheck": null,
    "startup_timeout_sec": 120,
    "reuse_if_healthy": true
  },
  "notes": "Fill in canonical commands and the dev-server contract. xlfg will auto-detect best-effort defaults if this file stays empty. Prefer commands that are non-interactive and prove the real user flow."
}
"""


def init_scaffold(root: Path) -> Dict[str, List[str]]:
    """Create xlfg scaffolding under root.

    Idempotent: does not overwrite existing files.
    """

    created: List[str] = []
    updated: List[str] = []

    ensure_dir(root / "docs" / "xlfg" / "knowledge")
    ensure_dir(root / "docs" / "xlfg" / "runs")
    ensure_dir(root / ".xlfg" / "runs")

    gitignore_path = root / ".gitignore"
    if append_unique_line(gitignore_path, ".xlfg/"):
        updated.append(str(gitignore_path))

    files = {
        "docs/xlfg/index.md": INDEX_MD,
        "docs/xlfg/knowledge/quality-bar.md": QUALITY_BAR_MD,
        "docs/xlfg/knowledge/decision-log.md": DECISION_LOG_MD,
        "docs/xlfg/knowledge/patterns.md": PATTERNS_MD,
        "docs/xlfg/knowledge/testing.md": TESTING_MD,
        "docs/xlfg/knowledge/ux-flows.md": UX_FLOWS_MD,
        "docs/xlfg/knowledge/failure-memory.md": FAILURE_MEMORY_MD,
        "docs/xlfg/knowledge/harness-rules.md": HARNESS_RULES_MD,
        "docs/xlfg/knowledge/commands.json": COMMANDS_JSON,
    }

    for rel_path, content in files.items():
        if safe_write(root / rel_path, content):
            created.append(rel_path)

    return {"created": created, "updated": updated}
