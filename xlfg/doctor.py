from __future__ import annotations

import datetime as _dt
import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .util import ensure_dir


class DoctorProcessHandle:
    def __init__(self, process: subprocess.Popen[str], started_new_session: bool) -> None:
        self.process = process
        self.started_new_session = started_new_session


def _http_health(url: str, timeout_sec: float = 2.0) -> Tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            status = getattr(resp, "status", 200)
            healthy = 200 <= status < 500
            return healthy, f"http {status}"
    except urllib.error.HTTPError as exc:
        return (exc.code < 500), f"http {exc.code}"
    except Exception as exc:
        return False, str(exc)


def _port_health(port: int, host: str = "127.0.0.1", timeout_sec: float = 1.0) -> Tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True, f"tcp {host}:{port} open"
    except Exception as exc:
        return False, str(exc)


def _is_healthy(dev_cfg: Dict[str, Any]) -> Tuple[bool, str]:
    healthcheck = dev_cfg.get("healthcheck")
    port = dev_cfg.get("port")
    if healthcheck:
        ok, detail = _http_health(str(healthcheck))
        if ok:
            return ok, detail
        if port:
            port_ok, port_detail = _port_health(int(port))
            return port_ok and ok, f"{detail}; {port_detail}"
        return ok, detail
    if port:
        return _port_health(int(port))
    return False, "no port or healthcheck configured"


def _doctor_md(report: Dict[str, Any]) -> str:
    lines = ["# Environment doctor", "", f"- Timestamp: {report.get('timestamp')}"]
    lines.append(f"- Status: {report.get('status')}")
    if report.get("command"):
        lines.append(f"- Command: `{report['command']}`")
    if report.get("cwd"):
        lines.append(f"- CWD: `{report['cwd']}`")
    if report.get("port") is not None:
        lines.append(f"- Port: {report['port']}")
    if report.get("healthcheck"):
        lines.append(f"- Healthcheck: `{report['healthcheck']}`")
    if report.get("health_detail"):
        lines.append(f"- Health detail: {report['health_detail']}")
    if report.get("log_file"):
        lines.append(f"- Log file: `{report['log_file']}`")
    if report.get("report_json"):
        lines.append(f"- JSON report: `{report['report_json']}`")
    if report.get("notes"):
        lines.append("")
        lines.append("## Notes")
        for note in report["notes"]:
            lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def ensure_dev_server(
    root: Path,
    run_id: str,
    dev_cfg: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Optional[DoctorProcessHandle]]:
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = root / ".xlfg" / "runs" / run_id / "doctor" / ts
    ensure_dir(log_dir)
    report_json = log_dir / "doctor-report.json"
    report_md = log_dir / "doctor-report.md"

    report: Dict[str, Any] = {
        "run_id": run_id,
        "timestamp": ts,
        "status": "no-config",
        "command": None,
        "cwd": None,
        "port": None,
        "healthcheck": None,
        "health_detail": None,
        "log_dir": str(log_dir),
        "log_file": None,
        "report_json": str(report_json),
        "report_md": str(report_md),
        "started_by_doctor": False,
        "notes": [],
    }

    if not dev_cfg:
        report["notes"].append("No dev server configuration found. Skipping environment doctor.")
        report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report_md.write_text(_doctor_md(report), encoding="utf-8")
        return report, None

    cfg = dict(dev_cfg)
    report.update(
        {
            "command": cfg.get("command"),
            "cwd": cfg.get("cwd") or ".",
            "port": cfg.get("port"),
            "healthcheck": cfg.get("healthcheck"),
        }
    )

    healthy, health_detail = _is_healthy(cfg)
    report["health_detail"] = health_detail
    if healthy and bool(cfg.get("reuse_if_healthy", True)):
        report["status"] = "reused"
        report["notes"].append("Existing healthy server detected; reusing it instead of starting another process.")
        report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report_md.write_text(_doctor_md(report), encoding="utf-8")
        return report, None

    port = cfg.get("port")
    if port is not None:
        port_ok, port_detail = _port_health(int(port))
        if port_ok and not healthy:
            report["status"] = "blocked-port-in-use"
            report["health_detail"] = f"{health_detail}; {port_detail}"
            report["notes"].append(
                "Port is already open but the configured healthcheck is not healthy. Refusing to start another dev server to avoid duplicate `yarn dev` / stale-server loops."
            )
            report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
            report_md.write_text(_doctor_md(report), encoding="utf-8")
            return report, None

    command = cfg.get("command")
    if not command:
        report["status"] = "no-command"
        report["notes"].append("No dev.command configured. Add it to docs/xlfg/knowledge/commands.json for smoke/e2e runs.")
        report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report_md.write_text(_doctor_md(report), encoding="utf-8")
        return report, None

    log_file = log_dir / "dev.log"
    report["log_file"] = str(log_file)
    cwd = root / str(cfg.get("cwd") or ".")
    ensure_dir(cwd)
    env = os.environ.copy()
    env.setdefault("BROWSER", "none")

    with log_file.open("w", encoding="utf-8") as f:
        f.write(f"$ {command}\n")
        f.write(f"# cwd: {cwd}\n\n")
        f.flush()
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=str(cwd),
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            start_new_session=True,
        )

    handle = DoctorProcessHandle(process=process, started_new_session=True)
    deadline = time.time() + int(cfg.get("startup_timeout_sec") or 120)
    while time.time() < deadline:
        healthy, health_detail = _is_healthy(cfg)
        report["health_detail"] = health_detail
        if healthy:
            report["status"] = "started"
            report["started_by_doctor"] = True
            report["pid"] = process.pid
            report["notes"].append("Started a fresh dev server for smoke/e2e verification.")
            report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
            report_md.write_text(_doctor_md(report), encoding="utf-8")
            return report, handle
        exit_code = process.poll()
        if exit_code is not None:
            report["status"] = "failed"
            report["exit_code"] = exit_code
            report["notes"].append("Dev server process exited before becoming healthy.")
            report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
            report_md.write_text(_doctor_md(report), encoding="utf-8")
            return report, handle
        time.sleep(1.0)

    report["status"] = "startup-timeout"
    report["started_by_doctor"] = True
    report["pid"] = process.pid
    report["notes"].append("Dev server did not become healthy before startup timeout.")
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_md.write_text(_doctor_md(report), encoding="utf-8")
    return report, handle


def cleanup_dev_server(handle: Optional[DoctorProcessHandle], timeout_sec: int = 5) -> Dict[str, Any]:
    if handle is None:
        return {"status": "not-started"}

    process = handle.process
    if process.poll() is not None:
        return {"status": "already-exited", "exit_code": process.returncode}

    try:
        if os.name == "posix" and handle.started_new_session:
            os.killpg(process.pid, 15)
        else:
            process.terminate()
        process.wait(timeout=timeout_sec)
        return {"status": "terminated", "exit_code": process.returncode}
    except Exception:
        try:
            if os.name == "posix" and handle.started_new_session:
                os.killpg(process.pid, 9)
            else:
                process.kill()
            process.wait(timeout=timeout_sec)
            return {"status": "killed", "exit_code": process.returncode}
        except Exception as exc:
            return {"status": "cleanup-failed", "error": str(exc)}
