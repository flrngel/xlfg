from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import append_unique_line, ensure_dir, safe_write

SCAFFOLD_SCHEMA_VERSION = 2

INDEX_MD = """# xlfg

This folder is the **file-based context** system-of-record for `/xlfg` work.

## Structure

Tracked durable knowledge:

- `knowledge/` — patterns, decisions, testing knowledge, UX flows, harness rules, and role-specific memories (commit this)
- `meta.json` — scaffold version + migration state (commit this)
- `migrations/` — migration notes when the xlfg version changes (commit this)

Local run evidence (do not commit by default):

- `runs/` — one folder per run containing diagnosis, solution decisions, contracts, plans, reviews, scorecards, and summaries
- `.xlfg/runs/` — raw command outputs, screenshots, traces, doctor reports

## Why `runs/` is local-only by default

Run folders are valuable as **episodic memory** and debugging evidence, but they create high-churn git noise, often include machine-local paths and transient failures, and are usually too verbose to serve as durable knowledge. xlfg therefore keeps:

- `docs/xlfg/runs/` — **local by default** (gitignored, except placeholders)
- `docs/xlfg/knowledge/` — **tracked** and curated
- `.xlfg/` — **ephemeral** and gitignored

Promote only the reusable lesson, not the entire run.

## Core workflow contract

Define **what the real problem is** and **what to build / test** *before* implementation:

1. `diagnosis.md` — root problem or missing capability
2. `solution-decision.md` — chosen solution and rejected shortcuts
3. `flow-spec.md` — UX / behavior contract
4. `test-contract.md` — F2P + P2P test mapping
5. `env-plan.md` — exact harness and dev-server plan
6. `scorecard.md` — step-level status for requirements and regressions

## Agent memory model

xlfg compounds in two layers:

1. **Shared memory** in `knowledge/` for repo-wide rules and patterns
2. **Role memory** in `knowledge/agent-memory/` for agents that repeatedly need the same lessons

Role memory must stay small, typed, and admission-gated. Do not dump raw run summaries there.
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
- **Unexpected failures are compounded** into failure memory / harness rules / role memory when warranted
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

AGENT_MEMORY_INDEX_MD = """# xlfg agent memory

Role memory exists for agents that repeatedly hit the same failure classes.

## Admission rules

Only compound something into role memory when it is:

- specific to the role's job
- validated by verification, review, or repeated successful reuse
- short enough to retrieve quickly
- better expressed as a rule / checklist / anti-pattern than a full summary

## Files

- `root-cause-analyst.md`
- `test-strategist.md`
- `env-doctor.md`
- `task-implementer.md`
- `verify-reducer.md`
- `ux-reviewer.md`
"""

ROOT_CAUSE_MEMORY_MD = """# Agent memory: root-cause-analyst

Store reusable diagnosis lessons that help avoid symptom patches.

## Entry template

## Pattern: <name>
- **Symptom signature**:
- **Likely true cause**:
- **Common wrong shortcut**:
- **Disproof probe**:
- **Evidence threshold before reuse**:
- **Links**:
"""

TEST_STRATEGIST_MEMORY_MD = """# Agent memory: test-strategist

Store scenario-design lessons for defining what to test.

## Entry template

## Flow pattern: <name>
- **Scenario shape**:
- **Fastest proving check**:
- **Real-flow check still required**:
- **Regression guard**:
- **Wrong-green trap**:
- **Links**:
"""

ENV_DOCTOR_MEMORY_MD = """# Agent memory: env-doctor

Store durable harness and environment lessons.

## Entry template

## Harness issue: <name>
- **Symptoms**:
- **Likely cause**:
- **Safe detection order**:
- **Preferred reuse / cleanup rule**:
- **Stack-specific notes**:
- **Links**:
"""

TASK_IMPLEMENTER_MEMORY_MD = """# Agent memory: task-implementer

Store implementation patterns that repeatedly land the root fix cleanly.

## Entry template

## Pattern: <name>
- **When it applies**:
- **Correct layer to edit**:
- **Files that usually move together**:
- **Shortcut to avoid**:
- **Minimal proving change**:
- **Links**:
"""

VERIFY_REDUCER_MEMORY_MD = """# Agent memory: verify-reducer

Store lessons for identifying the first actionable failure and updating scorecards honestly.

## Entry template

## Failure reduction pattern: <name>
- **Failure signature**:
- **How to isolate first actionable failure**:
- **Common misclassification to avoid**:
- **Scorecard update rule**:
- **Links**:
"""

UX_REVIEWER_MEMORY_MD = """# Agent memory: ux-reviewer

Store UX issues verification commonly misses.

## Entry template

## UX trap: <name>
- **Flow / component type**:
- **What usually gets missed**:
- **Why automation misses it**:
- **Review prompt / checklist**:
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

RUNS_README_MD = """# Local runs

This directory stores **episodic run artifacts** for xlfg.

Default policy:
- keep locally
- do not commit by default
- promote reusable lessons into `docs/xlfg/knowledge/` via `/xlfg:compound`

If you intentionally want to share a specific run, copy or export the relevant files instead of flipping the whole directory to tracked mode.
"""

MIGRATION_NOTES: Dict[str, List[str]] = {
    "2.0.1": [
        "`/xlfg` now treats scaffold bootstrap as a fast prepare/migrate check instead of mandatory init.",
        "`docs/xlfg/runs/` is now gitignored by default; durable knowledge remains tracked.",
        "Added `docs/xlfg/knowledge/agent-memory/` for role-specific compounded memory.",
    ]
}


