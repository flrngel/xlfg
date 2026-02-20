from __future__ import annotations

import datetime as _dt
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from .detect import detect_commands
from .runs import latest_run_id
from .util import ensure_dir


def _run_cmd(command: str, log_path: Path) -> int:
    ensure_dir(log_path.parent)
    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"$ {command}\n\n")
        p = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        assert p.stdout is not None
        for line in p.stdout:
            f.write(line)
        return p.wait()


def _tail(path: Path, max_lines: int = 80) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(lines[-max_lines:])
    except Exception:
        return ""


def verify(
    root: Path,
    run_id: Optional[str],
    mode: Literal["fast", "full"] = "full",
) -> Dict[str, Any]:
    """Run verification commands and write evidence.

    Returns a result dict with:
      - run_id
      - ok (bool)
      - log_dir
      - steps: list of {command, exit_code, log_file}
    """

    rid = run_id or latest_run_id(root)
    if not rid:
        raise RuntimeError("No run found. Run `xlfg init` and `xlfg start ...` first.")

    docs_run_dir = root / "docs" / "xlfg" / "runs" / rid
    dx_run_dir = root / ".xlfg" / "runs" / rid
    ensure_dir(docs_run_dir)
    ensure_dir(dx_run_dir)

    detected = detect_commands(root)
    cmds = detected["verify_fast"] if mode == "fast" else detected["verify_full"]
    cmds = list(cmds or [])

    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = dx_run_dir / "verify" / ts
    ensure_dir(log_dir)

    steps: List[Dict[str, Any]] = []
    ok = True

    for i, cmd in enumerate(cmds, start=1):
        name = f"{i:02d}"
        log_file = log_dir / f"{name}.log"
        code = _run_cmd(cmd, log_file)
        steps.append({"command": cmd, "exit_code": code, "log_file": str(log_file)})
        (log_dir / f"{name}.exitcode").write_text(str(code), encoding="utf-8")
        if code != 0:
            ok = False
            # stop at first failure to keep iterations tight
            break

    # Write verification.md (append with timestamped section)
    verification_md = docs_run_dir / "verification.md"
    header = f"## Verification run {ts} ({mode})\n\n"
    body_lines = []
    body_lines.append(f"Log dir: `{log_dir}`\n")
    for s in steps:
        body_lines.append(f"- `{s['command']}` → exit {s['exit_code']} (log: `{s['log_file']}`)")
    body_lines.append("")

    if not cmds:
        ok = False
        body_lines.append("No verification commands detected.")
        body_lines.append("Populate `docs/xlfg/knowledge/commands.json` with canonical commands.")
    elif not ok:
        last = steps[-1]
        body_lines.append("### First failing output (tail)")
        body_lines.append("```")
        body_lines.append(_tail(Path(last["log_file"])))
        body_lines.append("```")

    content = header + "\n".join(body_lines) + "\n\n"
    if verification_md.exists():
        with verification_md.open("a", encoding="utf-8") as f:
            f.write(content)
    else:
        verification_md.write_text("# Verification\n\n" + content, encoding="utf-8")

    return {"run_id": rid, "ok": ok, "log_dir": str(log_dir), "steps": steps, "detected": detected}
