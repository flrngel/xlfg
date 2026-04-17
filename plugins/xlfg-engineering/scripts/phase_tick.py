#!/usr/bin/env python3
"""xlfg phase-tick — record a single phase boundary event into the
run-local timings log so the post-mortem can compute per-phase wall
time honestly, including loopbacks.

Each invocation appends one JSONL line:
  {"run":"<RUN_ID>","phase":"<name>","event":"start|end","ts":"<ISO8601Z>"}

Output file: docs/xlfg/runs/<RUN_ID>/phase-timings.jsonl

The conductor brackets every phase Skill call with two ticks
(start before, end after). Loopbacks produce additional pairs for
the same phase — the post-mortem sums them.

Usage:
  phase_tick.py --run <RUN_ID> --phase <name> --event <start|end>

Exits 0 on success, 2 on bad args. Never fails the conductor — write
errors are logged to stderr but exit 0 so a missing disk does not
block /xlfg.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _parse_args(argv: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    i = 0
    while i < len(argv):
        k = argv[i]
        if k == "--run" and i + 1 < len(argv):
            out["run"] = argv[i + 1]
            i += 2
            continue
        if k == "--phase" and i + 1 < len(argv):
            out["phase"] = argv[i + 1]
            i += 2
            continue
        if k == "--event" and i + 1 < len(argv):
            out["event"] = argv[i + 1]
            i += 2
            continue
        raise ValueError(f"unexpected arg: {k}")
    return out


def _iso_now_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str]) -> int:
    try:
        args = _parse_args(argv)
    except ValueError as err:
        sys.stderr.write(f"phase-tick: {err}\n")
        return 2

    if not args.get("run") or not args.get("phase") or not args.get("event"):
        sys.stderr.write("phase-tick: --run, --phase, --event are all required\n")
        return 2

    if args["event"] not in ("start", "end"):
        sys.stderr.write(
            f"phase-tick: --event must be 'start' or 'end' (got '{args['event']}')\n"
        )
        return 2

    line = json.dumps(
        {
            "run": args["run"],
            "phase": args["phase"],
            "event": args["event"],
            "ts": _iso_now_z(),
        }
    ) + "\n"

    out_dir = Path.cwd() / "docs/xlfg/runs" / args["run"]
    out_path = out_dir / "phase-timings.jsonl"

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with out_path.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError as err:
        # Never block the conductor on a timings write failure.
        sys.stderr.write(f"phase-tick: write failed ({err}) — continuing\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
