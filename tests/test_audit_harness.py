from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


class TestAuditHarness(unittest.TestCase):
    """Tests for plugins/xlfg-engineering/scripts/audit-harness.mjs (v4.2.0)."""

    def _script(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "plugins"
            / "xlfg-engineering"
            / "scripts"
            / "audit-harness.mjs"
        )

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _run(self, *, args: list[str] | None = None, cwd: Path | None = None) -> tuple[int, str, str]:
        proc = subprocess.run(
            ["node", str(self._script()), *(args or [])],
            cwd=str(cwd or self._repo_root()),
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_passes_against_source_repo(self) -> None:
        # The source repo MUST always pass its own harness audit; otherwise
        # CI is meaningless. This is the canonical "the harness is shippable"
        # assertion.
        code, out, err = self._run()
        self.assertEqual(code, 0, msg=f"audit-harness failed:\n{out}\n---\n{err}")

    def test_json_output_shape(self) -> None:
        code, out, err = self._run(args=["--json"])
        self.assertEqual(code, 0, msg=err)
        data = json.loads(out)
        self.assertIn("plugin", data)
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 6)
        ids = [r["id"] for r in data["results"]]
        self.assertEqual(ids, [1, 2, 3, 4, 5, 6])
        for r in data["results"]:
            self.assertIn("name", r)
            self.assertIn("pass", r)
            self.assertIn("score", r)
            self.assertIn("note", r)

    def test_explicit_plugin_arg_works(self) -> None:
        plugin = self._repo_root() / "plugins" / "xlfg-engineering"
        code, _, err = self._run(args=["--plugin", str(plugin)])
        self.assertEqual(code, 0, msg=err)

    def test_does_not_false_positive_on_english_task_in_headings(self) -> None:
        # Regression: the previous regex-based stale-Task sweep flagged
        # "## Task decomposition hints" in solution-architect.md and
        # "## Task brief format" in task-divider.md. The fix scopes the
        # check to the frontmatter `tools:` field only.
        code, out, err = self._run(args=["--json"])
        self.assertEqual(code, 0, msg=err)
        data = json.loads(out)
        cc = next(r for r in data["results"] if r["id"] == 4)
        for failure in cc["detail"]["failures"]:
            self.assertNotIn("stale bare 'Task'", failure,
                             msg=f"false positive on stale-Task sweep: {failure}")
