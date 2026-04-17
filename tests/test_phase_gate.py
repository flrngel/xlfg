from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestPhaseGate(unittest.TestCase):
    """Tests for the xlfg phase_gate.py Stop hook."""

    def _run_gate(self, payload: dict, phase_state: dict | None = None, cwd: str | None = None) -> tuple[int, str]:
        """Run the phase-gate hook with the given payload and optional phase-state file."""
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "plugins" / "xlfg-engineering" / "scripts" / "phase_gate.py"

        if cwd is None:
            td_ctx = tempfile.TemporaryDirectory()
            td = td_ctx.__enter__()
        else:
            td = cwd
            td_ctx = None

        try:
            root = Path(td)
            if phase_state is not None:
                state_dir = root / ".xlfg"
                state_dir.mkdir(parents=True, exist_ok=True)
                (state_dir / "phase-state.json").write_text(
                    json.dumps(phase_state, indent=2), encoding="utf-8"
                )

            payload.setdefault("cwd", str(root))
            proc = subprocess.run(
                ["python3", str(script)],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=False,
            )
            # Re-read the state file if it exists (hook may have updated block_count).
            updated_state = None
            state_path = root / ".xlfg" / "phase-state.json"
            if state_path.exists():
                updated_state = json.loads(state_path.read_text(encoding="utf-8"))
            return proc.returncode, proc.stdout.strip(), updated_state
        finally:
            if td_ctx is not None:
                td_ctx.__exit__(None, None, None)

    def test_blocks_when_phases_incomplete(self) -> None:
        """Hook should block when only some phases are completed."""
        state = {
            "run_id": "test-run",
            "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
            "completed": ["recall", "intent"],
            "loopback_count": 0,
            "max_loopbacks": 2,
            "block_count": 0,
        }
        code, out, updated = self._run_gate({"stop_reason": "end_turn"}, state)
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["decision"], "block")
        self.assertIn("context", data["reason"])
        self.assertIn("2/8", data["reason"])
        # block_count should be incremented
        self.assertEqual(updated["block_count"], 1)

    def test_allows_when_all_phases_complete(self) -> None:
        """Hook should allow stopping when all phases are done."""
        all_phases = ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"]
        state = {
            "run_id": "test-run",
            "phases": all_phases,
            "completed": list(all_phases),
            "loopback_count": 0,
            "max_loopbacks": 2,
            "block_count": 0,
        }
        code, out, _ = self._run_gate({"stop_reason": "end_turn"}, state)
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_allows_on_max_tokens(self) -> None:
        """Hook should always allow on max_tokens — model can't continue."""
        state = {
            "run_id": "test-run",
            "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
            "completed": ["recall"],
            "loopback_count": 0,
            "max_loopbacks": 2,
            "block_count": 0,
        }
        code, out, _ = self._run_gate({"stop_reason": "max_tokens"}, state)
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_allows_when_no_phase_state_file(self) -> None:
        """Hook should allow stopping when no phase-state file exists (not in xlfg run)."""
        code, out, _ = self._run_gate({"stop_reason": "end_turn"}, phase_state=None)
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_safety_valve_after_max_blocks(self) -> None:
        """Hook should allow stopping after 3 consecutive blocks (safety valve)."""
        state = {
            "run_id": "test-run",
            "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
            "completed": ["recall"],
            "loopback_count": 0,
            "max_loopbacks": 2,
            "block_count": 3,
        }
        code, out, _ = self._run_gate({"stop_reason": "end_turn"}, state)
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_block_count_increments_on_each_block(self) -> None:
        """Each block should increment block_count in the state file."""
        state = {
            "run_id": "test-run",
            "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
            "completed": [],
            "loopback_count": 0,
            "max_loopbacks": 2,
            "block_count": 1,
        }
        code, out, updated = self._run_gate({"stop_reason": "end_turn"}, state)
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["decision"], "block")
        self.assertEqual(updated["block_count"], 2)

    def test_allows_on_empty_stdin(self) -> None:
        """Hook should allow stopping on malformed/empty input."""
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "plugins" / "xlfg-engineering" / "scripts" / "phase_gate.py"
        proc = subprocess.run(
            ["python3", str(script)],
            input="",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "")

    def test_phase_gate_in_progress_suppression(self) -> None:
        """v4.3.0: when in_progress_phase is non-empty, the hook exits 0 without writing.

        Suppresses hook noise during legitimate long foreground phases (verify parked
        on bg LLM work, implement between sub-packets). The hook must NOT increment
        block_count while a phase is in progress — that would trip the safety valve
        spuriously.
        """
        state = {
            "run_id": "test-run",
            "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
            "completed": ["recall", "intent", "context", "plan", "implement"],
            "loopback_count": 0,
            "max_loopbacks": 2,
            "block_count": 0,
            "in_progress_phase": "verify",
        }
        code, out, updated = self._run_gate({"stop_reason": "end_turn"}, state)
        # Exit 0, no block emitted.
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        # block_count must NOT have been incremented.
        self.assertEqual(updated["block_count"], 0)
        # in_progress_phase must be preserved as-read.
        self.assertEqual(updated["in_progress_phase"], "verify")

        # With in_progress_phase cleared to empty string, hook resumes normal blocking.
        state2 = dict(state)
        state2["in_progress_phase"] = ""
        code2, out2, updated2 = self._run_gate({"stop_reason": "end_turn"}, state2)
        self.assertEqual(code2, 0)
        data = json.loads(out2)
        self.assertEqual(data["decision"], "block")
        self.assertEqual(updated2["block_count"], 1)

    def test_phase_gate_monotonic_for_block_count_only(self) -> None:
        """v4.3.0: the hook must never clobber `completed` or `loopback_count`.

        Regression guard for the memo's concurrent-writer finding. The hook
        reads, modifies ONLY `block_count`, and writes back — preserving every
        other field (including `loopback_count`, `completed`, `in_progress_phase`,
        `run_id`, `phases`, and any extra conductor-written keys) exactly as read.
        """
        state = {
            "run_id": "test-run",
            "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
            "completed": ["recall", "intent", "context"],
            "loopback_count": 2,  # nonzero — must survive
            "max_loopbacks": 2,
            "block_count": 0,
            "in_progress_phase": "",
            "extra_conductor_field": "preserve-me",  # sentinel
        }
        code, _, updated = self._run_gate({"stop_reason": "end_turn"}, state)
        self.assertEqual(code, 0)
        # block_count incremented, everything else preserved.
        self.assertEqual(updated["block_count"], 1)
        self.assertEqual(updated["loopback_count"], 2)
        self.assertEqual(updated["completed"], ["recall", "intent", "context"])
        self.assertEqual(updated["run_id"], "test-run")
        self.assertEqual(updated["extra_conductor_field"], "preserve-me")
