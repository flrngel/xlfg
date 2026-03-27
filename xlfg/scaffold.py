from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import append_unique_line, ensure_dir, safe_write

SCAFFOLD_SCHEMA_VERSION = 12

INDEX_MD = """# xlfg

This folder is the **file-based context** system-of-record for `/xlfg` work.

## Structure

Tracked durable knowledge:

- `knowledge/` — current state, patterns, decisions, testing knowledge, UX flows, harness rules, role-specific memories, and an append-only memory ledger (commit this)
- `meta.json` — scaffold version + migration state (commit this)
- `migrations/` — migration notes when the xlfg version changes (commit this)

Local run evidence (do not commit by default):

- `runs/` — one folder per run containing the lean run card, proof, status, and optional deep-dive docs only when they changed a decision
- `.xlfg/runs/` — raw command outputs, screenshots, traces, doctor reports

## Why `runs/` is local-only by default

Run folders are valuable as **episodic memory** and debugging evidence, but they create high-churn git noise, often include machine-local paths and transient failures, and are usually too verbose to serve as durable knowledge. xlfg therefore keeps:

- `docs/xlfg/runs/` — **local by default** (gitignored, except placeholders)
- `docs/xlfg/knowledge/` — **tracked** and curated
- `.xlfg/` — **ephemeral** and gitignored

Promote only the reusable lesson, not the entire run.

## Merge-friendly knowledge policy

To reduce PR conflicts across concurrent worktrees and branches:

- shared knowledge files are **append-only by default**
- xlfg scaffolds `.gitattributes` rules so append-only knowledge files use Git's **union** merge driver
- `current-state.md` is treated as a **stable tracked brief**, not a hot file for every feature branch
- when a non-default branch learns something branch-local, `/xlfg:compound` should write `current-state-candidate.md` inside the run folder instead of rewriting the tracked brief

This keeps retrieval simple: read the tracked brief first for repo-wide truths, then read the latest local candidate for the current branch if one exists.

## Core workflow contract

Normal `/xlfg` runs should auto-execute recall → intent → context → plan → implement → verify → review → compound in one invocation. Minimal scaffold sync may happen silently when needed.

The lean core run files are:

1. `context.md` — request and constraints snapshot
2. `memory-recall.md` — the smallest relevant prior knowledge slice
3. `spec.md` — the **single source of truth** for the intent contract, PM / UX / Engineering / QA / Release
4. `test-contract.md` — concise practical scenario contracts with fast proof + ship proof
5. `test-readiness.md` — READY / REVISE gate for whether those scenarios are honest enough to code against
6. `workboard.md` — run-level stage + task ledger

Optional deep-dive files such as `research.md`, `diagnosis.md`, `solution-decision.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, and `risk.md` should exist only when they reduce ambiguity or risk.

## Agent memory model

xlfg compounds in two layers:

1. **`current-state.md`** as the shortest tracked handoff for the next agent
2. **Shared memory** in `knowledge/` for repo-wide rules and patterns
3. **Role memory** in `knowledge/agent-memory/` for agents that repeatedly need the same lessons
4. **Memory ledger** in `knowledge/ledger.jsonl` for append-only, structured durable memory events

Keep `current-state.md` short and current. Role memory must stay small, typed, and admission-gated. Do not dump raw run summaries there. The ledger is append-only; corrections should supersede old entries rather than silently rewriting them.
"""

QUALITY_BAR_MD = """# xlfg quality bar

Nothing is "done" unless:

- **The run card is explicit** (`spec.md` exists and keeps the intent contract, objective groups, non-goals, outcome, risks, and proof commitments visible)
- **Recall is honest** (`memory-recall.md` records real hits or a clear no-hit)
- **Test intent is shared** (`test-contract.md` maps concise scenario contracts to practical fast proof and ship proof)
- **Test readiness is explicit** (`test-readiness.md` is `READY` before coding or clearly explains why planning must be revised)
- **New behavior is proven** by scenario-targeted checks that were defined before implementation (Fail → Pass)
- **Existing behavior is preserved** with relevant guard coverage (Pass → Pass)
- **Lint / typecheck / build** pass when applicable
- **User-facing flows are validated** (happy path, alternates, failure path, a11y)
- **Workboard is current** (`workboard.md` reflects stage / task truth and reminds the agent it owns the work)
- **Verification is honest** (`verification.md` records exact commands, artifacts, and the first actionable failure when red)
- **Unexpected failures are compounded** into failure memory / harness rules / role memory when warranted
- **No monkey fix is misrepresented as the final solution** (bounded workarounds are labeled honestly)
- **Operational plan exists** (monitoring + rollback notes)

Optional files such as `research.md`, `diagnosis.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, and `review-summary.md` should exist only when they materially reduce risk or ambiguity.
"""