def _manifest(tool_version: str) -> Dict[str, Any]:
    return {
        "tool_version": tool_version,
        "scaffold_schema_version": SCAFFOLD_SCHEMA_VERSION,
        "run_tracking": "local-only",
        "knowledge_tracking": "tracked",
        "agent_memory": "enabled",
    }


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def scaffold_status(root: Path, tool_version: str) -> Dict[str, Any]:
    docs_dir = root / "docs" / "xlfg"
    meta_path = docs_dir / "meta.json"
    meta = _read_json(meta_path) or {}
    exists = docs_dir.exists() and (docs_dir / "knowledge").exists()
    current_version = str(meta.get("tool_version") or "") if meta else ""
    return {
        "exists": exists,
        "meta_path": str(meta_path),
        "current_tool_version": current_version or None,
        "target_tool_version": tool_version,
        "needs_bootstrap": not exists,
        "needs_migration": bool(exists and current_version and current_version != tool_version),
    }


def _write_migration_note(root: Path, from_version: str, to_version: str) -> Optional[str]:
    if not from_version or from_version == to_version:
        return None
    migrations_dir = root / "docs" / "xlfg" / "migrations"
    ensure_dir(migrations_dir)
    note_path = migrations_dir / f"{from_version}-to-{to_version}.md"
    bullets = MIGRATION_NOTES.get(
        to_version,
        [
            "Scaffold files were refreshed to match the new xlfg version.",
            "Review the repository CHANGELOG for any manual follow-up.",
        ],
    )
    content = [f"# xlfg migration {from_version} → {to_version}", "", "Applied changes:", ""]
    content.extend([f"- {bullet}" for bullet in bullets])
    content.extend([
        "",
        "Manual follow-up:",
        "",
        "- Review the plugin CHANGELOG in `plugins/xlfg-engineering/CHANGELOG.md`.",
    ])
    note_path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return str(note_path.relative_to(root))


def ensure_scaffold(root: Path, tool_version: str) -> Dict[str, Any]:
    """Create or migrate xlfg scaffolding under root.

    Idempotent for unchanged versions. Does not overwrite user-authored files.
    """

    created: List[str] = []
    updated: List[str] = []
    notes: List[str] = []

    status = scaffold_status(root, tool_version)
    previous_version = status.get("current_tool_version") or None

    ensure_dir(root / "docs" / "xlfg" / "knowledge")
    ensure_dir(root / "docs" / "xlfg" / "knowledge" / "agent-memory")
    ensure_dir(root / "docs" / "xlfg" / "migrations")
    ensure_dir(root / "docs" / "xlfg" / "runs")
    ensure_dir(root / ".xlfg" / "runs")

    gitignore_path = root / ".gitignore"
    for line in (
        ".xlfg/",
        "docs/xlfg/runs/*",
        "!docs/xlfg/runs/.gitkeep",
        "!docs/xlfg/runs/README.md",
    ):
        if append_unique_line(gitignore_path, line):
            updated.append(str(gitignore_path.relative_to(root)))

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
        "docs/xlfg/knowledge/agent-memory/README.md": AGENT_MEMORY_INDEX_MD,
        "docs/xlfg/knowledge/agent-memory/root-cause-analyst.md": ROOT_CAUSE_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/test-strategist.md": TEST_STRATEGIST_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/env-doctor.md": ENV_DOCTOR_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/task-implementer.md": TASK_IMPLEMENTER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/verify-reducer.md": VERIFY_REDUCER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/ux-reviewer.md": UX_REVIEWER_MEMORY_MD,
        "docs/xlfg/runs/.gitkeep": "",
        "docs/xlfg/runs/README.md": RUNS_README_MD,
    }

    for rel_path, content in files.items():
        if safe_write(root / rel_path, content):
            created.append(rel_path)

    migration_note: Optional[str] = None
    if previous_version and previous_version != tool_version:
        migration_note = _write_migration_note(root, previous_version, tool_version)
        if migration_note:
            created.append(migration_note)
            notes.append(f"Applied migration note {migration_note}")

    meta_path = root / "docs" / "xlfg" / "meta.json"
    desired_manifest = _manifest(tool_version)
    current_manifest = _read_json(meta_path)
    if current_manifest != desired_manifest:
        meta_path.write_text(json.dumps(desired_manifest, indent=2) + "\n", encoding="utf-8")
        updated.append(str(meta_path.relative_to(root)))

    if status["needs_bootstrap"]:
        notes.append("Bootstrapped xlfg scaffold.")
    elif status["needs_migration"]:
        notes.append(f"Migrated xlfg scaffold from {previous_version} to {tool_version}.")
    else:
        notes.append("Scaffold already current; prepare check passed with no migration.")

    return {
        "created": created,
        "updated": sorted(set(updated)),
        "needs_bootstrap": bool(status["needs_bootstrap"]),
        "needs_migration": bool(status["needs_migration"]),
        "previous_tool_version": previous_version,
        "tool_version": tool_version,
        "migration_note": migration_note,
        "notes": notes,
    }


def init_scaffold(root: Path, tool_version: str) -> Dict[str, Any]:
    """Backward-compatible alias for ensure_scaffold."""
    return ensure_scaffold(root, tool_version)
