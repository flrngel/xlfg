#!/usr/bin/env python3
"""xlfg render-workboard — regenerate the "## Phase status" section of
docs/xlfg/runs/<RUN_ID>/workboard.md from .xlfg/phase-state.json.

workboard.md is authored in layers: this renderer owns the
``## Phase status`` block only. Task tables, blockers, and the next-action
line remain authored by the phase skill that runs each phase. That split
means two writers of one file — but only one writer per section, which is
the point: phase-status stops being dual-written.

Usage:
  render_workboard.py                           # reads .xlfg/phase-state.json under cwd
  render_workboard.py --state <path> --out <workboard.md>
  render_workboard.py --dry-run                 # prints to stdout

Exits 0 when it rendered, 0 when no phase-state.json exists (no-op), and 2
on malformed state.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MARK_BEGIN = "<!-- BEGIN: rendered-phase-status (render-workboard.py) -->"
MARK_END = "<!-- END: rendered-phase-status -->"
# Match any BEGIN variant, including a placeholder left by a run-skeleton template.
MARK_BEGIN_PREFIX = "<!-- BEGIN: rendered-phase-status"

_HEADING_RE = re.compile(r"\A# [^\n]*\n")


def _parse_args(argv: list[str]) -> dict[str, object]:
    out: dict[str, object] = {"dryRun": False}
    i = 0
    while i < len(argv):
        k = argv[i]
        if k == "--dry-run":
            out["dryRun"] = True
            i += 1
            continue
        if k == "--state" and i + 1 < len(argv):
            out["state"] = argv[i + 1]
            i += 2
            continue
        if k == "--out" and i + 1 < len(argv):
            out["out"] = argv[i + 1]
            i += 2
            continue
        raise ValueError(f"unexpected arg: {k}")
    return out


def _render_block(state: dict[str, object]) -> str:
    phases = state.get("phases") if isinstance(state.get("phases"), list) else []
    completed = set(state.get("completed") or [])
    lines: list[str] = [MARK_BEGIN, "## Phase status", ""]
    lines.append(f"Run: `{state.get('run_id') or '(unknown)'}`")
    lc = state.get("loopback_count") if isinstance(state.get("loopback_count"), (int, float)) else 0
    mx = state.get("max_loopbacks") if isinstance(state.get("max_loopbacks"), (int, float)) else 2
    lines.append(f"Loopbacks: {int(lc)}/{int(mx)}")
    lines.append("")
    lines.append("| Phase | Status |")
    lines.append("|---|---|")
    active_seen = False
    for p in phases:
        if p in completed:
            status = "DONE"
        elif not active_seen:
            status = "IN_PROGRESS"
            active_seen = True
        else:
            status = "pending"
        lines.append(f"| {p} | {status} |")
    lines.append("")
    lines.append(MARK_END)
    return "\n".join(lines) + "\n"


def _splice_block(original: str, rendered: str) -> str:
    body = original or ""
    begin_idx = body.find(MARK_BEGIN_PREFIX)
    end_idx = body.find(MARK_END)
    if begin_idx != -1 and end_idx != -1 and end_idx > begin_idx:
        tail = body[end_idx + len(MARK_END):]
        tail = re.sub(r"\A\r?\n", "", tail)
        return body[:begin_idx] + rendered.rstrip() + "\n" + tail
    heading = _HEADING_RE.match(body)
    if heading:
        insert_at = heading.end()
        return body[:insert_at] + "\n" + rendered + body[insert_at:]
    return rendered + body


def main(argv: list[str]) -> int:
    try:
        args = _parse_args(argv)
    except ValueError as err:
        sys.stderr.write(f"render-workboard: {err}\n")
        return 2

    state_path = (
        Path(str(args["state"])).resolve()
        if args.get("state")
        else Path.cwd() / ".xlfg/phase-state.json"
    )

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return 0
    except (OSError, json.JSONDecodeError) as err:
        sys.stderr.write(f"render-workboard: cannot read state {state_path}: {err}\n")
        return 2

    if not state.get("run_id"):
        sys.stderr.write("render-workboard: state missing run_id\n")
        return 2

    rendered = _render_block(state)

    out_path = (
        Path(str(args["out"])).resolve()
        if args.get("out")
        else Path.cwd() / "docs/xlfg/runs" / str(state["run_id"]) / "workboard.md"
    )

    if args.get("dryRun"):
        sys.stdout.write(rendered)
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = out_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = "# Workboard\n\n"
    out_path.write_text(_splice_block(existing, rendered), encoding="utf-8")
    sys.stdout.write(f"{out_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
