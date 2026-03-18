from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional


_SCENARIO_HEADING_RE = re.compile(r"^###\s+([^\s—]+)\s*(?:—\s*(.*))?$")
_KEY_VALUE_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")
_NONE_VALUES = {"", "none", "n/a", "na", "null", "nil", "tbd", "guess"}
_VALID_PHASES = {"fast", "smoke", "e2e", "manual", "full"}


def _clean_value(value: str) -> Optional[str]:
    cleaned = value.strip().strip("`")
    return None if cleaned.lower() in _NONE_VALUES else cleaned


def _normalize_key(key: str) -> str:
    return (
        key.strip()
        .lower()
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


def _split_ids(value: Optional[str]) -> List[str]:
    if not value:
        return []
    raw = value.replace(",", " ").replace("`", " ")
    return [part.strip() for part in raw.split() if part.strip()]


def parse_test_contract(path: Path) -> List[Dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    scenarios: List[Dict[str, object]] = []
    current: Optional[Dict[str, object]] = None
    collecting_steps = False
    steps: List[str] = []

    def flush_current() -> None:
        nonlocal current, steps, collecting_steps
        if current is None:
            return
        if steps:
            current["practical_steps_text"] = "\n".join(steps).strip()
            steps = []
        current.setdefault("title", "")
        current.setdefault("objective", None)
        current.setdefault("requirement_kind", "F2P")
        current.setdefault("priority", None)
        current.setdefault("query_ids", [])
        current.setdefault("fast_check", None)
        current.setdefault("ship_phase", None)
        current.setdefault("ship_check", None)
        current.setdefault("regression_check", None)
        current.setdefault("manual_smoke", None)
        current.setdefault("anti_monkey_probe", None)
        current.setdefault("notes", None)
        # normalize fields
        current["query_ids"] = _split_ids(str(current.get("query_ids_raw") or current.get("query_ids") or ""))
        rk_clean = _clean_value(str(current.get("requirement_kind") or "F2P")) or "F2P"
        rk = rk_clean.strip().upper()
        current["requirement_kind"] = rk if rk in {"F2P", "P2P"} else "F2P"
        phase_clean = _clean_value(str(current.get("ship_phase") or "")) or ""
        phase = phase_clean.strip().lower()
        current["ship_phase"] = phase if phase in _VALID_PHASES else None
        for key in ("objective", "priority", "fast_check", "ship_check", "regression_check", "manual_smoke", "anti_monkey_probe", "notes"):
            current[key] = _clean_value(str(current.get(key) or ""))
        if current.get("ship_phase") is None:
            if current.get("ship_check"):
                current["ship_phase"] = "smoke"
            elif current.get("fast_check"):
                current["ship_phase"] = "fast"
            elif current.get("manual_smoke"):
                current["ship_phase"] = "manual"
        scenarios.append(current)
        current = None
        collecting_steps = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        heading = _SCENARIO_HEADING_RE.match(line.strip())
        if heading:
            flush_current()
            sid = heading.group(1).strip()
            title = (heading.group(2) or "").strip()
            current = {"id": sid, "title": title}
            continue
        if current is None:
            continue
        kv = _KEY_VALUE_RE.match(line.strip())
        if kv:
            key = _normalize_key(kv.group(1))
            value = kv.group(2).strip()
            if key == "practical_steps":
                collecting_steps = True
                steps = []
                if value:
                    steps.append(value)
                continue
            collecting_steps = False
            if key in {"query_ids", "query_intent_ids"}:
                current["query_ids_raw"] = value
            else:
                current[key] = value
            continue
        if collecting_steps:
            stripped = line.strip()
            if stripped and (stripped[0].isdigit() or stripped.startswith("- ")):
                steps.append(stripped)
            elif stripped:
                steps.append(stripped)
            else:
                collecting_steps = False

    flush_current()
    return scenarios


def parse_test_readiness_verdict(path: Path) -> Optional[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    for raw_line in text.splitlines():
        line = raw_line.strip().lower()
        if not line:
            continue
        if "ready" in line and "revise" in line:
            continue
        if line in {"- `ready`", "- ready", "ready", "`ready`"}:
            return "READY"
        if line in {"- `revise`", "- revise", "revise", "`revise`"}:
            return "REVISE"
        if line.startswith("verdict:"):
            rest = line.split(":", 1)[1].strip().strip("`")
            if rest == "ready":
                return "READY"
            if rest == "revise":
                return "REVISE"
    return None
