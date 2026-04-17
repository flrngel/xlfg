from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestRenderWorkboard(unittest.TestCase):
    """Tests for plugins/xlfg-engineering/scripts/render_workboard.py."""

    def _script(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "plugins"
            / "xlfg-engineering"
            / "scripts"
            / "render_workboard.py"
        )

    def _run(self, *, cwd: str | None = None, args: list[str] | None = None) -> tuple[int, str, str]:
        cmd = ["python3", str(self._script())]
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

    def test_begin_marker_prefix_match(self) -> None:
        """v4.3.0: renderer must match a placeholder BEGIN marker (without the
        script-attribution suffix) and replace it in place — not append a second
        rendered block.

        Regression guard for the memo finding "duplicate ## Phase status on
        first render": a run-skeleton template that preseeds the BEGIN marker
        as `<!-- BEGIN: rendered-phase-status -->` (no attribution) was not
        matched by the old exact-match logic, so the renderer took the
        "no markers" prepend path and left two ## Phase status sections.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".xlfg").mkdir()
            state_path = root / ".xlfg" / "phase-state.json"
            state_path.write_text(json.dumps(self._state(["recall"])), encoding="utf-8")

            out_path = root / "docs" / "xlfg" / "runs" / "20260415-143307-test" / "workboard.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Preseed a PLACEHOLDER — BEGIN without script attribution.
            preseed = (
                "# Workboard\n"
                "\n"
                "<!-- BEGIN: rendered-phase-status -->\n"
                "## Phase status\n"
                "\n"
                "_placeholder — renderer should replace this block_\n"
                "\n"
                "<!-- END: rendered-phase-status -->\n"
                "\n"
                "## Task notes\n"
                "- keep me\n"
            )
            out_path.write_text(preseed, encoding="utf-8")

            code, _, err = self._run(cwd=str(root))
            self.assertEqual(code, 0, err)

            rendered = out_path.read_text(encoding="utf-8")

            # Exactly ONE BEGIN marker in final output — no duplicate block.
            begin_count = rendered.count("<!-- BEGIN: rendered-phase-status")
            self.assertEqual(
                begin_count,
                1,
                f"Expected 1 BEGIN marker after render, got {begin_count}. Output:\n{rendered}",
            )
            # Exactly ONE ## Phase status heading — the placeholder must have been replaced.
            phase_status_count = rendered.count("## Phase status")
            self.assertEqual(
                phase_status_count,
                1,
                f"Expected 1 '## Phase status' heading, got {phase_status_count}. Output:\n{rendered}",
            )
            # Placeholder text must be gone.
            self.assertNotIn("_placeholder — renderer should replace this block_", rendered)
            # Human-authored surrounding content must be preserved.
            self.assertIn("## Task notes\n- keep me", rendered)
            # The rendered block must contain the real phase table.
            self.assertIn("| recall | DONE |", rendered)
