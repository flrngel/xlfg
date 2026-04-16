from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestRenderWorkboard(unittest.TestCase):
    """Tests for plugins/xlfg-engineering/scripts/render-workboard.mjs (v3.1.0)."""

    def _script(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "plugins"
            / "xlfg-engineering"
            / "scripts"
            / "render-workboard.mjs"
        )

    def _run(self, *, cwd: str | None = None, args: list[str] | None = None) -> tuple[int, str, str]:
        cmd = ["node", str(self._script())]
        if args:
            cmd.extend(args)
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def _state(self, completed: list[str]) -> dict:
        return {
            "run_id": "20260415-143307-test",
            "phases": ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"],
            "completed": completed,
            "loopback_count": 0,
            "max_loopbacks": 2,
            "block_count": 0,
        }

    def test_noop_when_no_phase_state(self) -> None:
        """Running outside an xlfg run (no phase-state.json) must exit 0 cleanly."""
        with tempfile.TemporaryDirectory() as td:
            code, out, err = self._run(cwd=td)
            self.assertEqual(code, 0, err)
            self.assertEqual(out.strip(), "")

    def test_dry_run_prints_block_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = root / "phase-state.json"
            state.write_text(json.dumps(self._state(["recall", "intent"])), encoding="utf-8")
            code, out, err = self._run(
                args=["--dry-run", "--state", str(state)],
            )
            self.assertEqual(code, 0, err)
            self.assertIn("BEGIN: rendered-phase-status", out)
            self.assertIn("| recall | DONE |", out)
            self.assertIn("| intent | DONE |", out)
            self.assertIn("| context | IN_PROGRESS |", out)
            self.assertIn("| plan | pending |", out)

    def test_writes_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".xlfg").mkdir()
            state_path = root / ".xlfg" / "phase-state.json"
            state_path.write_text(json.dumps(self._state(["recall"])), encoding="utf-8")
            out_path = root / "docs" / "xlfg" / "runs" / "20260415-143307-test" / "workboard.md"

            code, _, err = self._run(cwd=str(root))
            self.assertEqual(code, 0, err)
            first = out_path.read_text(encoding="utf-8")
            self.assertIn("| recall | DONE |", first)
            self.assertIn("| intent | IN_PROGRESS |", first)

            # Advance phase and re-render — only the block changes, surrounding
            # human-authored content must survive.
            preserved = first.replace(
                "<!-- END: rendered-phase-status -->",
                "<!-- END: rendered-phase-status -->\n\n## Task notes\n- preserve me\n",
            )
            out_path.write_text(preserved, encoding="utf-8")

            state_path.write_text(
                json.dumps(self._state(["recall", "intent", "context"])),
                encoding="utf-8",
            )
            code, _, err = self._run(cwd=str(root))
            self.assertEqual(code, 0, err)
            second = out_path.read_text(encoding="utf-8")
            self.assertIn("| context | DONE |", second)
            self.assertIn("| plan | IN_PROGRESS |", second)
            # Human-authored section must be preserved.
            self.assertIn("## Task notes\n- preserve me", second)

    def test_errors_on_missing_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state = Path(td) / "phase-state.json"
            bad = {"phases": ["recall"], "completed": []}
            state.write_text(json.dumps(bad), encoding="utf-8")
            code, _, err = self._run(
                args=["--dry-run", "--state", str(state)],
            )
            self.assertEqual(code, 2)
            self.assertIn("missing run_id", err)
