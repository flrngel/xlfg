from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .gitmeta import write_worktree_context
from .knowledge import AGENT_MEMORY_ROLES, SHARED_CARD_KINDS, ensure_knowledge_layout, rebuild_views
from .util import append_unique_line, ensure_dir, safe_write, write_text_if_changed

SCAFFOLD_SCHEMA_VERSION = 7

INDEX_MD = """# xlfg

This folder is the **file-based context** system-of-record for `/xlfg` work.

## Why the knowledge model changed

Concurrent xlfg runs across multiple git branches or linked worktrees were fighting over the same tracked rollup files (`current-state.md`, `patterns.md`, `ledger.jsonl`, role memory docs). That created avoidable merge conflicts and turned compounding into a git tax.

xlfg now uses a **branch-safe write model**:

- tracked immutable knowledge cards under `knowledge/cards/`
- tracked immutable event files under `knowledge/events/`
- tracked immutable role-memory cards under `knowledge/agent-memory/<role>/cards/`
- local generated read models under `knowledge/_views/`

This is a CQRS / event-sourcing style split: **write immutable facts, project local views**.

## Structure

Tracked durable knowledge:

- `knowledge/service-context.md` — stable human-owned repo / product context
- `knowledge/write-model.md` — branch-safe knowledge rules
- `knowledge/cards/<kind>/<branch-slug>/...` — immutable shared knowledge cards
- `knowledge/events/<branch-slug>/...json` — immutable durable memory events
- `knowledge/agent-memory/<role>/cards/<branch-slug>/...` — immutable role memory cards
- `knowledge/queries.md` — deterministic recall query syntax
- `knowledge/commands.json` — canonical verification and dev-server commands
- `meta.json` — scaffold version + migration state
- `migrations/` — migration notes when the xlfg version changes

Local generated views (gitignored):

- `knowledge/_views/current-state.md` — concise next-agent handoff for this worktree
- `knowledge/_views/*.md` — local projections of shared knowledge cards
- `knowledge/_views/agent-memory/*.md` — local projections of role memory cards
- `knowledge/_views/ledger.jsonl` — generated ledger view from immutable event files
- `knowledge/_views/worktree.md` — branch / worktree context for this checkout

Local run evidence (gitignored by default):

- `runs/` — one folder per run containing why, diagnosis, solution decisions, harness profiles, contracts, plans, workboards, proof maps, reviews, and summaries
- `.xlfg/runs/` — raw command outputs, screenshots, traces, doctor reports
- `.xlfg/worktree.json` — local git worktree context cache

## The important rule

**Do not hand-edit generated views on feature branches.**

Create or update immutable cards / events, then regenerate `_views/`. This keeps the read interface friendly while making the write path conflict-resistant.
"""

SERVICE_CONTEXT_MD = """# service context

This is the small tracked document humans or lead agents may edit when the enduring product / service context changes.

Keep it stable and high-signal:

- what the service does
- who the key users / operators are
- high-level constraints that survive across many runs
- major non-goals / invariants

Do **not** dump per-run lessons here. Those belong in cards and events.
"""

WRITE_MODEL_MD = """# xlfg knowledge write model

xlfg uses a **branch-safe write path** to avoid merge conflicts when multiple branches or git worktrees compound knowledge at the same time.

## Write path (tracked)

### Shared knowledge cards

Create immutable markdown cards under:

- `docs/xlfg/knowledge/cards/current-state/<branch-slug>/...`
- `docs/xlfg/knowledge/cards/patterns/<branch-slug>/...`
- `docs/xlfg/knowledge/cards/decision-log/<branch-slug>/...`
- `docs/xlfg/knowledge/cards/testing/<branch-slug>/...`
- `docs/xlfg/knowledge/cards/ux-flows/<branch-slug>/...`
- `docs/xlfg/knowledge/cards/failure-memory/<branch-slug>/...`
- `docs/xlfg/knowledge/cards/harness-rules/<branch-slug>/...`
- `docs/xlfg/knowledge/cards/quality-bar/<branch-slug>/...`

### Role memory cards

Create immutable role cards under:

- `docs/xlfg/knowledge/agent-memory/<role>/cards/<branch-slug>/...`

### Durable event files

Create one JSON file per admitted lesson under:

- `docs/xlfg/knowledge/events/<branch-slug>/...json`

## Read path (local only)

Never treat the tracked cards as the only human-facing interface. Regenerate local projections under:

- `docs/xlfg/knowledge/_views/current-state.md`
- `docs/xlfg/knowledge/_views/*.md`
- `docs/xlfg/knowledge/_views/agent-memory/*.md`
- `docs/xlfg/knowledge/_views/ledger.jsonl`

`/xlfg:prepare` and `xlfg knowledge rebuild` refresh these views.

## Filename convention

Prefer:

`<UTC timestamp>--<run-id>--<slug>.md`

or for events:

`<UTC timestamp>--<run-id>--<slug>.json`

Put the file inside the current branch slug directory so independent branches almost never touch the same path.

## Admission rule

Only promote lessons that are:

- concrete
- reusable
- evidenced by verification, review, or repeated real failure
- small enough to retrieve directly

## Things not to do

- do not append to shared tracked rollup docs on feature branches
- do not keep a single tracked `ledger.jsonl` as the source of truth
- do not overwrite old cards in place; supersede them with a new event / card
- do not store noisy raw run output in tracked knowledge
"""

