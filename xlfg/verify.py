from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

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


def _dedupe_phased_commands(detected: Dict[str, Any], mode: Literal["fast", "full"]) -> List[Tuple[str, str]]:
    phases: List[Tuple[str, str]] = []
    seen: set[str] = set()

    def add(phase: str, commands: List[str]) -> None:
        for cmd in commands:
            c = str(cmd).strip()
            if not c or c in seen:
                continue
            seen.add(c)
            phases.append((phase, c))

    add("fast", list(detected.get("verify_fast") or []))
    if mode == "full":
        add("smoke", list(detected.get("smoke") or []))
        add("e2e", list(detected.get("e2e") or []))
        add("full", list(detected.get("verify_full") or []))
    return phases


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
    mode: Literal["fast", "full"] = "full",
) -> Dict[str, Any]:
    """Run layered verification and write evidence.

    Returns a result dict with:
      - run_id
      - ok (bool)
      - log_dir
      - doctor
      - steps: list of {phase, command, exit_code, log_file}
    """

    rid = run_id or latest_run_id(root)
    if not rid:
        raise RuntimeError("No run found. Run `xlfg init` and `xlfg start ...` first.")

    docs_run_dir = root / "docs" / "xlfg" / "runs" / rid
    dx_run_dir = root / ".xlfg" / "runs" / rid
    ensure_dir(docs_run_dir)
    ensure_dir(dx_run_dir)

    detected = detect_commands(root)
    phased_commands = _dedupe_phased_commands(detected, mode)

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
        timeout_sec = 600 if mode == "fast" else 1800

    need_doctor = any(phase in {"smoke", "e2e"} for phase, _ in phased_commands)
    doctor_report: Optional[Dict[str, Any]] = None
    doctor_handle = None
    cleanup_report: Optional[Dict[str, Any]] = None

    try:
        if need_doctor:
            doctor_report, doctor_handle = ensure_dev_server(root, rid, detected.get("dev"))
            if doctor_report.get("status") not in {"reused", "started"}:
                ok = False

        if ok:
            for i, (phase, cmd) in enumerate(phased_commands, start=1):
                name = f"{i:02d}-{phase}"
                log_file = log_dir / f"{name}.log"
                code = _run_cmd(cmd, log_file, timeout_sec=timeout_sec)
                steps.append(
                    {
                        "phase": phase,
                        "command": cmd,
                        "exit_code": code,
                        "log_file": str(log_file),
                    }
                )
                (log_dir / f"{name}.exitcode").write_text(str(code), encoding="utf-8")
                if code != 0:
                    ok = False
                    break
    finally:
        if doctor_handle is not None:
            cleanup_report = cleanup_dev_server(doctor_handle)

    if not phased_commands:
        ok = False

    verification_md = docs_run_dir / "verification.md"
    rerun_cmd = f"xlfg verify --run {rid} --mode {mode}"
    header = f"## Verification run {ts} ({mode})\n\n"
    body_lines: List[str] = []
    body_lines.append(f"Result: {'GREEN' if ok else 'RED'}")
    body_lines.append(f"Log dir: `{log_dir}`")
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

    if phased_commands:
        body_lines.append("### Commands")
        for s in steps:
            body_lines.append(
                f"- [{s['phase']}] `{s['command']}` → exit {s['exit_code']} (log: `{s['log_file']}`)"
            )
        body_lines.append("")

    failure_reason: Optional[str] = None
    if not phased_commands:
        failure_reason = "No verification commands detected. Populate docs/xlfg/knowledge/commands.json."
        body_lines.append(failure_reason)
    elif doctor_report is not None and doctor_report.get("status") not in {"reused", "started"}:
        failure_reason = (
            "Environment doctor could not prepare a healthy dev server: "
            f"{doctor_report.get('status')} ({doctor_report.get('health_detail') or 'no detail'})."
        )
        body_lines.append("### First actionable failure")
        body_lines.append(f"- {failure_reason}")
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
        "mode": mode,
        "all_green": ok,
        "doctor": doctor_report,
        "cleanup": cleanup_report,
        "commands": steps,
        "detected": detected,
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
    }
