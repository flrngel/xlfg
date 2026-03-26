from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .contracts import parse_test_contract


_HEADING_RE = re.compile(r"^##\s+(.*)$", re.MULTILINE)
_INLINE_ID_BULLET_RE = re.compile(r"^(?:-\s+)?`?([A-Z]\d+)`?\s*[:—-]\s*(.*)$")
_OBJECTIVE_BULLET_RE = re.compile(
    r"^-\s+`?(O\d+)`?\s*[—-]\s*(.*?)(?:;\s*covers:\s*(.*?))?(?:;\s*depends_on:\s*(.*?))?(?:;\s*completion:\s*(.*))?$"
)
_TASK_BULLET_RE = re.compile(
    r"^-\s+`?(T\d+)`?\s*[—-]\s*(.*?)(?:;\s*objectives:\s*(.*?))?(?:;\s*scenarios:\s*(.*?))?(?:;\s*owner:\s*(.*))?$"
)
_TOP_BULLET_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _section_map(text: str) -> Dict[str, str]:
    matches = list(_HEADING_RE.finditer(text))
    out: Dict[str, str] = {}
    for i, match in enumerate(matches):
        title = match.group(1).strip().lower()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[title] = text[start:end].strip("\n")
    return out


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("/", "_").replace(" ", "_").replace("-", "_")