CURRENT_STATE_MD = """# xlfg current state

Read this file first when entering a repo that uses xlfg. It is the shortest tracked handoff for the next agent.

## Service / product context
- What is this repo / service trying to do right now?

## Current high-signal truths
- The most important facts that should shape new work immediately
- Any request-shaping rule that repeatedly prevents dropped implied asks or monkey fixes

## Active UX / behavior contracts
- Flows or invariants that repeatedly matter

## Current harness / verification rules
- Ports, healthchecks, non-interactive rules, dev-server reuse rules

## Repeated failures to avoid
- The recurring failure signatures and the proven first response

## Open risks / debts
- Things the next agent should keep in mind before touching risky areas

## Best starting recall queries
- One or two exact lexical or typed queries that load the right memory fast

Keep this document short, current, and biased toward actionable truths. Historical detail belongs in the ledger, shared knowledge files, or local runs.

Merge rule: prefer updating this file only on the default branch (`main`, `master`, or `trunk`) or when the user explicitly asks to promote a repo-wide handoff. Feature branches should usually write a local `current-state-candidate.md` inside the run folder instead.
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

MEMORY_LEDGER_MD = """# xlfg memory ledger

`ledger.jsonl` is the machine-readable durable memory store for xlfg.

Why it exists:
- append-only audit trail for compounded lessons
- stage- and role-aligned retrieval without prompt bloat
- deterministic recall over exact text, tags, and filters

## Event shape

One JSON object per line. Preferred event types:
- `memory.added`
- `memory.superseded`
- `memory.invalidated`

Recommended fields for `memory.added`:

```json
{
  "id": "mem-20260306-01",
  "event": "memory.added",
  "created_at": "2026-03-06T12:34:56Z",
  "run_id": "20260306-123456-login-flow",
  "kind": "harness-rule",
  "stage": "verify",
  "role": "env-doctor",
  "title": "Reuse healthy dev server before starting another one",
  "summary": "Check the configured health endpoint first and reuse a healthy process.",
  "symptom": "`yarn dev` started twice and the second process failed with EADDRINUSE.",
  "root_cause": "The harness assumed no existing server and skipped readiness reuse.",
  "action": "Probe health, reuse if healthy, otherwise kill stale PID and restart once.",
  "prevention": "Never spawn a second dev server without a health check.",
  "lex": "yarn dev EADDRINUSE duplicate server port already in use healthcheck reuse",
  "tags": ["yarn", "dev-server", "port", "healthcheck"],
  "evidence": ["docs/xlfg/runs/<run-id>/verification.md"],
  "status": "active"
}
```

## Admission rules

Only append a memory event when the lesson is:
- concrete
- reusable
- evidenced by verification, review, or repeated real failure
- small enough to retrieve directly

Do not store vague summaries or speculative advice.
"""

QUERIES_MD = """# xlfg recall query syntax

xlfg recall uses deterministic typed query documents inspired by QMD's query documents, but **without vector search, HyDE, or LLM expansion**. Always read `current-state.md` first.

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
- `scope:` filter `knowledge`, `agent-memory`, `ledger`, `runs`, `migrations`, `memory`, or `all` (with `current-state.md` living under `knowledge`)
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

## Lex rules

- `word` → exact token / prefix-like lexical match
- `"phrase"` → exact phrase
- `-word` → exclude results containing the word
- `-"phrase"` → exclude results containing the phrase

