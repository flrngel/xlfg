from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from .contracts import parse_test_contract, parse_test_readiness_verdict
from .detect import detect_commands
from .doctor import cleanup_dev_server, ensure_dev_server
from .runs import latest_run_id
from .util import ensure_dir


def _should_set_ci_env(command: str) -> bool:
    c = command.strip()
    return c.startswith(("npm ", "pnpm ", "yarn ", "bun ", "npx ", "node "))


def _run_cmd(command: str, log_path: Path, *, timeout_sec: Optional[int] = None) -> int:
    ensure_dir(log_path.parent)
    env = os.environ.copy()

    if _should_set_ci_env(command) and "CI" not in env:
        env["CI"] = "1"

    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"$ {command}\n")
        if timeout_sec:
            f.write(f"# timeout: {timeout_sec}s\n")
        if env.get("CI") == "1":
            f.write("# env: CI=1\n")
        f.write("\n")
        f.flush()

        try:
            completed = subprocess.run(
                command,
                shell=True,
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                timeout=timeout_sec,
            )
            return int(completed.returncode)
        except subprocess.TimeoutExpired:
            f.write("\n[XLFG] TIMEOUT\n")
            return 124


def _tail(path: Path, max_lines: int = 80) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(lines[-max_lines:])
    except Exception:
        return ""


def _recommended_mode_from_harness_profile(docs_run_dir: Path) -> Literal["fast", "full"]:
    profile_path = docs_run_dir / "harness-profile.md"
    try:
        text = profile_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return "full"

    selected_profile: Optional[str] = None
    recommended_mode: Optional[str] = None
    for raw_line in text.splitlines():
        line = raw_line.strip().lower()
        if "selected profile" in line:
            continue
        if line.startswith("- `quick`") or line == "- quick":
            selected_profile = "quick"
        elif line.startswith("- `standard`") or line == "- standard":
            selected_profile = "standard"
        elif line.startswith("- `deep`") or line == "- deep":
            selected_profile = "deep"
        if "recommended verify mode" in line:
            has_fast = "fast" in line
            has_full = "full" in line
            if has_fast and not has_full:
                recommended_mode = "fast"
            elif has_full and not has_fast:
                recommended_mode = "full"

    if recommended_mode in {"fast", "full"}:
        return recommended_mode  # type: ignore[return-value]
    if selected_profile == "quick":
        return "fast"
    return "full"


def _phase_sort_key(phase: str) -> int:
    order = {"fast": 0, "smoke": 1, "e2e": 2, "full": 3}
    return order.get(phase, 99)


def _normalize_phase(phase: Optional[str]) -> str:
    p = (phase or "").strip().lower()
    return p if p in {"fast", "smoke", "e2e", "full"} else "fast"


def _dedupe_planned_commands(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str, str]] = set()
    for item in items:
        cmd = str(item.get("command") or "").strip()
        phase = _normalize_phase(str(item.get("phase") or "fast"))
        scenario_id = str(item.get("scenario_id") or "")
        if not cmd:
            continue
        key = (phase, cmd, scenario_id)
        if key in seen:
            continue
        seen.add(key)
        normalized = dict(item)
        normalized["command"] = cmd
        normalized["phase"] = phase
        out.append(normalized)
    out.sort(key=lambda x: (_phase_sort_key(str(x.get("phase") or "fast")), str(x.get("scenario_id") or "~"), str(x.get("purpose") or "")))
    return out


