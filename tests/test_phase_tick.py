from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestPhaseTick(unittest.TestCase):
    """Tests for plugins/xlfg-engineering/scripts/phase-tick.mjs (v4.2.0)."""

    def _script(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "plugins"
            / "xlfg-engineering"
            / "scripts"
            / "phase-tick.mjs"
        )

    def _run(self, *, cwd: str, args: list[str]) -> tuple[int, str, str]:
        proc = subprocess.run(
            ["node", str(self._script()), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_appends_jsonl_line_with_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = self._run(
                cwd=tmp,
                args=["--run", "20260416-160000-x", "--phase", "recall", "--event", "start"],
            )
            self.assertEqual(code, 0, msg=err)
            log = Path(tmp) / "docs/xlfg/runs/20260416-160000-x/phase-timings.jsonl"
            self.assertTrue(log.exists())
            line = log.read_text(encoding="utf-8").strip()
            entry = json.loads(line)
            self.assertEqual(entry["run"], "20260416-160000-x")
            self.assertEqual(entry["phase"], "recall")
            self.assertEqual(entry["event"], "start")
            # ISO 8601 UTC, second-precision, Z-suffixed
            self.assertRegex(entry["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_appends_subsequent_events_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for event in ("start", "end"):
                code, _, err = self._run(
                    cwd=tmp,
                    args=["--run", "20260416-160000-x", "--phase", "recall", "--event", event],
                )
                self.assertEqual(code, 0, msg=err)
            log = Path(tmp) / "docs/xlfg/runs/20260416-160000-x/phase-timings.jsonl"
            lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["event"], "start")
            self.assertEqual(json.loads(lines[1])["event"], "end")

    def test_rejects_bad_event_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = self._run(
                cwd=tmp,
                args=["--run", "x", "--phase", "recall", "--event", "middle"],
            )
            self.assertEqual(code, 2)
            self.assertIn("event", err)

    def test_rejects_missing_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = self._run(cwd=tmp, args=["--run", "x", "--event", "start"])
            self.assertEqual(code, 2)
            self.assertIn("required", err)
