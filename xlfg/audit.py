from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import tomllib

WORD_RE = re.compile(r"[A-Za-z0-9_./:-]+")
VERSION_RE = re.compile(r'__version__\s*=\s*"([^"]+)"')
MODEL_RE = re.compile(r"^model:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE)
SAFE_WRITE_RE = re.compile(r'safe_write\(docs_dir / "([^"]+)"')
READ_DIR_RE = re.compile(r'ensure_dir\(docs_dir / "([^"]+)"\)')
FRONTMATTER_SPLIT_RE = re.compile(r"^---\s*$", re.MULTILINE)
FRONTMATTER_KV_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")
CODE_ITEM_RE = re.compile(r"`([^`]+)`|([A-Za-z0-9_.-]+(?:\.md|/))")
BULLET_RE = re.compile(r"^[-*]\s+")
PHASE_SKILL_NAME_RE = re.compile(r"xlfg-[a-z-]+-phase")
LEGACY_TASK_TOOL_RE = re.compile(r"(^|[^A-Za-z])Task([^A-Za-z]|$)")


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
    except Exception:
        return None
    return data if isinstance(data, dict) else None


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


def _parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm: dict[str, str] = {}
    for raw in lines[1:]:
        stripped = raw.strip()
        if stripped == "---":
            break
        m = FRONTMATTER_KV_RE.match(stripped)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        fm[key] = value
    return fm


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


def _extract_markdown_items(text: str, markers: list[str]) -> list[str]:
    items: list[str] = []
    for line in _extract_section_lines(text, markers):
        for match in CODE_ITEM_RE.finditer(line):
            value = (match.group(1) or match.group(2) or "").strip()
            if value.endswith(".md") or value.endswith("/"):
                items.append(value)
    return _unique_nonempty(items)


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




def _runtime_legacy_query_contract_refs(root: Path) -> dict[str, Any]:
    targets = [
        root / "plugins" / "xlfg-engineering" / "commands",
        root / "plugins" / "xlfg-engineering" / "skills",
        root / "plugins" / "xlfg-engineering" / "agents",
        root / "standalone" / ".claude" / "skills",
        root / "xlfg" / "runs.py",
    ]
    refs: list[str] = []
    for target in targets:
        if target.is_file():
            text = _read_text(target)
            if "query-contract.md" in text:
                refs.append(str(target.relative_to(root)))
            continue
        if not target.exists():
            continue
        for path in sorted(target.rglob("*.md")) if target.is_dir() else []:
            if "query-contract.md" in _read_text(path):
                refs.append(str(path.relative_to(root)))
    return {"count": len(refs), "paths": refs}


def _entrypoint_report(root: Path) -> dict[str, Any]:
    plugin_root = root / "plugins" / "xlfg-engineering"
    plugin_command = plugin_root / "commands" / "xlfg.md"
    plugin_skill = plugin_root / "skills" / "xlfg" / "SKILL.md"
    standalone_skill = root / "standalone" / ".claude" / "skills" / "xlfg" / "SKILL.md"

    plugin_command_text = _read_text(plugin_command)
    plugin_skill_text = _read_text(plugin_skill)
    standalone_text = _read_text(standalone_skill)

    has_plugin_command = plugin_command.exists()
    has_plugin_skill = plugin_skill.exists()
    has_standalone_skill = standalone_skill.exists()
    collision = has_plugin_command and has_plugin_skill

    plugin_primary_kind = "command" if has_plugin_command else ("skill" if has_plugin_skill else "none")
    plugin_primary_text = plugin_command_text if has_plugin_command else plugin_skill_text

    repo_relative_refs = 0
    for text in [plugin_command_text, plugin_skill_text, standalone_text]:
        repo_relative_refs += text.count("plugins/xlfg-engineering/")

    plugin_name_frontmatter_count = 0
    for path in sorted((plugin_root / "commands").glob("*.md")):
        # keep the intentional main-command alias from the 2.4.1 baseline
        if path == plugin_command:
            continue
        if _parse_frontmatter(_read_text(path)).get("name"):
            plugin_name_frontmatter_count += 1
    for path in sorted((plugin_root / "skills").rglob("SKILL.md")):
        if _parse_frontmatter(_read_text(path)).get("name"):
            plugin_name_frontmatter_count += 1

    background_support_skills = True
    for path in sorted((plugin_root / "skills").rglob("SKILL.md")):
        if path == plugin_skill:
            continue
        fm = _parse_frontmatter(_read_text(path))
        if fm.get("user-invocable") != "false":
            background_support_skills = False
            break

    plugin_phase_skills = sorted(
        p.parent.name for p in (plugin_root / "skills").rglob("SKILL.md") if p.parent.name.endswith("-phase")
    )
    standalone_phase_skills = sorted(
        p.parent.name for p in (root / "standalone" / ".claude" / "skills").rglob("SKILL.md") if p.parent.name.endswith("-phase")
    )

    return {
        "plugin_command_exists": has_plugin_command,
        "plugin_skill_exists": has_plugin_skill,
        "standalone_skill_exists": has_standalone_skill,
        "plugin_primary_kind": plugin_primary_kind,
        "command_skill_collision": collision,
        "repo_relative_plugin_refs": repo_relative_refs,
        "plugin_name_frontmatter_count": plugin_name_frontmatter_count,
        "background_support_skills": background_support_skills,
        "plugin_phase_skills": plugin_phase_skills,
        "plugin_phase_skill_count": len(plugin_phase_skills),
        "standalone_phase_skills": standalone_phase_skills,
        "standalone_phase_skill_count": len(standalone_phase_skills),
        "plugin_primary_text": plugin_primary_text,
        "standalone_text": standalone_text,
        "plugin_command_text": plugin_command_text,
        "plugin_skill_text": plugin_skill_text,
    }


def _word_metrics(root: Path, entrypoints: dict[str, Any]) -> dict[str, Any]:
    plugin_root = root / "plugins" / "xlfg-engineering"
    command_texts = {p.name: _read_text(p) for p in sorted((plugin_root / "commands").glob("*.md"))}
    skill_texts = {str(p.relative_to(plugin_root)): _read_text(p) for p in sorted((plugin_root / "skills").rglob("SKILL.md"))}
    agent_texts = {str(p.relative_to(plugin_root)): _read_text(p) for p in sorted((plugin_root / "agents").rglob("*.md"))}

    primary_plugin_words = _word_count(entrypoints["plugin_primary_text"])
    standalone_words = _word_count(entrypoints["standalone_text"])
    utility_command_words = sum(_word_count(text) for name, text in command_texts.items() if name != "xlfg.md")

    return {
        "primary_plugin_entrypoint_words": primary_plugin_words,
        "standalone_entrypoint_words": standalone_words,
        "utility_command_words": utility_command_words,
        "workflow_words": max(primary_plugin_words, standalone_words),
        "all_commands": sum(_word_count(t) for t in command_texts.values()),
        "all_skills": sum(_word_count(t) for t in skill_texts.values()),
        "all_agents": sum(_word_count(t) for t in agent_texts.values()),
        "command_files": {name: _word_count(text) for name, text in command_texts.items()},
    }


def _phase_metrics(root: Path, entrypoints: dict[str, Any]) -> dict[str, Any]:
    main_text = entrypoints["plugin_primary_text"] or entrypoints["standalone_text"]
    core_files = _extract_markdown_items(main_text, ["Up-front core files only", "core files"])
    # main entrypoint keeps the run centered on spec.md; phase read amplification is intentionally low
    impl_reads = 1 if "spec.md" in main_text else 0
    verify_reads = 1 if "verification.md" in main_text or "xlfg verify" in main_text else 0
    review_reads = 1 if "review" in main_text.lower() else 0
    default_agents = ["owner"] if "one owner by default" in main_text.lower() else []
    return {
        "plan_required_artifacts": core_files,
        "plan_required_artifact_count": len(core_files),
        "implement_initial_reads": impl_reads,
        "verify_initial_reads": verify_reads,
        "review_initial_reads": review_reads,
        "implementation_default_agents": default_agents,
        "implementation_default_agent_count": len(default_agents),
        "planning_specialist_budget": {"quick": 1, "standard": 1, "deep": 2},
        "review_budget": {"quick": 0, "standard": 1, "deep": 2},
    }


def _frontmatter_summary(text: str) -> dict[str, Any]:
    fm = _parse_frontmatter(text)
    allowed = [item.strip() for item in fm.get("allowed-tools", "").split(",") if item.strip()] if fm.get("allowed-tools") else []
    return {
        "allowed_tools": allowed,
        "effort": fm.get("effort"),
        "has_hooks": bool(fm.get("hooks")) or "\nhooks:" in text or text.startswith("hooks:"),
        "has_name": "name" in fm,
    }




def _subagent_hardening_report(root: Path) -> dict[str, Any]:
    plugin_agents = sorted((root / "plugins" / "xlfg-engineering" / "agents").rglob("*.md"))
    standalone_agents = sorted((root / "standalone" / ".claude" / "agents").rglob("*.md"))

    def _count(predicate):
        return sum(1 for path in plugin_agents if predicate(path, _read_text(path), _parse_frontmatter(_read_text(path))))

    def _has_tools(path: Path, _text: str, fm: dict[str, str]) -> bool:
        return bool(fm.get("tools"))

    def _background_false(path: Path, _text: str, fm: dict[str, str]) -> bool:
        return fm.get("background") == "false"

    def _short_turn_budget(path: Path, _text: str, fm: dict[str, str]) -> bool:
        try:
            return 0 < int(fm.get("maxTurns", "0")) <= 12
        except ValueError:
            return False

    def _leaf_worker_tools(path: Path, _text: str, fm: dict[str, str]) -> bool:
        tools = {item.strip().lower() for item in fm.get("tools", "").split(",") if item.strip()}
        return "agent" not in tools and "sendmessage" not in tools

    def _proactive_desc(path: Path, _text: str, fm: dict[str, str]) -> bool:
        return "use proactively" in fm.get("description", "").lower()

    def _specialist_identity(path: Path, text: str, _fm: dict[str, str]) -> bool:
        return "## Specialist identity" in text and "## Execution contract" in text

    def _status_contract(path: Path, text: str, _fm: dict[str, str]) -> bool:
        return "Status: DONE" in text and "Status: BLOCKED" in text and "Status: FAILED" in text

    def _completion_barrier(path: Path, text: str, _fm: dict[str, str]) -> bool:
        return "## Completion barrier" in text and "progress update" in text and "You are complete only when" in text

    def _resume_rule(path: Path, text: str, _fm: dict[str, str]) -> bool:
        return "If the parent resumes you" in text

    def _artifact_bootstrap(path: Path, text: str, _fm: dict[str, str]) -> bool:
        return "Status: IN_PROGRESS" in text and "exact artifact path" in text

    def _final_response_contract(path: Path, text: str, _fm: dict[str, str]) -> bool:
        return "## Final response contract" in text and "DONE <artifact-path>" in text and "Any other final reply shape is invalid" in text

    review_agents = [p for p in plugin_agents if "/review/" in str(p).replace("\\", "/")]
    review_paths = {
        "xlfg-architecture-reviewer": "DOCS_RUN_DIR/reviews/architecture-review.md",
        "xlfg-security-reviewer": "DOCS_RUN_DIR/reviews/security-review.md",
        "xlfg-performance-reviewer": "DOCS_RUN_DIR/reviews/performance-review.md",
        "xlfg-ux-reviewer": "DOCS_RUN_DIR/reviews/ux-review.md",
    }
    review_artifact_reports = 0
    for path in review_agents:
        text = _read_text(path)
        name_match = re.search(r"^name:\s*([^\n]+)", text, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else ""
        expected = review_paths.get(name)
        if expected and expected in text:
            review_artifact_reports += 1

    standalone_parity = len(plugin_agents) == len(standalone_agents) and len(plugin_agents) > 0

    return {
        "plugin_agent_count": len(plugin_agents),
        "standalone_agent_count": len(standalone_agents),
        "standalone_agent_pack": standalone_parity,
        "agents_with_tools_allowlist": _count(_has_tools),
        "agents_with_background_false": _count(_background_false),
        "agents_with_short_turn_budgets": _count(_short_turn_budget),
        "agents_with_leaf_worker_tools": _count(_leaf_worker_tools),
        "agents_with_proactive_description": _count(_proactive_desc),
        "agents_with_specialist_identity_contract": _count(_specialist_identity),
        "agents_with_status_contract": _count(_status_contract),
        "agents_with_completion_barrier": _count(_completion_barrier),
        "agents_with_resume_rule": _count(_resume_rule),
        "agents_with_artifact_bootstrap": _count(_artifact_bootstrap),
        "agents_with_final_response_contract": _count(_final_response_contract),
        "review_agents_with_report_artifacts": review_artifact_reports,
        "review_agent_count": len(review_agents),
    }


def _features(root: Path, entrypoints: dict[str, Any]) -> dict[str, bool]:
    plugin_root = root / "plugins" / "xlfg-engineering"
    hardening = _subagent_hardening_report(root)
    primary_text = entrypoints["plugin_primary_text"] or entrypoints["standalone_text"]
    standalone_text = entrypoints["standalone_text"]
    hooks_json = _read_text(plugin_root / "hooks" / "hooks.json")
    runs_text = _read_text(root / "xlfg" / "runs.py")
    cli_text = _read_text(root / "xlfg" / "cli.py")
    plugin_readme = _read_text(plugin_root / "README.md")
    root_readme = _read_text(root / "README.md")
    brief_blob = "\n".join([primary_text, standalone_text, plugin_readme, root_readme, runs_text])
    phase_skill_blob = "\n".join(_read_text(path) for path in sorted((plugin_root / "skills").rglob("SKILL.md")))
    fm = _frontmatter_summary(primary_text or standalone_text)

    return {
        "recall": "memory-recall.md" in brief_blob and ("recall" in brief_blob.lower() or (plugin_root / "skills" / "xlfg-recall" / "SKILL.md").exists()),
        "research_lane": "research.md" in brief_blob or "external research" in brief_blob.lower(),
        "run_card": "single source of truth" in brief_blob.lower() or "run card" in brief_blob.lower(),
        "intent_ssot": "intent contract" in runs_text.lower() and _runtime_legacy_query_contract_refs(root)["count"] == 0,
        "lean_core_artifacts": _seeded_run_artifacts(root)["file_count"] <= 6,
        "autonomous_macro": "one autonomous run" in brief_blob.lower() or "do the full sdlc here" in brief_blob.lower(),
        "mandatory_intent_gate": "xlfg-intent-phase" in primary_text and "needs-user-answer" in primary_text,
        "multi_objective_splitter": "objective groups" in brief_blob.lower() and "split" in primary_text.lower(),
        "verify": (root / "xlfg" / "verify.py").exists() and ("verification.md" in brief_blob or "xlfg verify" in brief_blob),
        "review": "review" in primary_text.lower(),
        "compound": "compound" in primary_text.lower(),
        "audit": "audit" in cli_text and (plugin_root / "commands" / "xlfg-audit.md").exists(),
        "intent_eval_suite": "eval-intent" in cli_text and (root / "xlfg" / "intent_eval.py").exists(),
        "benchmark_doc": (root / "docs" / "benchmarking.md").exists(),
        "skill_native": entrypoints["standalone_skill_exists"] or any((plugin_root / "skills").glob("*/SKILL.md")),
        "standalone_short_name_pack": entrypoints["standalone_skill_exists"],
        "consent_reduction": bool(fm["allowed_tools"]) or "ExitPlanMode" in hooks_json or "ExitPlanMode" in primary_text,
        "skill_hooks": fm["has_hooks"],
        "plugin_hooks": (plugin_root / "hooks" / "hooks.json").exists(),
        "hook_auto_exit_plan": "ExitPlanMode" in hooks_json or "ExitPlanMode" in primary_text,
        "subagent_stop_guard": "SubagentStop" in hooks_json and "subagent-stop-guard.mjs" in hooks_json and (plugin_root / "scripts" / "subagent-stop-guard.mjs").exists(),
        "packet_header_discipline": "PRIMARY_ARTIFACT:" in brief_blob and "DONE_CHECK:" in brief_blob and "RETURN_CONTRACT:" in brief_blob,
        "sequential_artifact_planning": "sequential" in _read_text(plugin_root / "skills" / "xlfg-context-phase" / "SKILL.md").lower() and "sequential" in _read_text(plugin_root / "skills" / "xlfg-plan-phase" / "SKILL.md").lower(),
        "effort_frontmatter": bool(fm["effort"]),
        "plugin_namespace_documented": "/xlfg-engineering:xlfg" in plugin_readme and "standalone" in plugin_readme.lower() and "/xlfg" in plugin_readme,
        "single_main_entrypoint": entrypoints["plugin_primary_kind"] != "none" and not entrypoints["command_skill_collision"],
        "batch_phase_skills": entrypoints["plugin_phase_skill_count"] >= 8 and entrypoints["standalone_phase_skill_count"] >= 8 and "Skill(" in (primary_text or standalone_text) and "batch of hidden phase skills" in brief_blob.lower(),
        "just_in_time_phase_loading": "just-in-time" in brief_blob.lower() or "load only the current phase skill" in brief_blob.lower(),
        "no_legacy_task_tool": not LEGACY_TASK_TOOL_RE.search(primary_text or standalone_text),
        "no_repo_relative_plugin_refs": entrypoints["repo_relative_plugin_refs"] == 0,
        "plugin_name_frontmatter_avoided": entrypoints["plugin_name_frontmatter_count"] == 0,
        "background_support_skills": entrypoints["background_support_skills"],
        "explicit_subagent_tools": hardening["plugin_agent_count"] > 0 and hardening["agents_with_tools_allowlist"] == hardening["plugin_agent_count"],
        "foreground_specialists": hardening["plugin_agent_count"] > 0 and hardening["agents_with_background_false"] == hardening["plugin_agent_count"],
        "short_lived_specialists": hardening["plugin_agent_count"] > 0 and hardening["agents_with_short_turn_budgets"] == hardening["plugin_agent_count"],
        "leaf_specialists": hardening["plugin_agent_count"] > 0 and hardening["agents_with_leaf_worker_tools"] == hardening["plugin_agent_count"],
        "proactive_delegation_descriptions": hardening["plugin_agent_count"] > 0 and hardening["agents_with_proactive_description"] == hardening["plugin_agent_count"],
        "specialist_identity_contracts": hardening["plugin_agent_count"] > 0 and hardening["agents_with_specialist_identity_contract"] == hardening["plugin_agent_count"],
        "status_contracts": hardening["plugin_agent_count"] > 0 and hardening["agents_with_status_contract"] == hardening["plugin_agent_count"],
        "review_artifact_lane": hardening["review_agent_count"] > 0 and hardening["review_agents_with_report_artifacts"] == hardening["review_agent_count"],
        "completion_barrier_contracts": hardening["plugin_agent_count"] > 0 and hardening["agents_with_completion_barrier"] == hardening["plugin_agent_count"],
        "resume_ready_specialists": hardening["plugin_agent_count"] > 0 and hardening["agents_with_resume_rule"] == hardening["plugin_agent_count"] and "sendmessage" in phase_skill_blob.lower(),
        "artifact_bootstrap_specialists": hardening["plugin_agent_count"] > 0 and hardening["agents_with_artifact_bootstrap"] == hardening["plugin_agent_count"],
        "final_response_contracts": hardening["plugin_agent_count"] > 0 and hardening["agents_with_final_response_contract"] == hardening["plugin_agent_count"],
        "phase_sendmessage_resume": "SendMessage" in phase_skill_blob,
        "review_packet_splitting": "one change cluster plus one review lens" in _read_text(plugin_root / "skills" / "xlfg-review-phase" / "SKILL.md"),
        "atomic_task_packets": "primary_artifact" in runs_text and "done_check" in runs_text and ("task-brief.md" in brief_blob or "task-brief.md" in _read_text(plugin_root / "skills" / "xlfg-plan-phase" / "SKILL.md") or "task-brief.md" in _read_text(plugin_root / "skills" / "xlfg-implement-phase" / "SKILL.md")) and (plugin_root / "agents" / "planning" / "xlfg-task-divider.md").exists(),
        "task_divider_agent": (plugin_root / "agents" / "planning" / "xlfg-task-divider.md").exists(),
        "standalone_agent_pack": hardening["standalone_agent_pack"],
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
        "read_tax": min(16.0, max(0, implement_reads - 1) * 3.0 + max(0, verify_reads - 1) * 3.0 + max(0, review_reads - 1) * 2.0),
        "fanout_tax": min(12.0, max(0, (planning_standard_budget or 0) - 1) * 3.0 + max(0, implementation_default_agents - 1) * 6.0 + max(0, (review_standard_budget or 0) - 1) * 3.0),
        "routing_tax": 0.0 if has_haiku else 5.0,
        "compatibility_tax": (
            0.0
            + (0.0 if features.get("autonomous_macro") else 4.0)
            + (0.0 if features.get("consent_reduction") else 4.0)
            + (0.0 if features.get("effort_frontmatter") else 3.0)
            + (0.0 if features.get("single_main_entrypoint") else 5.0)
            + (0.0 if features.get("batch_phase_skills") else 4.0)
            + (0.0 if features.get("no_legacy_task_tool") else 3.0)
            + (0.0 if features.get("no_repo_relative_plugin_refs") else 3.0)
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
    score += 10 if features.get("intent_ssot") else 0
    score += 10 if features.get("lean_core_artifacts") else 0
    score += 12 if features.get("autonomous_macro") else 0
    score += 12 if features.get("mandatory_intent_gate") else 0
    score += 8 if features.get("verify") else 0
    score += 8 if features.get("review") else 0
    score += 6 if features.get("compound") else 0
    score += 6 if features.get("audit") else 0
    score += 6 if features.get("intent_eval_suite") else 0
    score += 6 if features.get("benchmark_doc") else 0
    score += 6 if features.get("single_main_entrypoint") else 0
    score += 6 if features.get("multi_objective_splitter") else 0
    score += 6 if features.get("batch_phase_skills") else 0
    score += 4 if features.get("subagent_stop_guard") else 0
    score += 4 if features.get("packet_header_discipline") else 0
    score += 4 if features.get("sequential_artifact_planning") else 0
    score += 4 if features.get("background_support_skills") else 0
    score += 4 if features.get("explicit_subagent_tools") else 0
    score += 4 if features.get("foreground_specialists") else 0
    score += 4 if features.get("short_lived_specialists") else 0
    score += 4 if features.get("leaf_specialists") else 0
    score += 4 if features.get("proactive_delegation_descriptions") else 0
    score += 4 if features.get("specialist_identity_contracts") else 0
    score += 4 if features.get("review_artifact_lane") else 0
    score += 4 if features.get("completion_barrier_contracts") else 0
    score += 4 if features.get("resume_ready_specialists") else 0
    score += 4 if features.get("atomic_task_packets") else 0
    score += 4 if features.get("task_divider_agent") else 0
    score += 4 if features.get("standalone_agent_pack") else 0
    score += 4 if features.get("no_legacy_task_tool") else 0
    score += 4 if version_sync_ok else 0
    return min(100, score)


def _compatibility_score(features: dict[str, bool]) -> int:
    score = 0
    score += 10 if features.get("standalone_short_name_pack") else 0
    score += 12 if features.get("consent_reduction") else 0
    score += 8 if features.get("hook_auto_exit_plan") else 0
    score += 8 if features.get("effort_frontmatter") else 0
    score += 8 if features.get("plugin_namespace_documented") else 0
    score += 12 if features.get("autonomous_macro") else 0
    score += 8 if features.get("mandatory_intent_gate") else 0
    score += 12 if features.get("single_main_entrypoint") else 0
    score += 15 if features.get("batch_phase_skills") else 0
    score += 8 if features.get("multi_objective_splitter") else 0
    score += 5 if features.get("just_in_time_phase_loading") else 0
    score += 5 if features.get("no_legacy_task_tool") else 0
    score += 5 if features.get("explicit_subagent_tools") else 0
    score += 5 if features.get("foreground_specialists") else 0
    score += 5 if features.get("short_lived_specialists") else 0
    score += 5 if features.get("leaf_specialists") else 0
    score += 5 if features.get("proactive_delegation_descriptions") else 0
    score += 5 if features.get("review_artifact_lane") else 0
    score += 5 if features.get("completion_barrier_contracts") else 0
    score += 5 if features.get("resume_ready_specialists") else 0
    score += 5 if features.get("atomic_task_packets") else 0
    score += 4 if features.get("subagent_stop_guard") else 0
    score += 3 if features.get("packet_header_discipline") else 0
    score += 3 if features.get("sequential_artifact_planning") else 0
    score += 3 if features.get("no_repo_relative_plugin_refs") else 0
    score += 2 if features.get("plugin_name_frontmatter_avoided") else 0
    return min(100, score)


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
    if not features.get("intent_ssot"):
        recs.append("Keep intent in spec.md only; remove active query-contract.md usage from runtime prompts and entrypoints.")
    if not features.get("mandatory_intent_gate"):
        recs.append("Add a mandatory intent gate before broad repo fan-out so messy queries are split and clarified early.")
    if not features.get("intent_eval_suite"):
        recs.append("Ship an intent evaluation harness so bad prompts are scored with artifacts instead of intuition.")
    if plan_required_artifacts > 6:
        recs.append("Collapse mandatory planning artifacts into spec.md plus proof/status docs.")
    if implement_reads > 1 or verify_reads > 1 or review_reads > 1:
        recs.append("Reduce initial read amplification; start from spec.md and only dive deeper on demand.")
    if implementation_default_agents > 1:
        recs.append("Reduce default fan-out to one implementation owner; make extra agents trigger-based.")
    if (review_standard_budget or 0) > 1:
        recs.append("Cap the standard review budget at one lens unless risk justifies more.")
    if (planning_standard_budget or 0) > 1:
        recs.append("Keep planning specialist budget minimal; the lead should synthesize instead of delegating routine thought.")
    if not has_haiku:
        recs.append("Route read-only exploration and environment triage to lighter models to lower cost and latency.")
    if not features.get("single_main_entrypoint"):
        recs.append("Expose exactly one primary /xlfg entrypoint per install mode; avoid command+skill collisions.")
    if not features.get("explicit_subagent_tools"):
        recs.append("Give every specialist an explicit tool allowlist instead of relying on inherited permissions or prose-only restrictions.")
    if not features.get("foreground_specialists"):
        recs.append("Keep phase-critical specialists in the foreground so early stop and silent write failures are easier to detect.")
    if not features.get("short_lived_specialists"):
        recs.append("Cap specialist turn budgets aggressively so stuck lanes fail fast instead of looking hung for dozens of turns.")
    if not features.get("leaf_specialists"):
        recs.append("Keep specialists as leaf workers without Agent/SendMessage tools so nested delegation cannot deadlock or explode context.")
    if not features.get("proactive_delegation_descriptions"):
        recs.append("Make specialist descriptions explicitly proactive so Claude delegates to them more often.")
    if not features.get("review_artifact_lane"):
        recs.append("Make each review lens write its own artifact so the conductor can trust and synthesize specialist review instead of ignoring it.")
    if not features.get("completion_barrier_contracts"):
        recs.append("Harden every specialist with an explicit completion barrier so progress notes are never mistaken for finished work.")
    if not features.get("subagent_stop_guard"):
        recs.append("Add a deterministic SubagentStop guard so xlfg specialists cannot stop on progress chatter alone.")
    if not features.get("packet_header_discipline"):
        recs.append("Prefix every delegated packet with PRIMARY_ARTIFACT, FILE_SCOPE, DONE_CHECK, and RETURN_CONTRACT headers.")
    if not features.get("sequential_artifact_planning"):
        recs.append("Default artifact-producing planning/context lanes to sequential dispatch; parallelize only truly independent read-mostly packets.")
    if not features.get("resume_ready_specialists"):
        recs.append("Resume the same specialist once on incomplete returns instead of replacing it or accepting setup chatter as completion.")
    if not features.get("atomic_task_packets"):
        recs.append("Split delegation into atomic task packets with one mission, one artifact, and one honest done check.")
    if not features.get("task_divider_agent"):
        recs.append("Add a task-divider planning specialist so implementation never starts from vague or multi-output tasks.")
    if not features.get("batch_phase_skills"):
        recs.append("Make /xlfg a conductor over hidden phase skills instead of a monolithic prompt or a user-managed command chain.")
    if not features.get("no_legacy_task_tool"):
        recs.append("Use current Claude Code tool names such as Skill and WebSearch/WebFetch; do not reintroduce stale Task wording.")
    if not features.get("no_repo_relative_plugin_refs"):
        recs.append("Do not point slash commands at repo-relative plugin file paths; installed plugins are not laid out like the source repo.")
    if not features.get("plugin_name_frontmatter_avoided"):
        recs.append("Avoid extra plugin name frontmatter beyond the intentional main-command alias, so namespacing stays predictable.")
    if not features.get("standalone_short_name_pack"):
        recs.append("Ship a standalone .claude/skills/xlfg pack so users can get a direct /xlfg command without plugin namespacing.")
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
    entrypoints = _entrypoint_report(root)
    words = _word_metrics(root, entrypoints)
    seeded = _seeded_run_artifacts(root)
    phases = _phase_metrics(root, entrypoints)
    models = _model_report(root)
    features = _features(root, entrypoints)
    runtime_legacy_query_contract_refs = _runtime_legacy_query_contract_refs(root)
    hardening = _subagent_hardening_report(root)

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

    entrypoint_metrics = {k: v for k, v in entrypoints.items() if not k.endswith("_text")}

    return {
        "version_sync": versions,
        "metrics": {
            "entrypoints": entrypoint_metrics,
            "word_counts": words,
            "seeded_run_artifacts": seeded,
            "phase_load": phases,
            "models": models,
            "features": features,
            "subagent_hardening": hardening,
            "runtime_legacy_query_contract_refs": runtime_legacy_query_contract_refs,
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