This mode is intentionally precision-first and auditable.
"""

LEDGER_JSONL = """"""

AGENT_MEMORY_INDEX_MD = """# xlfg agent memory

Role memory exists for agents that repeatedly hit the same failure classes.

## Admission rules

Only compound something into role memory when it is:

- specific to the role's job
- validated by verification, review, or repeated successful reuse
- short enough to retrieve quickly
- better expressed as a rule / checklist / anti-pattern than a full summary

## Files

- `query-refiner.md`
- `why-analyst.md`
- `root-cause-analyst.md`
- `harness-profiler.md`
- `solution-architect.md`
- `test-strategist.md`
- `env-doctor.md`
- `test-implementer.md`
- `task-implementer.md`
- `task-checker.md`
- `verify-reducer.md`
- `ux-reviewer.md`
- `architecture-reviewer.md`
- `security-reviewer.md`
- `performance-reviewer.md`
- `test-readiness-checker.md`
"""

QUERY_REFINER_MEMORY_MD = """# Agent memory: query-refiner

Store reusable request-shaping lessons that help preserve what the user actually asked for.

## Entry template

## Query pattern: <name>
- **Raw request shape**:
- **Direct asks that often get dropped**:
- **Implied asks that must stay visible**:
- **Developer / product intention to preserve**:
- **Common monkey fix to reject**:
- **Best carry-forward anchor**:
- **Links**:
"""


WHY_ANALYST_MEMORY_MD = """# Agent memory: why-analyst

Store reusable product-intent patterns that keep runs anchored to the real user or operator value.

## Entry template

## Why pattern: <name>
- **Request shape**:
- **Real stakeholder / user**:
- **What false success looks like**:
- **Quality bar that matters**:
- **Links**:
"""

HARNESS_PROFILER_MEMORY_MD = """# Agent memory: harness-profiler

Store rules for choosing the minimum harness intensity that still gives honest proof.

## Entry template

## Profile rule: <name>
- **Problem / repo shape**:
- **Choose profile**: quick | standard | deep
- **Why this profile is sufficient**:
- **Escalation trigger**:
- **Links**:
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

SOLUTION_ARCHITECT_MEMORY_MD = """# Agent memory: solution-architect

Store solution-selection rules that repeatedly pick the right layer and reject the wrong shortcut.

## Entry template

## Decision pattern: <name>
- **Problem shape**:
- **Correct layer for the fix**:
- **Shortcut to reject**:
- **Tradeoff notes**:
- **Disconfirming signal**:
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

TEST_IMPLEMENTER_MEMORY_MD = """# Agent memory: test-implementer

Store tactical testing patterns for proving scenario contracts honestly.

## Entry template

## Test pattern: <name>
- **Scenario shape**:
- **Fast honest proof**:
- **When smoke / e2e is still required**:
- **Wrong-green trap**:
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

TASK_CHECKER_MEMORY_MD = """# Agent memory: task-checker

Store recurring acceptance / rejection rules for scoped task reviews.

## Entry template

## Review pattern: <name>
- **Task shape**:
- **Most common hidden drift**:
- **Acceptance evidence required**:
- **Common false green**:
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

ARCHITECTURE_REVIEWER_MEMORY_MD = """# Agent memory: architecture-reviewer

Store recurring architecture drift patterns that deserve fast review attention.

## Entry template

## Drift pattern: <name>
- **System shape**:
- **What tends to drift**:
- **Correct boundary / layering rule**:
- **Why verification often misses it**:
- **Links**:
"""

SECURITY_REVIEWER_MEMORY_MD = """# Agent memory: security-reviewer

Store recurring security review traps that are easy to miss during fast implementation.

## Entry template

## Security trap: <name>
- **Flow type**:
- **Sensitive boundary**:
- **What often slips through**:
- **Required review question**:
- **Links**:
"""

PERFORMANCE_REVIEWER_MEMORY_MD = """# Agent memory: performance-reviewer

Store recurring performance or iteration-speed traps worth checking quickly.

## Entry template

