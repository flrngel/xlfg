from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from xlfg.detect import detect_commands
from xlfg.doctor import ensure_dev_server
from xlfg.runs import create_run
from xlfg.scaffold import init_scaffold
from xlfg.verify import verify


class _OkHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):  # noqa: A003
        return


class TestXLFG(unittest.TestCase):
    def test_init_scaffold_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            result = init_scaffold(root)
            self.assertTrue((root / "docs" / "xlfg" / "index.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "failure-memory.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "harness-rules.md").exists())
            self.assertTrue((root / ".xlfg" / "runs").exists())
            gi = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".xlfg/", gi)
            result2 = init_scaffold(root)
            self.assertEqual(result2["created"], [])
            self.assertIn("docs/xlfg/knowledge/commands.json", result["created"])

    def test_create_run_seeds_diagnosis_and_solution_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            init_scaffold(root)
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
            init_scaffold(root)
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
            init_scaffold(root)
            run = create_run(root, request="example")
            res = verify(root, run_id=run["run_id"], mode="full")
            self.assertFalse(res["ok"])
            vmd = root / "docs" / "xlfg" / "runs" / run["run_id"] / "verification.md"
            fix = root / "docs" / "xlfg" / "runs" / run["run_id"] / "verify-fix-plan.md"
            self.assertTrue(vmd.exists())
            self.assertTrue(fix.exists())


if __name__ == "__main__":
    unittest.main()
