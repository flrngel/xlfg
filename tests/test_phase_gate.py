from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestPhaseGate(unittest.TestCase):
    """Tests for the xlfg-phase-gate.mjs Stop hook."""

    def _run_gate(self, payload: dict, phase_state: dict | None = None, cwd: str | None = None) -> tuple[int, str]:
        """Run the phase-gate hook with the given payload and optional phase-state file."""
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "plugins" / "xlfg-engineering" / "scripts" / "phase-gate.mjs"

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
                ["node", str(script)],
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
        script = repo_root / "plugins" / "xlfg-engineering" / "scripts" / "phase-gate.mjs"
        proc = subprocess.run(
            ["node", str(script)],
            input="",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "")

    def test_standalone_script_exists(self) -> None:
        """Standalone pack should have the same phase-gate hook."""
        repo_root = Path(__file__).resolve().parents[1]
        standalone = repo_root / "standalone" / ".claude" / "hooks" / "xlfg-phase-gate.mjs"
        self.assertTrue(standalone.exists())
        plugin = repo_root / "plugins" / "xlfg-engineering" / "scripts" / "phase-gate.mjs"
        self.assertEqual(
            standalone.read_text(encoding="utf-8"),
            plugin.read_text(encoding="utf-8"),
        )