def _supplemental_detected_commands(detected: Dict[str, Any], mode: Literal["fast", "full"]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for cmd in list(detected.get("verify_fast") or []):
        items.append({"phase": "fast", "command": cmd, "scenario_id": None, "purpose": "supplemental-fast"})
    if mode == "full":
        for phase_name, key in (("smoke", "smoke"), ("e2e", "e2e"), ("full", "verify_full")):
            for cmd in list(detected.get(key) or []):
                items.append({"phase": phase_name, "command": cmd, "scenario_id": None, "purpose": f"supplemental-{phase_name}"})
    return items


def _scenario_commands_and_issues(
    scenarios: List[Dict[str, object]], mode: Literal["fast", "full"]
) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Dict[str, Any]]]:
    items: List[Dict[str, Any]] = []
    issues: List[str] = []
    meta: Dict[str, Dict[str, Any]] = {}
    f2p_count = 0

    for scenario in scenarios:
        sid = str(scenario.get("id") or "").strip()
        if not sid:
            continue
        kind = str(scenario.get("requirement_kind") or "F2P").strip().upper()
        if kind == "F2P":
            f2p_count += 1
        meta[sid] = {
            "title": scenario.get("title"),
            "objective": scenario.get("objective"),
            "requirement_kind": kind,
            "priority": scenario.get("priority"),
            "query_ids": list(scenario.get("query_ids") or []),
            "ship_phase": scenario.get("ship_phase"),
            "manual_smoke": scenario.get("manual_smoke"),
            "anti_monkey_probe": scenario.get("anti_monkey_probe"),
            "planned": [],
        }
        fast_check = str(scenario.get("fast_check") or "").strip() or None
        ship_phase = str(scenario.get("ship_phase") or "").strip().lower() or None
        ship_check = str(scenario.get("ship_check") or "").strip() or None
        regression_check = str(scenario.get("regression_check") or "").strip() or None
        manual_smoke = str(scenario.get("manual_smoke") or "").strip() or None

        if kind == "F2P" and not fast_check:
            issues.append(f"Scenario {sid} is missing a practical fast_check for iteration.")
        if kind == "F2P" and ship_phase in {None, ""}:
            issues.append(f"Scenario {sid} is missing ship_phase.")
        if kind == "F2P" and ship_phase in {"smoke", "e2e", "full", "fast"} and not ship_check:
            if ship_phase == "fast" and fast_check:
                ship_check = fast_check
            else:
                issues.append(f"Scenario {sid} is missing ship_check for ship_phase={ship_phase}.")
        if kind == "F2P" and ship_phase == "manual" and not manual_smoke:
            issues.append(f"Scenario {sid} requires manual proof but manual_smoke is missing.")

        if fast_check:
            item = {
                "phase": "fast",
                "command": fast_check,
                "scenario_id": sid,
                "purpose": "fast-proof",
                "kind": kind,
            }
            items.append(item)
            meta[sid]["planned"].append(item)

        if mode == "full":
            if ship_phase == "manual":
                issues.append(f"Scenario {sid} still requires manual ship proof: {manual_smoke or 'manual smoke steps missing'}")
            elif ship_phase in {"fast", "smoke", "e2e", "full"} and ship_check:
                item = {
                    "phase": _normalize_phase(ship_phase),
                    "command": ship_check,
                    "scenario_id": sid,
                    "purpose": "ship-proof",
                    "kind": kind,
                }
                items.append(item)
                meta[sid]["planned"].append(item)
            if regression_check:
                item = {
                    "phase": "full",
                    "command": regression_check,
                    "scenario_id": sid,
                    "purpose": "regression-guard",
                    "kind": kind,
                }
                items.append(item)
                meta[sid]["planned"].append(item)
        else:
            if ship_phase == "fast" and ship_check:
                item = {
                    "phase": "fast",
                    "command": ship_check,
                    "scenario_id": sid,
                    "purpose": "ship-proof",
                    "kind": kind,
                }
                items.append(item)
                meta[sid]["planned"].append(item)

    if f2p_count == 0:
        issues.append("Test contract has no F2P scenario contracts. xlfg needs at least one changed/new scenario to prove.")

    return _dedupe_planned_commands(items), issues, meta


def _write_verify_fix_plan(docs_run_dir: Path, reason: str, rerun: str) -> None:
    fix_plan = docs_run_dir / "verify-fix-plan.md"
    content = """# Verify fix plan

## First actionable failure
- {reason}

## Minimum fix steps
- [ ] Address the failure above
- [ ] Re-run `{rerun}`
""".format(reason=reason, rerun=rerun)
    fix_plan.write_text(content, encoding="utf-8")