QUALITY_BAR_SEED = """# quality bar seed

Quality gates are ultimately enforced through run files (`flow-spec.md`, `test-contract.md`, `proof-map.md`, `scorecard.md`) and promoted via quality-bar cards.

Use cards under `docs/xlfg/knowledge/cards/quality-bar/` when a run discovers a missing gate that should persist.
"""

QUERIES_MD = """# xlfg recall query syntax

xlfg recall is deterministic and lexical. It reads the local `_views/` projections, tracked cards, immutable event files, and local runs.

## Plain query

A plain query is treated as an exact lexical search:

```
xlfg recall 'login button enter submit'
```

If the plain query is a supported date expression, xlfg does temporal recall instead:

```
xlfg recall yesterday
xlfg recall last week
xlfg recall 2026-03-06
```

## Typed query document

Each non-empty line is `type: value`. Supported types:
- `lex:` quoted phrases + negation + exact lexical terms
- `kind:` filter memory kind(s)
- `stage:` filter SDLC stage(s)
- `role:` filter role memory
- `scope:` filter `knowledge`, `agent-memory`, `ledger`, `runs`, `migrations`, `memory`, or `all`
- `path:` substring filter on relative path
- `when:` temporal filter (`today`, `yesterday`, `last week`, `YYYY-MM-DD`, `last 7 days`)

Example:

```
lex: "login button" enter -oauth
stage: plan verify
kind: testing harness-rule
role: test-strategist env-doctor
scope: memory runs
when: last 14 days
```

## Query order of operations

1. Read `docs/xlfg/knowledge/_views/current-state.md` if present
2. Search `_views/` for concise read models
3. Fall back to tracked cards / event files for exact provenance
4. Search local runs only when durable memory was not enough

This mode is intentionally precision-first and auditable.
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

CARDS_README_MD = """# knowledge cards

Each directory under here is a **kind** of durable knowledge card.

Write rules:
- create immutable cards
- namespace by branch slug
- never hand-edit generated `_views/` files
- supersede stale cards with a new card + event instead of rewriting history
"""

EVENTS_README_MD = """# knowledge events

This directory stores immutable JSON event files that back the generated ledger view.

One file per event keeps the write path branch-safe and easier to merge than a single append-only tracked JSONL file.
"""

AGENT_MEMORY_INDEX_MD = """# xlfg agent memory

Role memory exists for agents that repeatedly hit the same failure classes.

Role memory now follows the same conflict-resistant pattern as shared knowledge:

- tracked cards under `docs/xlfg/knowledge/agent-memory/<role>/cards/<branch-slug>/...`
- local generated views under `docs/xlfg/knowledge/_views/agent-memory/<role>.md`

Admission rules:
- specific to the role's job
- validated by verification, review, or repeated successful reuse
- short enough to retrieve quickly
- better expressed as a rule / checklist / anti-pattern than a full summary
"""

ROLE_README_TEMPLATE = """# agent memory: {role}

Write immutable cards under `cards/<branch-slug>/...` when a lesson is clearly role-specific.

Do not edit local generated views by hand.
"""

RUNS_README_MD = """# Local runs

This directory stores **episodic run artifacts** for xlfg.

Default policy:
- keep locally
- do not commit by default
- promote reusable lessons into `docs/xlfg/knowledge/cards/` and `docs/xlfg/knowledge/events/` via `/xlfg:compound`

