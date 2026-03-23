from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import tomllib


LEGACY_CORE_COMMAND_FILES = [
    "xlfg.md",
    "xlfg-plan.md",
    "xlfg-implement.md",
    "xlfg-verify.md",
    "xlfg-review.md",
]
PHASE_COMMAND_FILES = [
    "xlfg-plan.md",
    "xlfg-implement.md",
    "xlfg-verify.md",
    "xlfg-review.md",
    "xlfg-compound.md",
]

WORD_RE = re.compile(r"[A-Za-z0-9_./:-]+")
MODEL_RE = re.compile(r"^model:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE)
VERSION_RE = re.compile(r'__version__\s*=\s*"([^"]+)"')
SAFE_WRITE_RE = re.compile(r'safe_write\(docs_dir / "([^"]+)"')
READ_DIR_RE = re.compile(r'ensure_dir\(docs_dir / "([^"]+)"\)')
BULLET_RE = re.compile(r"^[-*]\s+")
CODE_ITEM_RE = re.compile(r"`([^`]+)`|([A-Za-z0-9_.-]+(?:\.md|/))")
BUDGET_LINE_RE = re.compile(r"^[-*]\s*`?(quick|standard|deep)`?\s*:\s*(.+)$", re.IGNORECASE)
NUMBER_RE = re.compile(r"(\d+)")
ALLOWED_TOOLS_RE = re.compile(r"^allowed-tools:\s*(.+)$", re.MULTILINE)
EFFORT_RE = re.compile(r"^effort:\s*(.+)$", re.MULTILINE)


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
        for token in re.findall(r"xlfg-[a-z0-9-]+", line):
            names.append(token)
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
    skill_texts = {str(p.relative_to(plugin_root)): _read_text(p) for p in sorted((plugin_root / "skills").rglob("SKILL.md"))}
    agent_texts = {str(p.relative_to(plugin_root)): _read_text(p) for p in sorted((plugin_root / "agents").rglob("*.md"))}

    primary_skill_text = _read_text(plugin_root / "skills" / "xlfg" / "SKILL.md")
    primary_command_text = _read_text(plugin_root / "commands" / "xlfg.md")
    phase_words = sum(_word_count(command_texts.get(name, "")) for name in PHASE_COMMAND_FILES)
    workflow_words = max(_word_count(primary_skill_text), _word_count(primary_command_text)) + phase_words

    return {
        "primary_skill_words": _word_count(primary_skill_text),
        "primary_command_words": _word_count(primary_command_text),
        "manual_phase_words": phase_words,
        "workflow_words": workflow_words,
        "legacy_core_commands": sum(_word_count(command_texts.get(name, "")) for name in LEGACY_CORE_COMMAND_FILES),
        "all_commands": sum(_word_count(t) for t in command_texts.values()),
        "all_skills": sum(_word_count(t) for t in skill_texts.values()),
        "all_agents": sum(_word_count(t) for t in agent_texts.values()),
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


def _frontmatter_summary(text: str) -> dict[str, Any]:
    allowed = None
    m = ALLOWED_TOOLS_RE.search(text)
    if m:
        allowed = [item.strip() for item in m.group(1).split(",") if item.strip()]
    effort = None
    em = EFFORT_RE.search(text)
    if em:
        effort = em.group(1).strip()
    return {
        "allowed_tools": allowed or [],
        "effort": effort,
        "has_hooks": "\nhooks:" in text or text.startswith("hooks:"),
    }


def _features(root: Path) -> dict[str, bool]:
    plugin_root = root / "plugins" / "xlfg-engineering"
    main_skill_path = plugin_root / "skills" / "xlfg" / "SKILL.md"
    main_command_path = plugin_root / "commands" / "xlfg.md"
    main_skill = _read_text(main_skill_path)
    main_command = _read_text(main_command_path)
    plan_text = _read_text(plugin_root / "commands" / "xlfg-plan.md")
    implement_text = _read_text(plugin_root / "commands" / "xlfg-implement.md")
    verify_text = _read_text(plugin_root / "commands" / "xlfg-verify.md")
    review_text = _read_text(plugin_root / "commands" / "xlfg-review.md")
    compound_text = _read_text(plugin_root / "commands" / "xlfg-compound.md")
    cli_text = _read_text(root / "xlfg" / "cli.py")
    plugin_readme = _read_text(plugin_root / "README.md")
    root_readme = _read_text(root / "README.md")
    hooks_json = _read_text(plugin_root / "hooks" / "hooks.json")
    runs_text = _read_text(root / "xlfg" / "runs.py")
    brief_blob = "\n".join([main_skill, main_command, plan_text, implement_text, verify_text, review_text, compound_text, plugin_readme, root_readme, runs_text])
    fm = _frontmatter_summary(main_skill or main_command)
    return {
        "recall": "memory-recall.md" in brief_blob,
        "research_lane": "research.md" in brief_blob or "external findings" in runs_text,
        "run_card": "single source of truth" in brief_blob.lower() or "run card" in brief_blob.lower(),
        "lean_core_artifacts": _seeded_run_artifacts(root)["file_count"] <= 6,
        "autonomous_macro": "one autonomous run" in brief_blob.lower() or "do not ask the user to invoke" in brief_blob.lower() or "do **not** ask the user to run phase subcommands" in brief_blob.lower(),
        "skill_native": main_skill_path.exists(),
        "standalone_short_name_pack": (root / "standalone" / ".claude" / "skills" / "xlfg" / "SKILL.md").exists(),
        "consent_reduction": bool(fm["allowed_tools"]) or "ExitPlanMode" in hooks_json or "ExitPlanMode" in main_skill or "ExitPlanMode" in main_command,
        "skill_hooks": fm["has_hooks"],
        "plugin_hooks": (plugin_root / "hooks" / "hooks.json").exists(),
        "hook_auto_exit_plan": "ExitPlanMode" in hooks_json or "ExitPlanMode" in main_skill or "ExitPlanMode" in main_command,
        "effort_frontmatter": bool(fm["effort"]),
        "plugin_namespace_documented": "/xlfg-engineering:xlfg" in plugin_readme and "standalone" in plugin_readme.lower() and "/xlfg" in plugin_readme,
        "verify": bool(verify_text.strip()) and (root / "xlfg" / "verify.py").exists(),
        "review": bool(review_text.strip()),
        "compound": bool(compound_text.strip()),
        "benchmark_doc": (root / "docs" / "benchmarking.md").exists(),
        "audit": "audit" in cli_text and (plugin_root / "commands" / "xlfg-audit.md").exists(),
    }


def _phase_metrics(root: Path) -> dict[str, Any]:
    plan_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-plan.md")
    implement_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-implement.md")
    verify_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-verify.md")
    review_text = _read_text(root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-review.md")

    plan_required = _extract_markdown_items(plan_text, [
        "Always create these core files",
        "Always create these core",
        "Always write these core artifacts",
    ])
    impl_reads = _count_list_items(implement_text, [
        "Always read these first",
        "Read these first",
        "Read the minimum honest brief first",
    ])
    verify_reads = _count_list_items(verify_text, [
        "Always read these first",
        "Read first (if present)",
        "Read only when needed",
    ])
    review_reads = _count_list_items(review_text, [
        "Always read these first",
        "Read the shortest useful brief",
        "Read only when a chosen lens needs them",
    ])
    impl_default_agents = _extract_agent_names(implement_text, ["Default path"])
    plan_budget = _extract_budget(plan_text, ["Default specialist budget", "Review budget"])
    review_budget = _extract_budget(review_text, ["Default review budget"])
    if review_budget.get("standard") is None:
        review_budget["standard"] = len(_extract_agent_names(review_text, ["Use security", "Use performance", "Use ux", "Use architecture"])) or 2

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


def _workflow_load_score(
    *,
    workflow_words: int,
    seeded_run_files: int,
    plan_required_artifacts: int,
    implement_reads: int,
    verify_reads: int,
    review_reads: int,
    planning_standard_budget: Optional[int],
    implementation_default_agents: int,
    review_standard_budget: Optional[int],
    has_haiku: bool,
    version_sync_ok: bool,
    features: dict[str, bool],
) -> dict[str, Any]:
    components = {
        "workflow_tax": min(30.0, workflow_words / 220.0),
        "artifact_tax": min(18.0, seeded_run_files * 1.4),
        "duplication_tax": min(12.0, max(0, plan_required_artifacts - 6) * 2.0),
        "read_tax": min(16.0, max(0, implement_reads - 4) * 2.0 + max(0, verify_reads - 4) * 1.5 + max(0, review_reads - 3) * 1.5),
        "fanout_tax": min(12.0, max(0, (planning_standard_budget or 0) - 2) * 2.0 + max(0, implementation_default_agents - 1) * 6.0 + max(0, (review_standard_budget or 0) - 2) * 2.0),
        "routing_tax": 0.0 if has_haiku else 5.0,
        "compatibility_tax": (
            0.0
            + (0.0 if features.get("skill_native") else 4.0)
            + (0.0 if features.get("autonomous_macro") else 4.0)
            + (0.0 if features.get("consent_reduction") else 4.0)
            + (0.0 if features.get("effort_frontmatter") else 3.0)
            + (0.0 if features.get("standalone_short_name_pack") else 2.0)
        ),
        "hygiene_tax": 0.0 if version_sync_ok else 5.0,
    }
    score = round(min(100.0, sum(components.values())), 1)
    if score <= 30:
        band = "lean"
    elif score <= 50:
        band = "moderate"
    elif score <= 70:
        band = "heavy"
    else:
        band = "overloaded"
    return {"score": score, "band": band, "components": components}


def _coverage_score(features: dict[str, bool], version_sync_ok: bool) -> int:
    score = 0
    score += 10 if features.get("recall") else 0
    score += 10 if features.get("research_lane") else 0
    score += 10 if features.get("run_card") else 0
    score += 10 if features.get("lean_core_artifacts") else 0
    score += 12 if features.get("autonomous_macro") else 0
    score += 8 if features.get("verify") else 0
    score += 8 if features.get("review") else 0
    score += 6 if features.get("compound") else 0
    score += 6 if features.get("audit") else 0
    score += 6 if features.get("benchmark_doc") else 0
    score += 5 if features.get("skill_native") else 0
    score += 5 if features.get("plugin_namespace_documented") else 0
    score += 4 if version_sync_ok else 0
    return score


def _compatibility_score(features: dict[str, bool]) -> int:
    score = 0
    score += 20 if features.get("skill_native") else 0
    score += 15 if features.get("standalone_short_name_pack") else 0
    score += 20 if features.get("consent_reduction") else 0
    score += 10 if features.get("hook_auto_exit_plan") else 0
    score += 10 if features.get("effort_frontmatter") else 0
    score += 10 if features.get("plugin_namespace_documented") else 0
    score += 15 if features.get("autonomous_macro") else 0
    return score


def _top_recommendations(
    *,
    workflow_words: int,
    seeded_run_files: int,
    plan_required_artifacts: int,
    implement_reads: int,
    verify_reads: int,
    review_reads: int,
    planning_standard_budget: Optional[int],
    implementation_default_agents: int,
    review_standard_budget: Optional[int],
    has_haiku: bool,
    version_sync_ok: bool,
    features: dict[str, bool],
) -> list[str]:
    recs: list[str] = []
    if workflow_words > 3200:
        recs.append("Trim the primary workflow further so xlfg stays lighter than a strong vanilla Claude Code path.")
    if seeded_run_files > 6:
        recs.append("Keep only the lean core run files always-on; create supporting docs only when they change a decision.")
    if plan_required_artifacts > 6:
        recs.append("Collapse mandatory planning artifacts into spec.md plus proof/status docs.")
    if implement_reads > 4 or verify_reads > 4 or review_reads > 3:
        recs.append("Reduce initial read amplification; start each phase from spec.md and only dive deeper on demand.")
    if implementation_default_agents > 1:
        recs.append("Reduce default fan-out to one implementation owner; make extra agents trigger-based.")
    if (review_standard_budget or 0) > 2:
        recs.append("Cap the standard review budget at one or two lenses instead of routine multi-reviewer fan-out.")
    if (planning_standard_budget or 0) > 2:
        recs.append("Keep planning specialist budget small; the lead planner should synthesize instead of delegating every thought.")
    if not has_haiku:
        recs.append("Route read-only exploration and environment triage to lighter models to lower cost and latency.")
    if not features.get("skill_native"):
        recs.append("Ship a first-class skill; current Claude Code is skills-first and commands are legacy compatibility.")
    if not features.get("standalone_short_name_pack"):
        recs.append("Add a standalone .claude/skills/xlfg pack so users can get a direct /xlfg command without plugin namespacing.")
    if not features.get("consent_reduction"):
        recs.append("Add allowed-tools or narrow hooks so /xlfg stops asking for avoidable internal approvals.")
    if not features.get("plugin_namespace_documented"):
        recs.append("Document plugin namespacing clearly and show the standalone path for short commands.")
    if not version_sync_ok:
        recs.append("Fix package/plugin version drift so the bundle can be trusted and benchmarked cleanly.")
    if not recs:
        recs.append("The main remaining opportunity is live A/B evaluation on real Claude Code tasks; the static harness shape is in strong condition.")
    return recs[:6]


def audit_repo(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    versions = _version_report(root)
    words = _word_metrics(root)
    seeded = _seeded_run_artifacts(root)
    phases = _phase_metrics(root)
    models = _model_report(root)
    features = _features(root)

    load = _workflow_load_score(
        workflow_words=words["workflow_words"],
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
    coverage = _coverage_score(features, versions["ok"])
    compatibility = _compatibility_score(features)
    efficiency = round((coverage + compatibility / 2.0) / max(load["score"], 1.0), 2)
    if efficiency >= 2.4:
        efficiency_band = "excellent"
    elif efficiency >= 1.6:
        efficiency_band = "strong"
    elif efficiency >= 1.0:
        efficiency_band = "acceptable"
    else:
        efficiency_band = "poor"

    recommendations = _top_recommendations(
        workflow_words=words["workflow_words"],
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
            "claude_code_compatibility_score": compatibility,
            "efficiency_index": efficiency,
            "efficiency_band": efficiency_band,
        },
        "recommendations": recommendations,
    }