## Performance trap: <name>
- **Path / system type**:
- **What usually gets slow**:
- **Fast signal to inspect**:
- **Why it matters to iteration or production**:
- **Links**:
"""


TEST_READINESS_CHECKER_MEMORY_MD = """# Agent memory: test-readiness-checker

Store recurring rules for deciding whether a planned test contract is concrete enough to code against.

## Entry template

## Readiness rule: <name>
- **Scenario shape**:
- **What made the contract READY**:
- **What forced REVISE**:
- **Fast proof rule**:
- **Ship proof rule**:
- **Wrong-green trap avoided**:
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
- keep branch/worktree-specific handoffs such as `current-state-candidate.md` here to avoid hot-file merge conflicts

If you intentionally want to share a specific run, copy or export the relevant files instead of flipping the whole directory to tracked mode.
"""

MIGRATION_NOTES: Dict[str, List[str]] = {
    "2.6.0": [
        "Hardened specialist agents with explicit tool allowlists, proactive delegation descriptions, and foreground-only execution hints.",
        "Review specialists now write lane artifacts under docs/xlfg/runs/<run>/reviews/ so the conductor can synthesize from real expert output.",
        "Added standalone .claude/agents parity plus stronger audit and test coverage for subagent execution quality.",
    ],
    "2.5.1": [
        "Intent resolution now lives inside spec.md; xlfg no longer relies on a separate query-contract file during active runs.",
        "Added a mandatory intent phase before broad repo fan-out so messy prompts are split into objective groups with explicit assumptions or blockers.",
        "Added xlfg eval-intent plus artifact-graded fixtures so bad prompts can be scored for ask recall, objective splitting, blocker handling, and false assumptions.",
    ],
    "2.0.10": [
        "`/xlfg` no longer treats scaffold sync as a routine prepare stage; normal runs start from recall and planning.",
        "Planning now uses a simpler lead-owned model: fewer routine subagents, three explicit planning states (semantic / structural / execution), and agent-owned execution by default.",
        "Run templates now record execution ownership explicitly and remove the stale prepare stage from workboard state.",
    ],
    "2.0.9": [
        "Added `test-readiness.md` to every run scaffold as a hard plan gate before implementation.",
        "Verification now compiles scenario-targeted checks from `test-contract.md` and stays RED when changed scenarios lack practical proof.",
        "Planning and checker-style agents now bias toward concise scenario contracts, minimal context, and bounded execution budgets.",
    ],
    "2.0.8": [
        "Added `query-contract.md` to every run scaffold (historical; active intent handling now lives inside spec.md).",
        "Planning now starts by separating direct asks, implied asks, functionality/quality requirements, and solution constraints before broad repo fan-out.",
        "Implementation, verification, and review now re-read the query carry-forward anchor to reduce request drift and monkey fixes.",
    ],
    "2.0.7": [
        "Scaffold now adds .gitattributes rules so append-only knowledge files use Git's union merge driver.",
        "Shared knowledge files should stay append-only; do not rewrite old entries during compounding.",
        "`current-state.md` is now a stable tracked brief. Feature branches should prefer a run-local `current-state-candidate.md` instead of rewriting it.",
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
    ]
}


def _manifest(tool_version: str) -> Dict[str, Any]:
    return {
        "tool_version": tool_version,
        "scaffold_schema_version": SCAFFOLD_SCHEMA_VERSION,
        "run_tracking": "local-only",
        "knowledge_tracking": "tracked",
        "current_state": "tracked-brief",
        "agent_memory": "enabled",
        "recall": "deterministic-lexical",
        "memory_ledger": "append-only-jsonl",
        "why_file": "required",
        "harness_profiles": "quick-standard-deep",
        "workboard": "required",
        "proof_map": "required",
        "knowledge_merge_strategy": "union-append",
        "current_state_promotion": "default-branch-or-explicit",
        "test_contract_style": "concise-practical-scenarios",
        "test_readiness_gate": "required",
        "workflow_entry": "recall-intent-context-plan-implement-verify-review-compound",
        "intent_contract": "spec-md-ssot",
        "multi_objective_splitter": "objective-groups-in-spec",
        "intent_eval": "artifact-graded",
        "prepare_mode": "manual-maintenance-only",
        "planning_model": "semantic-structural-execution-state",
        "execution_ownership": "agent-owned-except-human-only",
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
    previous_version = status.get("repo_scaffold_version") or None

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

    gitattributes_path = root / ".gitattributes"
    for line in (
        "# xlfg merge-friendly knowledge",
        "docs/xlfg/knowledge/decision-log.md merge=union",
        "docs/xlfg/knowledge/patterns.md merge=union",
        "docs/xlfg/knowledge/testing.md merge=union",
        "docs/xlfg/knowledge/ux-flows.md merge=union",
        "docs/xlfg/knowledge/failure-memory.md merge=union",
        "docs/xlfg/knowledge/harness-rules.md merge=union",
        "docs/xlfg/knowledge/quality-bar.md merge=union",
        "docs/xlfg/knowledge/ledger.jsonl merge=union",
        "docs/xlfg/knowledge/agent-memory/*.md merge=union",
    ):
        if append_unique_line(gitattributes_path, line):
            updated.append(str(gitattributes_path.relative_to(root)))

    files = {
        "docs/xlfg/index.md": INDEX_MD,
        "docs/xlfg/knowledge/current-state.md": CURRENT_STATE_MD,
        "docs/xlfg/knowledge/quality-bar.md": QUALITY_BAR_MD,
        "docs/xlfg/knowledge/decision-log.md": DECISION_LOG_MD,
        "docs/xlfg/knowledge/patterns.md": PATTERNS_MD,
        "docs/xlfg/knowledge/testing.md": TESTING_MD,
        "docs/xlfg/knowledge/ux-flows.md": UX_FLOWS_MD,
        "docs/xlfg/knowledge/failure-memory.md": FAILURE_MEMORY_MD,
        "docs/xlfg/knowledge/harness-rules.md": HARNESS_RULES_MD,
        "docs/xlfg/knowledge/ledger.md": MEMORY_LEDGER_MD,
        "docs/xlfg/knowledge/ledger.jsonl": LEDGER_JSONL,
        "docs/xlfg/knowledge/queries.md": QUERIES_MD,
        "docs/xlfg/knowledge/commands.json": COMMANDS_JSON,
        "docs/xlfg/knowledge/agent-memory/README.md": AGENT_MEMORY_INDEX_MD,
        "docs/xlfg/knowledge/agent-memory/query-refiner.md": QUERY_REFINER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/why-analyst.md": WHY_ANALYST_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/root-cause-analyst.md": ROOT_CAUSE_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/harness-profiler.md": HARNESS_PROFILER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/solution-architect.md": SOLUTION_ARCHITECT_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/test-strategist.md": TEST_STRATEGIST_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/env-doctor.md": ENV_DOCTOR_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/test-implementer.md": TEST_IMPLEMENTER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/task-implementer.md": TASK_IMPLEMENTER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/task-checker.md": TASK_CHECKER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/verify-reducer.md": VERIFY_REDUCER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/ux-reviewer.md": UX_REVIEWER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/architecture-reviewer.md": ARCHITECTURE_REVIEWER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/security-reviewer.md": SECURITY_REVIEWER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/performance-reviewer.md": PERFORMANCE_REVIEWER_MEMORY_MD,
        "docs/xlfg/knowledge/agent-memory/test-readiness-checker.md": TEST_READINESS_CHECKER_MEMORY_MD,
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

    if status["needs_bootstrap"]:
        notes.append("Bootstrapped xlfg scaffold.")
    elif status["needs_migration"]:
        notes.append(f"Migrated xlfg scaffold from {previous_version} to {tool_version}.")
    elif status.get("needs_meta_sync"):
        notes.append("Synchronized scaffold metadata to the canonical docs/xlfg/meta.json format.")
    else:
        notes.append("Scaffold already current; no migration needed.")

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
        "notes": notes,
    }


def init_scaffold(root: Path, tool_version: str) -> Dict[str, Any]:
    """Backward-compatible alias for ensure_scaffold."""
    return ensure_scaffold(root, tool_version)