If you intentionally want to share a specific run, copy or export the relevant files instead of flipping the whole directory to tracked mode.
"""

MIGRATION_NOTES: Dict[str, List[str]] = {
    "2.0.6": [
        "Shared knowledge and role memory now write to immutable branch-scoped cards instead of hot tracked rollup files.",
        "Immutable event files now replace the single tracked ledger.jsonl as the source of truth; `knowledge/_views/ledger.jsonl` is generated locally.",
        "Prepare now records git worktree context and rebuilds local knowledge views under `docs/xlfg/knowledge/_views/`.",
    ],
    "2.0.5": [
        "Added `why.md`, `harness-profile.md`, `workboard.md`, and `proof-map.md` to every run scaffold.",
        "`/xlfg` now selects verification depth from the run’s harness profile instead of always assuming a full run.",
        "Added `why-analyst` and `harness-profiler` role memory plus the bundle-level DeerFlow harness review notes.",
    ],
    "2.0.4": [
        "`/xlfg` now requires deterministic recall before planning.",
        "Added `docs/xlfg/knowledge/current-state.md` as the tracked handoff document for the next agent.",
        "Expanded role-memory scaffolds for more planning, implementation, and review specialists.",
    ],
    "2.0.3": [
        "Added deterministic `xlfg recall` over durable knowledge, role memory, the append-only ledger, and local runs.",
        "Introduced `docs/xlfg/knowledge/ledger.jsonl` and recall query syntax docs for stage- and role-aligned retrieval.",
        "Compounding now has a structured append-only memory target instead of relying only on prose markdown files.",
    ],
    "2.0.2": [
        "Status / prepare now distinguish installed xlfg version from repo scaffold version.",
        "Legacy docs/xlfg/metadata.json is normalized to the canonical docs/xlfg/meta.json format.",
        "Prepare reports the source of the repo scaffold version to avoid stale-file confusion.",
    ],
    "2.0.1": [
        "`/xlfg` now treats scaffold bootstrap as a fast prepare/migrate check instead of mandatory init.",
        "`docs/xlfg/runs/` is now gitignored by default; durable knowledge remains tracked.",
        "Added `docs/xlfg/knowledge/agent-memory/` for role-specific compounded memory.",
    ],
}


def _manifest(tool_version: str) -> Dict[str, Any]:
    return {
        "tool_version": tool_version,
        "scaffold_schema_version": SCAFFOLD_SCHEMA_VERSION,
        "run_tracking": "local-only",
        "knowledge_write_model": "branch-safe-cards",
        "knowledge_read_model": "generated-local-views",
        "current_state": "local-view",
        "service_context": "tracked-seed",
        "agent_memory": "branch-safe-cards+views",
        "recall": "deterministic-lexical",
        "memory_events": "sharded-json-files",
        "why_file": "required",
        "harness_profiles": "quick-standard-deep",
        "workboard": "required",
        "proof_map": "required",
        "worktree_awareness": "enabled",
    }


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_version(meta: Optional[Dict[str, Any]]) -> tuple[Optional[str], Optional[str]]:
    if not meta:
        return None, None
    for key in ("tool_version", "version", "scaffold_version"):
        value = meta.get(key)
        if value:
            return str(value), key
    return None, None


def _meta_state(docs_dir: Path) -> Dict[str, Any]:
    canonical = docs_dir / "meta.json"
    legacy = docs_dir / "metadata.json"

    if canonical.exists():
        data = _read_json(canonical) or {}
        version, version_key = _extract_version(data)
        return {
            "canonical_path": canonical,
            "legacy_path": legacy if legacy.exists() else None,
            "source_path": canonical,
            "data": data,
            "version": version,
            "version_key": version_key,
            "source_kind": "canonical",
        }

    if legacy.exists():
        data = _read_json(legacy) or {}
        version, version_key = _extract_version(data)
        return {
            "canonical_path": canonical,
            "legacy_path": legacy,
            "source_path": legacy,
            "data": data,
            "version": version,
            "version_key": version_key,
            "source_kind": "legacy",
        }

    return {
        "canonical_path": canonical,
        "legacy_path": legacy if legacy.exists() else None,
        "source_path": canonical,
        "data": None,
        "version": None,
        "version_key": None,
        "source_kind": "missing",
    }


def scaffold_status(root: Path, tool_version: str) -> Dict[str, Any]:
    docs_dir = root / "docs" / "xlfg"
    meta = _meta_state(docs_dir)
    exists = docs_dir.exists() and (docs_dir / "knowledge").exists()
    repo_version = meta.get("version")
    needs_meta_sync = bool(
        exists and (
            meta.get("source_kind") != "canonical"
            or repo_version is None
            or repo_version != tool_version
        )
    )
    version_source = None
    if meta.get("source_path") and meta.get("version_key"):
        version_source = f"{Path(meta['source_path']).name}:{meta['version_key']}"
    return {
        "exists": exists,
        "meta_path": str(meta["canonical_path"]),
        "legacy_meta_path": str(meta["legacy_path"]) if meta.get("legacy_path") else None,
        "version_source": version_source,
        "repo_scaffold_version": repo_version,
        "installed_tool_version": tool_version,
        "target_tool_version": tool_version,
        "needs_bootstrap": not exists,
        "needs_meta_sync": needs_meta_sync,
        "needs_migration": bool(exists and repo_version and repo_version != tool_version),
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
        "- If this repo still edits tracked rollup docs directly, move future knowledge writes into cards / events and let prepare rebuild local views.",
    ])
    note_path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return str(note_path.relative_to(root))


def ensure_scaffold(root: Path, tool_version: str) -> Dict[str, Any]:
    created: List[str] = []
    updated: List[str] = []
    notes: List[str] = []

    status = scaffold_status(root, tool_version)
    previous_version = status.get("repo_scaffold_version") or None

    ensure_dir(root / "docs" / "xlfg" / "knowledge")
    ensure_dir(root / "docs" / "xlfg" / "migrations")
    ensure_dir(root / "docs" / "xlfg" / "runs")
    ensure_dir(root / ".xlfg" / "runs")

    gitignore_path = root / ".gitignore"
    for line in (
        ".xlfg/",
        "docs/xlfg/runs/*",
        "!docs/xlfg/runs/.gitkeep",
        "!docs/xlfg/runs/README.md",
        "docs/xlfg/knowledge/_views/",
    ):
        if append_unique_line(gitignore_path, line):
            updated.append(str(gitignore_path.relative_to(root)))

    files = {
        "docs/xlfg/index.md": INDEX_MD,
        "docs/xlfg/knowledge/service-context.md": SERVICE_CONTEXT_MD,
        "docs/xlfg/knowledge/write-model.md": WRITE_MODEL_MD,
        "docs/xlfg/knowledge/quality-bar-seed.md": QUALITY_BAR_SEED,
        "docs/xlfg/knowledge/queries.md": QUERIES_MD,
        "docs/xlfg/knowledge/commands.json": COMMANDS_JSON,
        "docs/xlfg/knowledge/cards/README.md": CARDS_README_MD,
        "docs/xlfg/knowledge/events/README.md": EVENTS_README_MD,
        "docs/xlfg/knowledge/agent-memory/README.md": AGENT_MEMORY_INDEX_MD,
        "docs/xlfg/runs/.gitkeep": "",
        "docs/xlfg/runs/README.md": RUNS_README_MD,
    }
    for role in AGENT_MEMORY_ROLES:
        files[f"docs/xlfg/knowledge/agent-memory/{role}/README.md"] = ROLE_README_TEMPLATE.format(role=role)

    ensure_knowledge_layout(root)

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

    legacy_meta_path = root / "docs" / "xlfg" / "metadata.json"
    if legacy_meta_path.exists():
        legacy_manifest = {
            **desired_manifest,
            "deprecated": True,
            "canonical_path": "docs/xlfg/meta.json",
        }
        current_legacy_manifest = _read_json(legacy_meta_path)
        if current_legacy_manifest != legacy_manifest:
            legacy_meta_path.write_text(json.dumps(legacy_manifest, indent=2) + "\n", encoding="utf-8")
            updated.append(str(legacy_meta_path.relative_to(root)))
            notes.append("Normalized legacy docs/xlfg/metadata.json to mirror docs/xlfg/meta.json.")

    worktree_info = write_worktree_context(root)
    if worktree_info.get("changed"):
        updated.append(worktree_info["path"])

    views = rebuild_views(root)
    updated.extend(views.get("updated", []))

    if status["needs_bootstrap"]:
        notes.append("Bootstrapped xlfg scaffold.")
    elif status["needs_migration"]:
        notes.append(f"Migrated xlfg scaffold from {previous_version} to {tool_version}.")
    elif status.get("needs_meta_sync"):
        notes.append("Synchronized scaffold metadata to the canonical docs/xlfg/meta.json format.")
    else:
        notes.append("Scaffold already current; prepare check passed with no migration.")

    notes.append("Rebuilt local knowledge views from tracked cards and event files.")

    return {
        "created": created,
        "updated": sorted(set(updated)),
        "needs_bootstrap": bool(status["needs_bootstrap"]),
        "needs_meta_sync": bool(status.get("needs_meta_sync")),
        "needs_migration": bool(status["needs_migration"]),
        "previous_repo_scaffold_version": previous_version,
        "previous_tool_version": previous_version,
        "installed_tool_version": tool_version,
        "repo_scaffold_version": tool_version,
        "tool_version": tool_version,
        "migration_note": migration_note,
        "worktree": worktree_info["data"],
        "views_updated": views.get("updated", []),
        "notes": notes,
    }


def init_scaffold(root: Path, tool_version: str) -> Dict[str, Any]:
    return ensure_scaffold(root, tool_version)
