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
from xlfg.recall import recall
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
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "current-state.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "env-doctor.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "solution-architect.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "test-implementer.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "task-checker.md").exists())
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
            self.assertTrue((root / "docs" / "xlfg" / "migrations" / f"2.0.0-to-{__version__}.md").exists())
            status = scaffold_status(root, __version__)
            self.assertFalse(status["needs_migration"])

    def test_status_reports_installed_and_repo_versions_separately(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            status = scaffold_status(root, __version__)
            self.assertEqual(status["installed_tool_version"], __version__)
            self.assertEqual(status["repo_scaffold_version"], __version__)
            self.assertEqual(status["version_source"], "meta.json:tool_version")

    def test_legacy_metadata_json_is_migrated_and_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            (root / "docs" / "xlfg" / "knowledge").mkdir(parents=True)
            legacy = root / "docs" / "xlfg" / "metadata.json"
            legacy.write_text(json.dumps({"version": "1.0.0"}), encoding="utf-8")
            status_before = scaffold_status(root, __version__)
            self.assertEqual(status_before["repo_scaffold_version"], "1.0.0")
            self.assertEqual(status_before["installed_tool_version"], __version__)
            self.assertEqual(status_before["version_source"], "metadata.json:version")
            self.assertTrue(status_before["needs_migration"])
            result = ensure_scaffold(root, __version__)
            self.assertEqual(result["previous_repo_scaffold_version"], "1.0.0")
            meta = json.loads((root / "docs" / "xlfg" / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["tool_version"], __version__)
            legacy_meta = json.loads(legacy.read_text(encoding="utf-8"))
            self.assertEqual(legacy_meta["tool_version"], __version__)
            self.assertTrue(legacy_meta["deprecated"])
            self.assertEqual(legacy_meta["canonical_path"], "docs/xlfg/meta.json")
            status_after = scaffold_status(root, __version__)
            self.assertEqual(status_after["repo_scaffold_version"], __version__)
            self.assertFalse(status_after["needs_migration"])

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


    def test_prepare_scaffold_creates_recall_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "ledger.jsonl").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "queries.md").exists())

    def test_create_run_seeds_memory_recall_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="fix login flow")
            run_dir = root / "docs" / "xlfg" / "runs" / run["run_id"]
            self.assertTrue((run_dir / "memory-recall.md").exists())

    def test_recall_searches_ledger_and_agent_memory_with_filters(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            ledger = root / "docs" / "xlfg" / "knowledge" / "ledger.jsonl"
            ledger.write_text(
                '\n'.join(
                    [
                        json.dumps(
                            {
                                "id": "mem-1",
                                "event": "memory.added",
                                "created_at": "2026-03-06T12:00:00",
                                "run_id": "20260306-120000-login",
                                "kind": "failure",
                                "stage": "verify",
                                "role": "env-doctor",
                                "title": "Port already in use from duplicate yarn dev",
                                "summary": "Reuse the healthy server instead of starting another yarn dev.",
                                "lex": "port already in use yarn dev healthcheck",
                                "evidence": ["verification.md", "doctor.log"],
                            }
                        )
                    ]
                )
                + '\n',
                encoding="utf-8",
            )
            agent_mem = root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "env-doctor.md"
            agent_mem.write_text(
                "# env-doctor memory\n\n- Reuse healthy dev servers before spawning another `yarn dev`.\n",
                encoding="utf-8",
            )
            result = recall(
                root,
                '\n'.join(
                    [
                        'lex: "port already in use" yarn dev',
                        'stage: verify',
                        'kind: failure agent-memory',
                        'role: env-doctor',
                        'scope: memory',
                    ]
                ),
                limit=5,
            )
            self.assertEqual(result["mode"], "search")
            self.assertGreaterEqual(len(result["results"]), 1)
            self.assertEqual(result["results"][0]["role"], "env-doctor")
            self.assertIn(result["results"][0]["scope"], {"ledger", "agent-memory"})

    def test_recall_temporal_lists_recent_runs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            create_run(root, request="fix login flow", run_id="20260306-120000-login")
            create_run(root, request="improve search flow", run_id="20260306-130000-search")
            result = recall(root, "2026-03-06", limit=10)
            self.assertEqual(result["mode"], "temporal")
            self.assertEqual(len(result["results"]), 2)
            self.assertEqual(result["results"][0]["run_id"], "20260306-130000-search")

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


    def test_plugin_macro_runs_recall_before_plan(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        xlfg_cmd = repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md"
        text = xlfg_cmd.read_text(encoding="utf-8")
        self.assertIn("/xlfg:recall $ARGUMENTS", text)
        self.assertLess(text.index("/xlfg:recall $ARGUMENTS"), text.index("/xlfg:plan $ARGUMENTS"))

    def test_bundle_context_exists_and_mentions_recall_first(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        handoff = repo_root / "NEXT_AGENT_CONTEXT.md"
        self.assertTrue(handoff.exists())
        text = handoff.read_text(encoding="utf-8")
        self.assertIn("/xlfg", text)
        self.assertIn("recall", text.lower())


if __name__ == "__main__":
    unittest.main()
