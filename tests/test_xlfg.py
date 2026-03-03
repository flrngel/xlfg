from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from xlfg import __version__
from xlfg.detect import detect_commands
from xlfg.doctor import ensure_dev_server
from xlfg.runs import create_run
from xlfg.scaffold import ensure_scaffold, scaffold_status
from xlfg.verify import verify


class _OkHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):  # noqa: A003
        return


class TestXLFG(unittest.TestCase):
    def test_prepare_scaffold_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            result = ensure_scaffold(root, __version__)
            self.assertTrue((root / "docs" / "xlfg" / "index.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "meta.json").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "env-doctor.md").exists())
            self.assertTrue((root / ".xlfg" / "runs").exists())
            gi = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".xlfg/", gi)
            self.assertIn("docs/xlfg/runs/*", gi)
            self.assertIn("!docs/xlfg/runs/.gitkeep", gi)
            self.assertIn("docs/xlfg/meta.json", result["updated"])
            result2 = ensure_scaffold(root, __version__)
            self.assertEqual(result2["created"], [])
            self.assertFalse(result2["needs_migration"])

    def test_prepare_detects_version_drift_and_writes_migration(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, "2.0.0")
            result = ensure_scaffold(root, __version__)
            self.assertEqual(result["previous_tool_version"], "2.0.0")
            self.assertTrue((root / "docs" / "xlfg" / "migrations" / "2.0.0-to-2.0.1.md").exists())
            status = scaffold_status(root, __version__)
            self.assertFalse(status["needs_migration"])

    def test_create_run_seeds_diagnosis_and_solution_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="fix login flow")
            run_dir = root / "docs" / "xlfg" / "runs" / run["run_id"]
            self.assertTrue((run_dir / "diagnosis.md").exists())
            self.assertTrue((run_dir / "solution-decision.md").exists())
            self.assertTrue((run_dir / "flow-spec.md").exists())
            self.assertTrue((run_dir / "tasks").exists())

    def test_detect_node_package_json_and_dev(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test": "jest",
                            "lint": "eslint .",
                            "build": "tsc",
                            "smoke": "playwright test smoke.spec.ts",
                            "e2e": "playwright test",
                            "dev": "vite --port 4100",
                        }
                    }
                ),
                encoding="utf-8",
            )
            detected = detect_commands(root)
            self.assertIn("npm run test", detected["verify_full"])
            self.assertIn("npm run lint", detected["verify_fast"])
            self.assertIn("npm run smoke", detected["smoke"])
            self.assertIn("npm run e2e", detected["e2e"])
            self.assertEqual(detected["dev"]["port"], 4100)

    def test_doctor_reuses_healthy_server(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="example")

            server = ThreadingHTTPServer(("127.0.0.1", 0), _OkHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                port = server.server_address[1]
                report, handle = ensure_dev_server(
                    root,
                    run["run_id"],
                    {
                        "command": "python -m http.server",
                        "cwd": ".",
                        "port": port,
                        "healthcheck": f"http://127.0.0.1:{port}/",
                        "startup_timeout_sec": 5,
                        "reuse_if_healthy": True,
                    },
                )
                self.assertEqual(report["status"], "reused")
                self.assertIsNone(handle)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_verify_writes_verification_md_when_no_cmds(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="example")
            res = verify(root, run_id=run["run_id"], mode="full")
            self.assertFalse(res["ok"])
            vmd = root / "docs" / "xlfg" / "runs" / run["run_id"] / "verification.md"
            fix = root / "docs" / "xlfg" / "runs" / run["run_id"] / "verify-fix-plan.md"
            self.assertTrue(vmd.exists())
            self.assertTrue(fix.exists())


if __name__ == "__main__":
    unittest.main()
