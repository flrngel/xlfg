from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xlfg.detect import detect_commands
from xlfg.runs import create_run
from xlfg.scaffold import init_scaffold
from xlfg.verify import verify


class TestXLFG(unittest.TestCase):
    def test_init_scaffold_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            result = init_scaffold(root)
            self.assertTrue((root / "docs" / "xlfg" / "index.md").exists())
            self.assertTrue((root / ".xlfg" / "runs").exists())
            gi = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".xlfg/", gi)
            # idempotent
            result2 = init_scaffold(root)
            self.assertEqual(result2["created"], [])

    def test_detect_node_package_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            (root / "package.json").write_text(
                json.dumps({"scripts": {"test": "jest", "lint": "eslint .", "build": "tsc"}}),
                encoding="utf-8",
            )
            detected = detect_commands(root)
            self.assertIn("npm run test", detected["verify_full"])
            self.assertIn("npm run lint", detected["verify_fast"])

    def test_verify_writes_verification_md_when_no_cmds(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            init_scaffold(root)
            run = create_run(root, request="example")
            res = verify(root, run_id=run["run_id"], mode="full")
            self.assertFalse(res["ok"])
            vmd = root / "docs" / "xlfg" / "runs" / run["run_id"] / "verification.md"
            self.assertTrue(vmd.exists())


if __name__ == "__main__":
    unittest.main()
