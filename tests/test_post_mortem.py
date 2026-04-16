from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestPostMortem(unittest.TestCase):
    """Tests for plugins/xlfg-engineering/scripts/post-mortem.mjs (v4.2.0)."""

    def _script(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "plugins"
            / "xlfg-engineering"
            / "scripts"
            / "post-mortem.mjs"
        )

    def _run(self, *, cwd: str, args: list[str] | None = None) -> tuple[int, str, str]:
        cmd = ["node", str(self._script()), *(args or [])]
        proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
        return proc.returncode, proc.stdout, proc.stderr

    def _scaffold_run(self, root: Path, run_id: str, *, timings: list[dict] | None = None,
                      artifacts: dict[str, bytes] | None = None) -> Path:
        run_dir = root / "docs/xlfg/runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        if timings:
            with (run_dir / "phase-timings.jsonl").open("w", encoding="utf-8") as fh:
                for t in timings:
                    fh.write(json.dumps(t) + "\n")
        if artifacts:
            for name, content in artifacts.items():
                (run_dir / name).write_bytes(content)
        return run_dir

    def test_exits_3_when_no_runs_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = self._run(cwd=tmp)
            self.assertEqual(code, 3)
            self.assertIn("no runs found", err)

    def test_handles_run_without_timings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._scaffold_run(Path(tmp), "20260416-100000-noTimings",
                               artifacts={"spec.md": b"hello world"})
            code, out, err = self._run(cwd=tmp)
            self.assertEqual(code, 0, msg=err)
            self.assertIn("20260416-100000-noTimings", out)
            self.assertIn("n/a (no phase-timings.jsonl)", out)
            self.assertIn("no `phase-timings.jsonl` recorded", out)

    def test_computes_per_phase_wall_time_and_loopback_invocations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            timings = [
                {"run": "20260416-200000-t", "phase": "recall",  "event": "start", "ts": "2026-04-16T20:00:00Z"},
                {"run": "20260416-200000-t", "phase": "recall",  "event": "end",   "ts": "2026-04-16T20:00:30Z"},
                {"run": "20260416-200000-t", "phase": "verify",  "event": "start", "ts": "2026-04-16T20:01:00Z"},
                {"run": "20260416-200000-t", "phase": "verify",  "event": "end",   "ts": "2026-04-16T20:11:00Z"},
                # loopback: verify ran twice
                {"run": "20260416-200000-t", "phase": "verify",  "event": "start", "ts": "2026-04-16T20:11:30Z"},
                {"run": "20260416-200000-t", "phase": "verify",  "event": "end",   "ts": "2026-04-16T20:13:30Z"},
            ]
            self._scaffold_run(Path(tmp), "20260416-200000-t", timings=timings,
                               artifacts={"spec.md": b"x" * 100})
            code, out, err = self._run(cwd=tmp, args=["--json"])
            self.assertEqual(code, 0, msg=err)
            data = json.loads(out)
            phases = {p["phase"]: p for p in data["phases"]}
            self.assertIn("recall", phases)
            self.assertIn("verify", phases)
            self.assertEqual(phases["recall"]["invocations"], 1)
            self.assertEqual(phases["recall"]["wall"], "30s")
            self.assertEqual(phases["verify"]["invocations"], 2)
            # 10m + 2m = 12m total
            self.assertEqual(phases["verify"]["wall"], "12m")
            # total includes both phases
            self.assertEqual(data["total_seconds"], 30 + 600 + 120)

    def test_emits_loopback_suggestion_when_phase_runs_twice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            timings = [
                {"run": "20260416-210000-t", "phase": "verify", "event": "start", "ts": "2026-04-16T21:00:00Z"},
                {"run": "20260416-210000-t", "phase": "verify", "event": "end",   "ts": "2026-04-16T21:00:10Z"},
                {"run": "20260416-210000-t", "phase": "verify", "event": "start", "ts": "2026-04-16T21:00:20Z"},
                {"run": "20260416-210000-t", "phase": "verify", "event": "end",   "ts": "2026-04-16T21:00:30Z"},
            ]
            self._scaffold_run(Path(tmp), "20260416-210000-t", timings=timings)
            code, out, err = self._run(cwd=tmp, args=["--json"])
            self.assertEqual(code, 0, msg=err)
            data = json.loads(out)
            joined = " ".join(data["suggestions"])
            self.assertIn("ran 2 times", joined)

    def test_specific_run_arg_selects_that_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._scaffold_run(Path(tmp), "20260101-010101-old")
            self._scaffold_run(Path(tmp), "20260202-020202-new")
            code, out, err = self._run(cwd=tmp, args=["--run", "20260101-010101-old"])
            self.assertEqual(code, 0, msg=err)
            self.assertIn("20260101-010101-old", out)
            self.assertNotIn("20260202-020202-new", out)
