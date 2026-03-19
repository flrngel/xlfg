from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import tomllib


CORE_COMMAND_FILES = [
    "xlfg.md",
    "xlfg-plan.md",
    "xlfg-implement.md",
    "xlfg-verify.md",
    "xlfg-review.md",
]

WORD_RE = re.compile(r"[A-Za-z0-9_./:-]+")
FRONTMATTER_RE = re.compile(r"^---\s*$", re.MULTILINE)
MODEL_RE = re.compile(r"^model:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE)
VERSION_RE = re.compile(r'__version__\s*=\s*"([^"]+)"')
SAFE_WRITE_RE = re.compile(r'safe_write\(docs_dir / "([^"]+)"')
READ_DIR_RE = re.compile(r'ensure_dir\(docs_dir / "([^"]+)"\)')
RUN_ID_RE = re.compile(r"xlfg-[a-z0-9-]+")
BULLET_RE = re.compile(r"^[-*]\s+")
CODE_ITEM_RE = re.compile(r"`([^`]+)`|([A-Za-z0-9_.-]+(?:\.md|/))")
BUDGET_LINE_RE = re.compile(r"^[-*]\s*`?(quick|standard|deep)`?\s*:\s*(.+)$", re.IGNORECASE)
NUMBER_RE = re.compile(r"(\d+)")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _load_json(path: Path) -> Optional[dict[str, Any]]:
    try:
        data = json.loads(_read_text(path))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _unique_nonempty(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        item = str(value).strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _extract_section_lines(text: str, markers: list[str]) -> list[str]:
    lines = text.splitlines()
    start = None
    for idx, raw in enumerate(lines):
        lowered = raw.strip().lower()
        if any(marker.lower() in lowered for marker in markers):
            start = idx + 1
            break
    if start is None:
        return []

    items: list[str] = []
    collecting = False
    for raw in lines[start:]:
        stripped = raw.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            if items:
                break
            continue
        if BULLET_RE.match(stripped) or re.match(r"^\d+[.)]\s+", stripped):
            collecting = True
            items.append(stripped)
            continue
        if collecting and not stripped:
            continue
        if collecting and items:
            # Stop once the list is clearly over.
            break
    return items


def _count_list_items(text: str, markers: list[str]) -> int:
    return len(_extract_section_lines(text, markers))


def _extract_markdown_items(text: str, markers: list[str]) -> list[str]:
    items: list[str] = []
    for line in _extract_section_lines(text, markers):
        for match in CODE_ITEM_RE.finditer(line):
            value = (match.group(1) or match.group(2) or "").strip()
            if value.endswith(".md") or value.endswith("/"):
                items.append(value)
    return _unique_nonempty(items)


def _extract_agent_names(text: str, markers: list[str]) -> list[str]:
    items = _extract_section_lines(text, markers)
    names: list[str] = []
    for line in items:
        names.extend(RUN_ID_RE.findall(line))
    return _unique_nonempty(names)


def _extract_budget(text: str, markers: list[str]) -> dict[str, Optional[int]]:
    out: dict[str, Optional[int]] = {"quick": None, "standard": None, "deep": None}
    for line in _extract_section_lines(text, markers):
        m = BUDGET_LINE_RE.match(line)
        if not m:
            continue
        label = m.group(1).lower()
        nums = [int(x) for x in NUMBER_RE.findall(m.group(2))]
        if nums:
            out[label] = max(nums)
    return out


def _version_report(root: Path) -> dict[str, Any]:
    pyproject_version = None
    pyproject_path = root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            data = tomllib.loads(_read_text(pyproject_path))
            pyproject_version = data.get("project", {}).get("version")
        except Exception:
            pyproject_version = None

    package_version = None
    m = VERSION_RE.search(_read_text(root / "xlfg" / "__init__.py"))
    if m:
        package_version = m.group(1)

    plugin_versions: dict[str, Optional[str]] = {}
    for rel in [
        Path("plugins/xlfg-engineering/.claude-plugin/plugin.json"),
        Path("plugins/xlfg-engineering/.cursor-plugin/plugin.json"),
    ]:
        data = _load_json(root / rel)
        plugin_versions[str(rel)] = data.get("version") if data else None

    values = [pyproject_version, package_version, *plugin_versions.values()]
    present = [v for v in values if v]
    ok = bool(present) and len(set(present)) == 1 and len(present) == len(values)
    return {
        "ok": ok,
        "versions": {
            "pyproject": pyproject_version,
            "package": package_version,
            **plugin_versions,
        },
    }


def _model_report(root: Path) -> dict[str, Any]:
    counts: dict[str, int] = {}
    by_agent: dict[str, str] = {}
    for path in sorted((root / "plugins" / "xlfg-engineering" / "agents").rglob("*.md")):
        text = _read_text(path)
        m = MODEL_RE.search(text)
        model = m.group(1) if m else "unknown"
        counts[model] = counts.get(model, 0) + 1
        by_agent[str(path.relative_to(root))] = model
    return {"counts": counts, "by_agent": by_agent}


def _word_metrics(root: Path) -> dict[str, Any]:
    plugin_root = root / "plugins" / "xlfg-engineering"
    command_texts = {p.name: _read_text(p) for p in sorted((plugin_root / "commands").glob("*.md"))}
    agent_texts = {str(p.relative_to(plugin_root)): _read_text(p) for p in sorted((plugin_root / "agents").rglob("*.md"))}
    skill_texts = {str(p.relative_to(plugin_root)): _read_text(p) for p in sorted((plugin_root / "skills").rglob("SKILL.md"))}
    core_commands = sum(_word_count(command_texts.get(name, "")) for name in CORE_COMMAND_FILES)
    return {
        "core_commands": core_commands,
        "all_commands": sum(_word_count(t) for t in command_texts.values()),
        "all_agents": sum(_word_count(t) for t in agent_texts.values()),
        "all_skills": sum(_word_count(t) for t in skill_texts.values()),
        "command_files": {name: _word_count(text) for name, text in command_texts.items()},
    }


def _seeded_run_artifacts(root: Path) -> dict[str, Any]:
    text = _read_text(root / "xlfg" / "runs.py")
    files = _unique_nonempty(SAFE_WRITE_RE.findall(text))
    dirs = _unique_nonempty(READ_DIR_RE.findall(text))
    return {
        "files": files,
        "directories": dirs,
        "file_count": len(files),
        "directory_count": len(dirs),
    }


def _features(root: Path) -> dict[str, bool]:
    plan_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-plan.md")
    implement_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-implement.md")
    verify_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-verify.md")
    review_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-review.md")
    xlfg_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md")
    cli_text = _read_text(root / "xlfg" / "cli.py")
    return {
        "recall": "xlfg:recall" in xlfg_text and "memory-recall.md" in _read_text(root / "xlfg" / "runs.py"),
        "research_lane": "research.md" in plan_text or "xlfg-researcher" in plan_text,
        "query_contract": "query-contract.md" in plan_text and "query-contract.md" in _read_text(root / "xlfg" / "runs.py"),
        "run_card": "run card" in plan_text.lower() or "run card" in implement_text.lower(),
        "execution_ownership": "Execution ownership" in plan_text or "execution ownership" in _read_text(root / "xlfg" / "runs.py").lower(),
        "test_contract": "test-contract.md" in plan_text and "test-contract.md" in verify_text,
        "test_readiness": "test-readiness.md" in plan_text and "test-readiness.md" in implement_text,
        "proof_map": "proof-map.md" in plan_text and "proof-map.md" in verify_text,
        "verify": "xlfg:verify" in xlfg_text and (root / "xlfg" / "verify.py").exists(),
        "review": "xlfg:review" in xlfg_text and review_text.strip() != "",
        "compound": "/xlfg:compound" in xlfg_text and (root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-compound.md").exists(),
        "benchmark_doc": (root / "docs" / "benchmarking.md").exists(),
        "audit": "audit" in cli_text and (root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-audit.md").exists(),
    }


def _phase_metrics(root: Path) -> dict[str, Any]:
    plan_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-plan.md")
    implement_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-implement.md")
    verify_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-verify.md")
    review_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-review.md")

    plan_required = _extract_markdown_items(plan_text, [
        "Always write these core artifacts",
        "must produce",
        "Ensure the run contains at least",
    ])
    impl_reads = _count_list_items(implement_text, [
        "Always read these first",
        "Read these files first",
        "Read the minimum honest brief first",
    ])
    verify_reads = _count_list_items(verify_text, [
        "Always read these first",
        "Read first (if present)",
        "Read first",
    ])
    review_reads = _count_list_items(review_text, [
        "Always read these first",
        "Read the shortest useful brief",
        "Always read first",
    ])
    impl_default_agents = _extract_agent_names(implement_text, ["Default path", "Run these agents in order for the task"])
    plan_budget = _extract_budget(plan_text, ["Default specialist budget"])
    review_budget = _extract_budget(review_text, ["Default review budget"])
    if review_budget.get("standard") is None:
        review_budget["standard"] = len(_extract_agent_names(review_text, ["Run these review agents", "Pick review lenses"])) or None

    return {
        "plan_required_artifacts": plan_required,
        "plan_required_artifact_count": len(plan_required),
        "implement_initial_reads": impl_reads,
        "verify_initial_reads": verify_reads,
        "review_initial_reads": review_reads,
        "implementation_default_agents": impl_default_agents,
        "implementation_default_agent_count": len(impl_default_agents),
        "planning_specialist_budget": plan_budget,
        "review_budget": review_budget,
    }


def _workflow_load_score(*, core_command_words: int, seeded_run_files: int, plan_required_artifacts: int, implement_reads: int, verify_reads: int, review_reads: int, planning_standard_budget: Optional[int], implementation_default_agents: int, review_standard_budget: Optional[int], has_haiku: bool, version_sync_ok: bool) -> dict[str, Any]:
    components = {
        "core_prompt_tax": min(30.0, core_command_words / 200.0),
        "artifact_tax": min(18.0, seeded_run_files * 0.9),
        "plan_tax": min(14.0, max(0, plan_required_artifacts - 8) * 2.0),
        "read_tax": min(18.0, max(0, implement_reads - 6) * 1.5 + max(0, verify_reads - 6) * 1.0 + max(0, review_reads - 5) * 1.0),
        "fanout_tax": min(18.0, max(0, (planning_standard_budget or 0) - 1) * 3.0 + max(0, implementation_default_agents - 1) * 6.0 + max(0, (review_standard_budget or 0) - 2) * 3.0),
        "routing_tax": 0.0 if has_haiku else 6.0,
        "hygiene_tax": 0.0 if version_sync_ok else 6.0,
    }
    score = round(min(100.0, sum(components.values())), 1)
    if score <= 35:
        band = "lean"
    elif score <= 55:
        band = "moderate"
    elif score <= 75:
        band = "heavy"
    else:
        band = "overloaded"
    return {"score": score, "band": band, "components": components}


def _coverage_score(features: dict[str, bool], version_sync_ok: bool) -> int:
    score = 0
    score += 10 if features.get("recall") else 0
    score += 10 if features.get("research_lane") else 0
    score += 10 if features.get("query_contract") else 0
    score += 8 if features.get("run_card") else 0
    score += 7 if features.get("execution_ownership") else 0
    score += 7 if features.get("test_contract") else 0
    score += 7 if features.get("test_readiness") else 0
    score += 7 if features.get("proof_map") else 0
    score += 7 if features.get("verify") else 0
    score += 7 if features.get("review") else 0
    score += 5 if features.get("compound") else 0
    score += 5 if features.get("benchmark_doc") else 0
    score += 5 if features.get("audit") else 0
    score += 5 if version_sync_ok else 0
    return score


def _top_recommendations(*, core_command_words: int, seeded_run_files: int, plan_required_artifacts: int, implement_reads: int, verify_reads: int, review_reads: int, planning_standard_budget: Optional[int], implementation_default_agents: int, review_standard_budget: Optional[int], has_haiku: bool, version_sync_ok: bool, features: dict[str, bool]) -> list[str]:
    recs: list[str] = []
    if core_command_words > 4500:
        recs.append("Trim the core command prompts so the macro is lighter than a strong vanilla Claude Code session.")
    if plan_required_artifacts > 10:
        recs.append("Collapse mandatory planning artifacts; keep only the run card, plan, proof, and status docs always-on.")
    if implement_reads > 6 or verify_reads > 6 or review_reads > 5:
        recs.append("Reduce initial read amplification; start each phase from spec.md plus the proof/status docs and dive deeper only on demand.")
    if implementation_default_agents > 1:
        recs.append("Reduce default per-task fan-out to one implementation agent and make tests/checkers trigger-based.")
    if (review_standard_budget or 0) > 2:
        recs.append("Cap the standard review budget at one or two lenses instead of routine multi-reviewer fan-out.")
    if (planning_standard_budget or 0) > 2:
        recs.append("Keep planning specialist budget small; the lead planner should synthesize instead of delegating every thinking step.")
    if not has_haiku:
        recs.append("Route read-only exploration and environment triage to lighter models to lower cost and latency.")
    if not features.get("research_lane"):
        recs.append("Add a first-class research lane so external truth is handled deliberately instead of informally or not at all.")
    if not features.get("benchmark_doc") or not features.get("audit"):
        recs.append("Add deterministic harness auditing plus a live A/B benchmark protocol against vanilla Claude Code.")
    if not version_sync_ok:
        recs.append("Fix package/plugin version drift so the bundle can be trusted and benchmarked cleanly.")
    if not recs:
        recs.append("The main remaining opportunity is live A/B evaluation on real Claude Code tasks; the static harness shape is already in good condition.")
    return recs[:5]


def audit_repo(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    versions = _version_report(root)
    words = _word_metrics(root)
    seeded = _seeded_run_artifacts(root)
    phases = _phase_metrics(root)
    models = _model_report(root)
    features = _features(root)

    load = _workflow_load_score(
        core_command_words=words["core_commands"],
        seeded_run_files=seeded["file_count"],
        plan_required_artifacts=phases["plan_required_artifact_count"],
        implement_reads=phases["implement_initial_reads"],
        verify_reads=phases["verify_initial_reads"],
        review_reads=phases["review_initial_reads"],
        planning_standard_budget=phases["planning_specialist_budget"].get("standard"),
        implementation_default_agents=phases["implementation_default_agent_count"],
        review_standard_budget=phases["review_budget"].get("standard"),
        has_haiku=models["counts"].get("haiku", 0) > 0,
        version_sync_ok=versions["ok"],
    )
    coverage = _coverage_score(features, versions["ok"])
    efficiency = round(coverage / max(load["score"], 1.0), 2)
    if efficiency >= 2.0:
        efficiency_band = "excellent"
    elif efficiency >= 1.4:
        efficiency_band = "strong"
    elif efficiency >= 1.0:
        efficiency_band = "acceptable"
    else:
        efficiency_band = "poor"

    recommendations = _top_recommendations(
        core_command_words=words["core_commands"],
        seeded_run_files=seeded["file_count"],
        plan_required_artifacts=phases["plan_required_artifact_count"],
        implement_reads=phases["implement_initial_reads"],
        verify_reads=phases["verify_initial_reads"],
        review_reads=phases["review_initial_reads"],
        planning_standard_budget=phases["planning_specialist_budget"].get("standard"),
        implementation_default_agents=phases["implementation_default_agent_count"],
        review_standard_budget=phases["review_budget"].get("standard"),
        has_haiku=models["counts"].get("haiku", 0) > 0,
        version_sync_ok=versions["ok"],
        features=features,
    )

    return {
        "version_sync": versions,
        "metrics": {
            "word_counts": words,
            "seeded_run_artifacts": seeded,
            "phase_load": phases,
            "models": models,
            "features": features,
        },
        "scores": {
            "workflow_load_score": load["score"],
            "workflow_load_band": load["band"],
            "workflow_load_components": load["components"],
            "sdlc_coverage_score": coverage,
            "efficiency_index": efficiency,
            "efficiency_band": efficiency_band,
        },
        "recommendations": recommendations,
    }