def verify(
    root: Path,
    run_id: Optional[str],
    mode: Optional[Literal["fast", "full"]] = None,
) -> Dict[str, Any]:
    """Run layered verification and write evidence."""

    rid = run_id or latest_run_id(root)
    if not rid:
        raise RuntimeError("No run found. Run `xlfg init` and `xlfg start ...` first.")

    docs_run_dir = root / "docs" / "xlfg" / "runs" / rid
    dx_run_dir = root / ".xlfg" / "runs" / rid
    ensure_dir(docs_run_dir)
    ensure_dir(dx_run_dir)

    actual_mode: Literal["fast", "full"] = mode or _recommended_mode_from_harness_profile(docs_run_dir)

    detected = detect_commands(root)
    scenarios = parse_test_contract(docs_run_dir / "test-contract.md")
    readiness = parse_test_readiness_verdict(docs_run_dir / "test-readiness.md")
    scenario_commands, contract_issues, scenario_meta = _scenario_commands_and_issues(scenarios, actual_mode)
    supplemental_commands = _supplemental_detected_commands(detected, actual_mode)
    planned_commands = _dedupe_planned_commands([*scenario_commands, *supplemental_commands])

    if readiness == "REVISE":
        contract_issues.insert(0, "test-readiness.md verdict is REVISE. Return to planning before implementation or verification.")
    elif readiness is None:
        contract_issues.insert(0, "test-readiness.md verdict is missing or unreadable.")

    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = dx_run_dir / "verify" / ts
    ensure_dir(log_dir)

    steps: List[Dict[str, Any]] = []
    ok = True

    timeout_env = os.environ.get("XLFG_VERIFY_TIMEOUT_SECS")
    timeout_sec: Optional[int]
    if timeout_env is not None:
        try:
            t = int(timeout_env)
            timeout_sec = None if t <= 0 else t
        except Exception:
            timeout_sec = None
    else:
        timeout_sec = 600 if actual_mode == "fast" else 1800

    need_doctor = any(str(item.get("phase")) in {"smoke", "e2e"} for item in planned_commands)
    doctor_report: Optional[Dict[str, Any]] = None
    doctor_handle = None
    cleanup_report: Optional[Dict[str, Any]] = None

    try:
        if need_doctor:
            doctor_report, doctor_handle = ensure_dev_server(root, rid, detected.get("dev"))
            if doctor_report.get("status") not in {"reused", "started"}:
                ok = False

        if ok:
            for i, item in enumerate(planned_commands, start=1):
                phase = str(item.get("phase") or "fast")
                cmd = str(item.get("command") or "")
                scenario_id = item.get("scenario_id")
                purpose = str(item.get("purpose") or "")
                name = f"{i:02d}-{phase}"
                if scenario_id:
                    name += f"-{scenario_id}"
                log_file = log_dir / f"{name}.log"
                code = _run_cmd(cmd, log_file, timeout_sec=timeout_sec)
                step = {
                    "phase": phase,
                    "command": cmd,
                    "exit_code": code,
                    "log_file": str(log_file),
                    "scenario_id": scenario_id,
                    "purpose": purpose,
                }
                steps.append(step)
                (log_dir / f"{name}.exitcode").write_text(str(code), encoding="utf-8")
                if code != 0:
                    ok = False
                    break
    finally:
        if doctor_handle is not None:
            cleanup_report = cleanup_dev_server(doctor_handle)

    scenario_results: Dict[str, Dict[str, Any]] = {}
    for sid, meta in scenario_meta.items():
        related = [s for s in steps if s.get("scenario_id") == sid]
        fast_ok = any(s["purpose"] == "fast-proof" and s["exit_code"] == 0 for s in related)
        ship_ok = any(s["purpose"] == "ship-proof" and s["exit_code"] == 0 for s in related)
        regression_ok = any(s["purpose"] == "regression-guard" and s["exit_code"] == 0 for s in related)
        scenario_results[sid] = {
            **meta,
            "executed": related,
            "fast_ok": fast_ok,
            "ship_ok": ship_ok,
            "regression_ok": regression_ok,
        }

    if not planned_commands:
        contract_issues.append("No verification commands were compiled from test-contract.md or detected project commands.")

    executed_scenario_commands = [s for s in steps if s.get("scenario_id")]
    if scenarios and not executed_scenario_commands:
        contract_issues.append("No scenario-targeted checks were executed. xlfg cannot claim proof without at least one scenario run.")

    if actual_mode == "full":
        for sid, result in scenario_results.items():
            if str(result.get("requirement_kind")) != "F2P":
                continue
            ship_phase = str(result.get("ship_phase") or "")
            if ship_phase in {"fast", "smoke", "e2e", "full"} and not result.get("ship_ok"):
                contract_issues.append(f"Scenario {sid} has no passing ship proof in full mode.")
            if not result.get("fast_ok"):
                contract_issues.append(f"Scenario {sid} has no passing fast proof.")
    else:
        for sid, result in scenario_results.items():
            if str(result.get("requirement_kind")) != "F2P":
                continue
            if not result.get("fast_ok"):
                contract_issues.append(f"Scenario {sid} has no passing fast proof.")

    if contract_issues:
        ok = False

    verification_md = docs_run_dir / "verification.md"
    rerun_cmd = f"xlfg verify --run {rid} --mode {actual_mode}"
    header = f"## Verification run {ts} ({actual_mode})\n\n"
    body_lines: List[str] = []
    body_lines.append(f"Result: {'GREEN' if ok else 'RED'}")
    body_lines.append(f"Log dir: `{log_dir}`")
    body_lines.append("")
    body_lines.append("### Test readiness")
    body_lines.append(f"- Verdict: {readiness or 'MISSING'}")
    body_lines.append("")

    if doctor_report is not None:
        body_lines.append("### Environment doctor")
        body_lines.append(f"- Status: {doctor_report.get('status')}")
        if doctor_report.get("command"):
            body_lines.append(f"- Command: `{doctor_report['command']}`")
        if doctor_report.get("health_detail"):
            body_lines.append(f"- Health detail: {doctor_report['health_detail']}")
        if doctor_report.get("report_md"):
            body_lines.append(f"- Report: `{doctor_report['report_md']}`")
        if cleanup_report:
            body_lines.append(f"- Cleanup: {cleanup_report.get('status')}")
        body_lines.append("")

    body_lines.append("### Scenario contracts")
    if scenario_results:
        for sid, result in scenario_results.items():
            qids = " ".join(result.get("query_ids") or [])
            body_lines.append(
                f"- {sid} ({result.get('requirement_kind')}, {result.get('ship_phase')}) | query IDs: {qids or '-'} | fast_ok={result.get('fast_ok')} | ship_ok={result.get('ship_ok')} | regression_ok={result.get('regression_ok')}"
            )
    else:
        body_lines.append("- No scenario contracts parsed from test-contract.md")
    body_lines.append("")

    if planned_commands:
        body_lines.append("### Commands")
        for s in steps:
            sid = f" [{s['scenario_id']}]" if s.get("scenario_id") else ""
            purpose = f" {s['purpose']}" if s.get("purpose") else ""
            body_lines.append(
                f"- [{s['phase']}]`{sid}`{purpose} `{s['command']}` → exit {s['exit_code']} (log: `{s['log_file']}`)"
            )
        body_lines.append("")

    failure_reason: Optional[str] = None
    if not planned_commands:
        failure_reason = "No verification commands were compiled. Write practical scenario checks in test-contract.md and/or populate docs/xlfg/knowledge/commands.json."
        body_lines.append("### First actionable failure")
        body_lines.append(f"- {failure_reason}")
    elif doctor_report is not None and doctor_report.get("status") not in {"reused", "started"}:
        failure_reason = (
            "Environment doctor could not prepare a healthy dev server: "
            f"{doctor_report.get('status')} ({doctor_report.get('health_detail') or 'no detail'})."
        )
        body_lines.append("### First actionable failure")
        body_lines.append(f"- {failure_reason}")
    elif contract_issues:
        failure_reason = contract_issues[0]
        body_lines.append("### Contract / proof issues")
        for issue in contract_issues:
            body_lines.append(f"- {issue}")
    elif not ok and steps:
        last = steps[-1]
        failure_reason = f"`{last['command']}` failed with exit code {last['exit_code']}."
        body_lines.append("### First actionable failure")
        body_lines.append(f"- {failure_reason}")
        body_lines.append("")
        body_lines.append("### First failing output (tail)")
        body_lines.append("```")
        body_lines.append(_tail(Path(last["log_file"])))
        body_lines.append("```")
    else:
        body_lines.append("### First actionable failure")
        body_lines.append("- None")

    results_json = {
        "run_id": rid,
        "timestamp": ts,
        "mode": actual_mode,
        "all_green": ok,
        "doctor": doctor_report,
        "cleanup": cleanup_report,
        "commands": steps,
        "detected": detected,
        "test_readiness": readiness,
        "scenario_contracts": scenarios,
        "scenario_results": scenario_results,
        "contract_issues": contract_issues,
    }
    (log_dir / "results.json").write_text(json.dumps(results_json, indent=2), encoding="utf-8")

    content = header + "\n".join(body_lines) + "\n\n"
    if verification_md.exists():
        with verification_md.open("a", encoding="utf-8") as f:
            f.write(content)
    else:
        verification_md.write_text("# Verification\n\n" + content, encoding="utf-8")

    if not ok:
        _write_verify_fix_plan(docs_run_dir, failure_reason or "Verification failed.", rerun_cmd)

    return {
        "run_id": rid,
        "ok": ok,
        "log_dir": str(log_dir),
        "steps": steps,
        "doctor": doctor_report,
        "cleanup": cleanup_report,
        "detected": detected,
        "test_readiness": readiness,
        "scenario_contracts": scenarios,
        "scenario_results": scenario_results,
        "contract_issues": contract_issues,
    }
