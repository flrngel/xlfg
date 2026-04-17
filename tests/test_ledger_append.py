from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestLedgerAppend(unittest.TestCase):
    """Tests for plugins/xlfg-engineering/scripts/ledger_append.py."""

    def _script(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "plugins"
            / "xlfg-engineering"
            / "scripts"
            / "ledger_append.py"
        )

    def _run(self, *, stdin: str = "", args: list[str] | None = None) -> tuple[int, str, str]:
        cmd = ["python3", str(self._script())]
        if args:
            cmd.extend(args)
        proc = subprocess.run(
            cmd,
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_schema_doc_exists(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        schema = repo_root / "docs" / "xlfg" / "knowledge" / "ledger-schema.md"
        self.assertTrue(schema.exists(), "ledger-schema.md must exist as the canonical schema")
        text = schema.read_text(encoding="utf-8")
        for needle in ("ts", "run", "type", "version", "summary", "Tag allow-list"):
            self.assertIn(needle, text, f"schema missing section: {needle}")

    def test_dry_run_accepts_well_formed_event(self) -> None:
        event = {
            "ts": "2026-04-15T14:33:07Z",
            "run": "20260415-143307-example",
            "type": "feature",
            "version": "3.1.0",
            "summary": "shipped something",
        }
        code, out, _ = self._run(stdin=json.dumps(event), args=["--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.strip()), event)

    def test_rejects_bad_ts(self) -> None:
        event = {
            "ts": "2026-04-15",
            "run": "20260415-143307-example",
            "type": "feature",
            "version": "3.1.0",
            "summary": "x",
        }
        code, _, err = self._run(stdin=json.dumps(event), args=["--dry-run"])
        self.assertEqual(code, 1)
        self.assertIn("ts must be ISO 8601", err)

    def test_rejects_bad_type(self) -> None:
        event = {
            "ts": "2026-04-15T14:33:07Z",
            "run": "20260415-143307-example",
            "type": "typo",
            "version": "3.1.0",
            "summary": "x",
        }
        code, _, err = self._run(stdin=json.dumps(event), args=["--dry-run"])
        self.assertEqual(code, 1)
        self.assertIn("type must be one of", err)

    def test_rejects_bad_version(self) -> None:
        event = {
            "ts": "2026-04-15T14:33:07Z",
            "run": "20260415-143307-example",
            "type": "feature",
            "version": "not-a-version",
            "summary": "x",
        }
        code, _, err = self._run(stdin=json.dumps(event), args=["--dry-run"])
        self.assertEqual(code, 1)
        self.assertIn("version must be semver", err)

    def test_rejects_unknown_field(self) -> None:
        event = {
            "ts": "2026-04-15T14:33:07Z",
            "run": "20260415-143307-example",
            "type": "feature",
            "version": "3.1.0",
            "summary": "x",
            "some_garbage": "nope",
        }
        code, _, err = self._run(stdin=json.dumps(event), args=["--dry-run"])
        self.assertEqual(code, 1)
        self.assertIn("unknown field: some_garbage", err)

    def test_rejects_tag_outside_allowlist(self) -> None:
        event = {
            "ts": "2026-04-15T14:33:07Z",
            "run": "20260415-143307-example",
            "type": "feature",
            "version": "3.1.0",
            "summary": "x",
            "tags": ["not-a-real-tag"],
        }
        code, _, err = self._run(stdin=json.dumps(event), args=["--dry-run"])
        self.assertEqual(code, 1)
        self.assertIn("tag not in allow-list", err)

    def test_appends_to_custom_ledger_path(self) -> None:
        event = {
            "ts": "2026-04-15T14:33:07Z",
            "run": "20260415-143307-example",
            "type": "feature",
            "version": "3.1.0",
            "summary": "file write check",
        }
        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "subdir" / "ledger.jsonl"
            code, _, _ = self._run(
                stdin=json.dumps(event),
                args=["--ledger", str(out_path)],
            )
            self.assertEqual(code, 0)
            self.assertTrue(out_path.exists())
            # Exactly one line, decodable, round-trips.
            lines = out_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0]), event)