def _clean_item(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = re.sub(r"^\*+|\*+$", "", value)
    return value.strip()


def _split_ids(value: str) -> List[str]:
    raw = value.replace(",", " ").replace("`", " ")
    return [part.strip() for part in raw.split() if part.strip()]


def parse_spec_artifact(path: Path) -> Dict[str, Any]:
    text = _read_text(path)
    sections = _section_map(text)
    intent = sections.get("intent contract", "")
    objectives_section = sections.get("objective groups", "")
    task_map = sections.get("task map", "")

    result: Dict[str, Any] = {
        "resolution": None,
        "work_kind": None,
        "raw_request": None,
        "direct_asks": [],
        "implied_asks": [],
        "acceptance_criteria": [],
        "non_goals": [],
        "constraints_requested": [],
        "assumptions_to_proceed": [],
        "blocking_ambiguities": [],
        "carry_forward_anchor": None,
        "objective_groups": [],
        "task_map": [],
    }

    list_fields = {
        "direct_asks",
        "implied_asks",
        "acceptance_criteria",
        "non_goals",
        "constraints_actually_requested",
        "assumptions_to_proceed",
        "blocking_ambiguities",
    }
    current_list: Optional[str] = None
    for raw in intent.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped:
            continue
        if line.startswith("  - ") and current_list:
            item = _clean_item(line[4:])
            if item and item != "...":
                if current_list == "constraints_actually_requested":
                    result["constraints_requested"].append(item)
                else:
                    result[current_list].append(item)
            continue
        if line.startswith("- "):
            m = _TOP_BULLET_RE.match(stripped)
            if not m:
                current_list = None
                continue
            key = _normalize_key(m.group(1))
            value = _clean_item(m.group(2))
            current_list = key if key in list_fields else None
            if key == "resolution" and value and value != "...":
                result["resolution"] = value
            elif key == "work_kind" and value and value != "...":
                result["work_kind"] = value
            elif key == "raw_request" and value and value != "...":
                result["raw_request"] = value
            elif key == "carry_forward_anchor" and value and value != "...":
                result["carry_forward_anchor"] = value
            elif key == "non_goals" and value and value != "...":
                result["non_goals"].append(value)
                current_list = "non_goals"
            elif key == "constraints_actually_requested" and value and value != "...":
                result["constraints_requested"].append(value)
                current_list = "constraints_actually_requested"
            elif key == "assumptions_to_proceed" and value and value != "...":
                result["assumptions_to_proceed"].append(value)
                current_list = "assumptions_to_proceed"
            elif key == "blocking_ambiguities" and value and value != "...":
                result["blocking_ambiguities"].append(value)
                current_list = "blocking_ambiguities"
            elif key in {"direct_asks", "implied_asks", "acceptance_criteria"} and value and value != "...":
                # tolerate single-line forms
                result[key].append(value)
                current_list = key

    for raw in objectives_section.splitlines():
        stripped = raw.strip()
        if not stripped.startswith("- "):
            continue
        m = _OBJECTIVE_BULLET_RE.match(stripped)
        if not m:
            continue
        oid, goal, covers, depends, completion = m.groups()
        result["objective_groups"].append(
            {
                "id": oid,
                "goal": _clean_item(goal),
                "covers": _split_ids(covers or ""),
                "depends_on": _clean_item(depends or "") or None,
                "completion": _clean_item(completion or "") or None,
            }
        )

    for raw in task_map.splitlines():
        stripped = raw.strip()
        if not stripped.startswith("- "):
            continue
        m = _TASK_BULLET_RE.match(stripped)
        if not m:
            continue
        tid, title, objectives, scenarios, owner = m.groups()
        result["task_map"].append(
            {
                "id": tid,
                "title": _clean_item(title),
                "objectives": _split_ids(objectives or ""),
                "scenarios": _split_ids(scenarios or ""),
                "owner": _clean_item(owner or "") or None,
            }
        )

    # recover ID-tagged nested bullets
    for field, key in [("direct_asks", "direct_asks"), ("implied_asks", "implied_asks"), ("acceptance_criteria", "acceptance_criteria")]:
        if result[key]:
            cleaned: List[str] = []
            for item in result[key]:
                m = _INLINE_ID_BULLET_RE.match(item)
                cleaned.append(_clean_item(m.group(2) if m else item))
            result[key] = cleaned

    return result


def parse_workboard_artifact(path: Path) -> Dict[str, Any]:
    text = _read_text(path)
    objectives: List[Dict[str, Any]] = []
    tasks: List[Dict[str, Any]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].lower() in {"objective", "task"}:
            continue
        if len(cells) >= 6 and cells[0].startswith("O"):
            objectives.append(
                {
                    "id": cells[0],
                    "status": cells[1],
                    "covers": _split_ids(cells[2]),
                    "depends_on": cells[3],
                    "scenarios": _split_ids(cells[4]),
                    "notes": cells[5] if len(cells) > 5 else "",
                }
            )
        elif len(cells) >= 8 and cells[0].startswith("T"):
            tasks.append(
                {
                    "id": cells[0],
                    "status": cells[1],
                    "objectives": _split_ids(cells[2]),
                    "query_ids": _split_ids(cells[3]),
                    "scenario_ids": _split_ids(cells[4]),
                    "owner": cells[5],
                    "checks": cells[6],
                    "notes": cells[7] if len(cells) > 7 else "",
                }
            )
    return {"objectives": objectives, "tasks": tasks}


def _normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"`[^`]+`", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(part for part in value.split() if part)


def _token_set(value: str) -> set[str]:
    return set(_normalize_text(value).split())


def _similarity(a: str, b: str) -> float:
    na = _normalize_text(a)
    nb = _normalize_text(b)
    if not na or not nb:
        return 0.0
    if na in nb or nb in na:
        return 1.0
    ta = _token_set(a)
    tb = _token_set(b)
    if not ta or not tb:
        return 0.0
    overlap = len(ta & tb)
    return overlap / max(len(ta), len(tb))


def _best_match_count(expected: Iterable[str], actual: Iterable[str], threshold: float = 0.55) -> Tuple[int, List[Tuple[str, str, float]]]:
    remaining = list(actual)
    matched = 0
    pairs: List[Tuple[str, str, float]] = []
    for want in expected:
        best_idx = None
        best_score = 0.0
        for idx, got in enumerate(remaining):
            score = _similarity(want, got)
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx is not None and best_score >= threshold:
            got = remaining.pop(best_idx)
            matched += 1
            pairs.append((want, got, round(best_score, 3)))
        else:
            pairs.append((want, "", round(best_score, 3)))
    return matched, pairs


def _ratio(num: int, den: int) -> float:
    return round(num / den, 3) if den else 1.0


def _count_question_like(items: Iterable[str]) -> int:
    return sum(1 for item in items if "?" in item or item.lower().startswith(("which ", "what ", "should ", "is ", "are ", "do ", "does ")))


def grade_intent_artifacts(
    *,
    fixture: Dict[str, Any],
    spec_path: Path,
    test_contract_path: Optional[Path] = None,
    workboard_path: Optional[Path] = None,
) -> Dict[str, Any]:
    expected = dict(fixture.get("expected") or {})
    spec = parse_spec_artifact(spec_path)
    test_contract = parse_test_contract(test_contract_path) if test_contract_path and test_contract_path.exists() else []
    workboard = parse_workboard_artifact(workboard_path) if workboard_path and workboard_path.exists() else {"objectives": [], "tasks": []}

    expected_objectives = [item.get("goal", item) if isinstance(item, dict) else str(item) for item in expected.get("objectives", [])]
    actual_objectives = [item.get("goal", "") for item in spec.get("objective_groups", [])]

    direct_match, direct_pairs = _best_match_count(expected.get("direct_asks", []), spec.get("direct_asks", []))
    implied_match, implied_pairs = _best_match_count(expected.get("implied_asks", []), spec.get("implied_asks", []))
    accept_match, accept_pairs = _best_match_count(expected.get("acceptance_criteria", []), spec.get("acceptance_criteria", []))
    objective_match, objective_pairs = _best_match_count(expected_objectives, actual_objectives, threshold=0.45)
    blocker_match, blocker_pairs = _best_match_count(expected.get("blocking_ambiguities", []), spec.get("blocking_ambiguities", []), threshold=0.45)

    actual_blob = "\n".join(
        [
            *(spec.get("direct_asks") or []),
            *(spec.get("implied_asks") or []),
            *(spec.get("acceptance_criteria") or []),
            *(actual_objectives or []),
            *(spec.get("assumptions_to_proceed") or []),
        ]
    )
    forbidden = expected.get("forbidden_claims", [])
    forbidden_hits = [claim for claim in forbidden if _similarity(claim, actual_blob) >= 0.6]

    objective_ids = {item.get("id") for item in spec.get("objective_groups", []) if item.get("id")}
    scenario_objectives = {str(s.get("objective") or "") for s in test_contract if s.get("objective")}
    task_objectives = {oid for task in workboard.get("tasks", []) for oid in task.get("objectives", [])}
    objective_scenario_coverage = _ratio(len(objective_ids & scenario_objectives), len(objective_ids)) if objective_ids else 1.0
    objective_task_coverage = _ratio(len(objective_ids & task_objectives), len(objective_ids)) if objective_ids else 1.0

    expected_work_kind = expected.get("work_kind")
    work_kind_match = 1.0 if not expected_work_kind else float(str(spec.get("work_kind") or "").strip("`").lower() == str(expected_work_kind).lower())

    max_blocking_questions = expected.get("max_blocking_questions")
    actual_blocking_questions = _count_question_like(spec.get("blocking_ambiguities", []))
    blocking_question_budget_ok = 1.0
    if isinstance(max_blocking_questions, int):
        blocking_question_budget_ok = 1.0 if actual_blocking_questions <= max_blocking_questions else 0.0

    metrics = {
        "work_kind_match": work_kind_match,
        "direct_ask_recall": _ratio(direct_match, len(expected.get("direct_asks", []))),
        "implied_ask_recall": _ratio(implied_match, len(expected.get("implied_asks", []))),
        "acceptance_recall": _ratio(accept_match, len(expected.get("acceptance_criteria", []))),
        "objective_split_recall": _ratio(objective_match, len(expected_objectives)),
        "blocking_ambiguity_recall": _ratio(blocker_match, len(expected.get("blocking_ambiguities", []))),
        "false_assumption_rate": round(len(forbidden_hits) / len(forbidden), 3) if forbidden else 0.0,
        "blocking_question_budget_ok": blocking_question_budget_ok,
        "objective_scenario_coverage": objective_scenario_coverage,
        "objective_task_coverage": objective_task_coverage,
    }
    values = [
        metrics["work_kind_match"],
        metrics["direct_ask_recall"],
        metrics["implied_ask_recall"],
        metrics["acceptance_recall"],
        metrics["objective_split_recall"],
        1.0 - metrics["false_assumption_rate"],
        metrics["blocking_question_budget_ok"],
        metrics["objective_scenario_coverage"],
        metrics["objective_task_coverage"],
    ]
    metrics["overall"] = round(sum(values) / len(values), 3)

    return {
        "fixture_id": fixture.get("id"),
        "query": fixture.get("query"),
        "spec_path": str(spec_path),
        "test_contract_path": str(test_contract_path) if test_contract_path else None,
        "workboard_path": str(workboard_path) if workboard_path else None,
        "metrics": metrics,
        "details": {
            "direct_pairs": direct_pairs,
            "implied_pairs": implied_pairs,
            "acceptance_pairs": accept_pairs,
            "objective_pairs": objective_pairs,
            "blocker_pairs": blocker_pairs,
            "forbidden_hits": forbidden_hits,
            "spec": spec,
            "scenario_ids": [s.get("id") for s in test_contract],
            "scenario_objectives": sorted(x for x in scenario_objectives if x),
            "task_objectives": sorted(x for x in task_objectives if x),
        },
    }


def _load_fixture(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_intent_fixture(
    *,
    fixture_path: Path,
    spec_path: Path,
    test_contract_path: Optional[Path] = None,
    workboard_path: Optional[Path] = None,
) -> Dict[str, Any]:
    fixture = _load_fixture(fixture_path)
    return grade_intent_artifacts(
        fixture=fixture,
        spec_path=spec_path,
        test_contract_path=test_contract_path,
        workboard_path=workboard_path,
    )


def evaluate_intent_suite(*, suite_dir: Path, artifacts_root: Path) -> Dict[str, Any]:
    cases = sorted(suite_dir.glob("*.json"))
    reports: List[Dict[str, Any]] = []
    for case in cases:
        cid = case.stem
        artifact_dir = artifacts_root / cid
        reports.append(
            evaluate_intent_fixture(
                fixture_path=case,
                spec_path=artifact_dir / "spec.md",
                test_contract_path=artifact_dir / "test-contract.md",
                workboard_path=artifact_dir / "workboard.md",
            )
        )
    overall = round(sum(r["metrics"]["overall"] for r in reports) / len(reports), 3) if reports else 0.0
    return {"case_count": len(reports), "overall": overall, "cases": reports}
