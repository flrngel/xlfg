from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .util import append_unique_line, ensure_dir, safe_write

INDEX_MD = """# xlfg

This folder is the **file-based context** system-of-record for `/xlfg` runs.

## Structure

- `knowledge/` — durable patterns, decisions, and checklists (commit this)
- `runs/` — one folder per run containing specs, plans, reviews, and run summaries (commit this)

Ephemeral logs (do not commit):

- `.xlfg/runs/` — raw command outputs, traces, screenshots

## How to use

- Run `xlfg start "your request"` (or `/xlfg` in Claude Code) to begin a new run.
- Each run writes artifacts to `docs/xlfg/runs/<run-id>/`.
- Verification logs land in `.xlfg/runs/<run-id>/`.
"""

QUALITY_BAR_MD = """# xlfg quality bar

Nothing is "done" unless:

- **Behavior is specified** (acceptance criteria)
- **Tests exist** for new behavior
- **Regression suite passes** (no breakages)
- **Lint / typecheck / build** pass (when applicable)
- **UX is validated** (screenshots, a11y, happy-path + failure-path)
- **Operational plan exists** (monitoring + rollback notes)

Evidence should be recorded in each run's `verification.md`.
"""

DECISION_LOG_MD = """# xlfg decision log

Record durable architectural/product decisions made during `/xlfg` runs.

## Template

- **Date**:
- **Decision**:
- **Context**:
- **Alternatives considered**:
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
- **Pitfalls**:
- **Examples / links**:
"""

COMMANDS_JSON = """{
  "install": null,
  "verify_fast": [],
  "verify_full": [],
  "notes": "Fill in canonical project commands. xlfg will auto-detect if this file is empty."
}
"""


def init_scaffold(root: Path) -> Dict[str, List[str]]:
    """Create xlfg scaffolding under root.

    Idempotent: does not overwrite existing files.
    """

    created: List[str] = []
    updated: List[str] = []

    # directories
    ensure_dir(root / "docs" / "xlfg" / "knowledge")
    ensure_dir(root / "docs" / "xlfg" / "runs")
    ensure_dir(root / ".xlfg" / "runs")

    # gitignore
    gitignore_path = root / ".gitignore"
    if append_unique_line(gitignore_path, ".xlfg/"):
        updated.append(str(gitignore_path))

    # files
    if safe_write(root / "docs" / "xlfg" / "index.md", INDEX_MD):
        created.append("docs/xlfg/index.md")

    if safe_write(root / "docs" / "xlfg" / "knowledge" / "quality-bar.md", QUALITY_BAR_MD):
        created.append("docs/xlfg/knowledge/quality-bar.md")

    if safe_write(root / "docs" / "xlfg" / "knowledge" / "decision-log.md", DECISION_LOG_MD):
        created.append("docs/xlfg/knowledge/decision-log.md")

    if safe_write(root / "docs" / "xlfg" / "knowledge" / "patterns.md", PATTERNS_MD):
        created.append("docs/xlfg/knowledge/patterns.md")

    if safe_write(root / "docs" / "xlfg" / "knowledge" / "commands.json", COMMANDS_JSON):
        created.append("docs/xlfg/knowledge/commands.json")

    return {"created": created, "updated": updated}
