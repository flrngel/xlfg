#!/usr/bin/env python3
"""xlfg phase-gate — Stop hook that blocks the conductor from ending the
/xlfg pipeline before all phases complete.

Write discipline: this hook only ever mutates ``block_count``. The
read-modify-write cycle preserves every other field (``completed``,
``loopback_count``, ``in_progress_phase``, ``run_id``, ``phases``, ...) exactly
as read. Treat the hook as monotonic-for-block_count; it must never
reset lifecycle state written by the conductor.

Known limitation (not concurrency-safe): the read-modify-write is not
atomic. If the conductor writes the state file between the hook's
read and the hook's write, the hook's write clobbers the conductor's
update. The suppression branch narrows the window (hook exits
without writing while a phase is in progress), but the race is not
eliminated. A real fix would require file-locking or a separate
ledger for block_count — intentionally out of scope here.

Noise suppression: if the conductor has set ``in_progress_phase`` to a
non-empty string, the hook exits 0 without writing. That covers the
case where a long-running foreground phase (e.g. verify with live LLM
proof) legitimately parks the conversation awaiting a background task
or the next sub-packet. Without this guard, every parked turn would
fire the hook, increment block_count, and trip the safety valve.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PHASE_STATE_PATH = ".xlfg/phase-state.json"
ALL_PHASES = [
    "recall",
    "intent",
    "context",
    "plan",
    "implement",
    "verify",
    "review",
    "compound",
]
MAX_BLOCKS = 3


def _block(reason: str) -> None:
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))


def main() -> int:
    raw = sys.stdin.read()
    # Empty stdin means this invocation carries no Claude Code stop event.
    # Allow stopping instead of reading the cwd-relative phase-state file,
    # which would otherwise block legitimate non-xlfg invocations.
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    # Always allow stopping when model hits token limit — it cannot continue.
    stop_reason = str(payload.get("stop_reason") or "").strip()
    if stop_reason == "max_tokens":
        return 0

    cwd = str(payload.get("cwd") or os.getcwd())
    state_file = Path(cwd).resolve() / PHASE_STATE_PATH

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # No phase-state file means we are not inside an /xlfg run — allow stopping.
        return 0

    completed = state.get("completed") if isinstance(state.get("completed"), list) else []
    phases = state.get("phases") if isinstance(state.get("phases"), list) else ALL_PHASES

    # If all phases are done, allow stopping.
    if all(p in completed for p in phases):
        return 0

    # Noise suppression: while a phase is legitimately running, exit 0 without
    # writing — do not increment block_count, do not trip the safety valve.
    in_progress = state.get("in_progress_phase")
    in_progress_str = in_progress.strip() if isinstance(in_progress, str) else ""
    if in_progress_str:
        return 0

    # Safety valve: if we have already blocked too many times in a row, allow
    # stopping to prevent an infinite loop when the model cannot make progress.
    block_count = state.get("block_count") if isinstance(state.get("block_count"), (int, float)) else 0
    block_count = int(block_count)
    if block_count >= MAX_BLOCKS:
        return 0

    next_phase = next((p for p in phases if p not in completed), None)

    # Increment block_count and write back so the safety valve can trigger.
    try:
        state["block_count"] = block_count + 1
        state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    except OSError:
        # If we cannot write back, still block this time but the safety valve
        # will not advance — acceptable because the model will eventually hit
        # max_tokens or the user can intervene.
        pass

    _block(
        f"The /xlfg pipeline is not complete. {len(completed)}/{len(phases)} phases done. "
        f"Run the next phase: {next_phase}. "
        f"Use the Skill tool to invoke the {next_phase} phase skill with the current RUN_ID."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
