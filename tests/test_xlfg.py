from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from xlfg import __version__
from xlfg.audit import audit_repo
from xlfg.detect import detect_commands
from xlfg.doctor import ensure_dev_server
from xlfg.runs import create_run
from xlfg.recall import recall
from xlfg.contracts import parse_test_readiness_verdict
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
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "query-refiner.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "why-analyst.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "harness-profiler.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "env-doctor.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "solution-architect.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "test-implementer.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "task-checker.md").exists())
            self.assertTrue((root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "test-readiness-checker.md").exists())
            self.assertTrue((root / ".xlfg" / "runs").exists())
            gi = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".xlfg/", gi)
            self.assertIn("docs/xlfg/runs/*", gi)
            self.assertIn("!docs/xlfg/runs/.gitkeep", gi)
            ga = (root / ".gitattributes").read_text(encoding="utf-8")
            self.assertIn("docs/xlfg/knowledge/patterns.md merge=union", ga)
            self.assertIn("docs/xlfg/knowledge/agent-memory/*.md merge=union", ga)
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

    def test_create_run_seeds_lean_core_files_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="fix login flow")
            run_dir = root / "docs" / "xlfg" / "runs" / run["run_id"]
            self.assertTrue((run_dir / "context.md").exists())
            self.assertTrue((run_dir / "memory-recall.md").exists())
            self.assertTrue((run_dir / "spec.md").exists())
            self.assertTrue((run_dir / "test-contract.md").exists())
            self.assertTrue((run_dir / "test-readiness.md").exists())
            self.assertTrue((run_dir / "workboard.md").exists())
            self.assertFalse((run_dir / "query-contract.md").exists())
            self.assertFalse((run_dir / "why.md").exists())
            self.assertFalse((run_dir / "harness-profile.md").exists())
            self.assertFalse((run_dir / "plan.md").exists())
            self.assertFalse((run_dir / "proof-map.md").exists())
            self.assertFalse((run_dir / "diagnosis.md").exists())
            self.assertFalse((run_dir / "solution-decision.md").exists())
            self.assertFalse((run_dir / "flow-spec.md").exists())
            self.assertFalse((run_dir / "env-plan.md").exists())
            self.assertFalse((run_dir / "scorecard.md").exists())
            self.assertTrue((run_dir / "tasks").exists())
            workboard = (run_dir / "workboard.md").read_text(encoding="utf-8")
            self.assertNotIn("prepare:", workboard)
            self.assertIn("Single source of truth", workboard)
            self.assertIn("do not ask the user to sequence phase commands", workboard)
            spec = (run_dir / "spec.md").read_text(encoding="utf-8")
            self.assertIn("single source of truth", spec.lower())

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

    def test_readiness_parser_ignores_template_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test-readiness.md"
            path.write_text(
                "# Test readiness\n\n## Verdict\n- `READY` | `REVISE`\n",
                encoding="utf-8",
            )
            self.assertIsNone(parse_test_readiness_verdict(path))


    def test_recall_searches_ledger_and_agent_memory_with_filters(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            ledger = root / "docs" / "xlfg" / "knowledge" / "ledger.jsonl"
            ledger.write_text(
                "\n".join(
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
                + "\n",
                encoding="utf-8",
            )
            agent_mem = root / "docs" / "xlfg" / "knowledge" / "agent-memory" / "env-doctor.md"
            agent_mem.write_text(
                "# env-doctor memory\n\n- Reuse healthy dev servers before spawning another `yarn dev`.\n",
                encoding="utf-8",
            )
            result = recall(
                root,
                "\n".join(
                    [
                        'lex: "port already in use" yarn dev',
                        "stage: verify",
                        "kind: failure agent-memory",
                        "role: env-doctor",
                        "scope: memory",
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

    def test_recall_can_find_branch_local_current_state_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="fix login flow")
            candidate = root / "docs" / "xlfg" / "runs" / run["run_id"] / "current-state-candidate.md"
            candidate.write_text(
                "# Current state candidate\n\n- Local branch rule: reuse the existing preview server before starting another one.\n",
                encoding="utf-8",
            )
            result = recall(root, 'preview server', limit=5)
            self.assertGreaterEqual(len(result["results"]), 1)
            self.assertTrue(any(r["path"].endswith("current-state-candidate.md") for r in result["results"]))

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

    def test_verify_passes_with_ready_scenario_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="fix login flow")
            run_dir = root / "docs" / "xlfg" / "runs" / run["run_id"]
            (run_dir / "test-readiness.md").write_text(
                "# Test readiness\n\n## Verdict\n- `READY`\n",
                encoding="utf-8",
            )
            (run_dir / "test-contract.md").write_text(
                """# Test contract\n\n## Required scenario contracts\n\n### P0-1 — login submit\n- objective: `O1`\n- requirement_kind: `F2P`\n- priority: `P0`\n- query_ids: `Q1 I1 A1`\n- practical_steps:\n  1. enter valid credentials\n  2. submit\n  3. land on dashboard\n- fast_check: python -c "print('fast proof')"\n- ship_phase: `fast`\n- ship_check: python -c "print('ship proof')"\n- regression_check: python -c "print('guard proof')"\n- manual_smoke: open app and confirm dashboard\n- anti_monkey_probe: invalid credentials still show an error\n- notes:\n\n### G1 — invalid credentials guard\n- objective: `O1`\n- requirement_kind: `P2P`\n- priority: `P1`\n- query_ids: `I1`\n- practical_steps:\n  1. submit invalid credentials\n- fast_check: python -c "print('guard fast')"\n- ship_phase: `fast`\n- ship_check: python -c "print('guard ship')"\n- regression_check: python -c "print('guard full')"\n- manual_smoke: try invalid login manually\n- anti_monkey_probe: button path works but enter path fails\n- notes:\n""",
                encoding="utf-8",
            )
            res = verify(root, run_id=run["run_id"], mode="full")
            self.assertTrue(res["ok"])
            self.assertEqual(res["test_readiness"], "READY")
            self.assertIn("P0-1", res["scenario_results"])
            self.assertTrue(res["scenario_results"]["P0-1"]["fast_ok"])
            self.assertTrue(res["scenario_results"]["P0-1"]["ship_ok"])

    def test_verify_fails_when_scenario_proof_is_not_practical(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            ensure_scaffold(root, __version__)
            run = create_run(root, request="fix checkout flow")
            run_dir = root / "docs" / "xlfg" / "runs" / run["run_id"]
            (run_dir / "test-readiness.md").write_text(
                "# Test readiness\n\n## Verdict\n- `READY`\n",
                encoding="utf-8",
            )
            (run_dir / "test-contract.md").write_text(
                """# Test contract\n\n## Required scenario contracts\n\n### P0-1 — checkout submit\n- objective: `O1`\n- requirement_kind: `F2P`\n- priority: `P0`\n- query_ids: `Q1 A1`\n- practical_steps:\n  1. add item\n  2. submit order\n- fast_check: NONE\n- ship_phase: `manual`\n- ship_check: NONE\n- regression_check: NONE\n- manual_smoke: click around until it seems okay\n- anti_monkey_probe: API succeeds but order UI never updates\n- notes:\n""",
                encoding="utf-8",
            )
            res = verify(root, run_id=run["run_id"], mode="full")
            self.assertFalse(res["ok"])
            joined = "\n".join(res["contract_issues"])
            self.assertIn("practical fast_check", joined)
            self.assertIn("manual ship proof", joined)

    def test_versions_are_synced_across_package_and_plugin_manifests(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        pyproject_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{__version__}"', pyproject_text)
        claude_plugin = json.loads((repo_root / "plugins" / "xlfg-engineering" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        cursor_plugin = json.loads((repo_root / "plugins" / "xlfg-engineering" / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(claude_plugin["version"], __version__)
        self.assertEqual(cursor_plugin["version"], __version__)

    def test_audit_reports_load_coverage_sync_and_compatibility(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        report = audit_repo(repo_root)
        self.assertTrue(report["version_sync"]["ok"])
        self.assertIn("workflow_load_score", report["scores"])
        self.assertIn("sdlc_coverage_score", report["scores"])
        self.assertIn("claude_code_compatibility_score", report["scores"])
        self.assertGreater(report["scores"]["efficiency_index"], 0)
        self.assertTrue(report["metrics"]["features"]["research_lane"])
        self.assertTrue(report["metrics"]["features"]["audit"])
        self.assertTrue(report["metrics"]["features"]["skill_native"])
        self.assertTrue(report["metrics"]["features"]["autonomous_macro"])
        self.assertTrue(report["metrics"]["features"]["consent_reduction"])
        self.assertTrue(report["metrics"]["features"]["standalone_short_name_pack"])
        self.assertGreaterEqual(report["metrics"]["models"]["counts"].get("haiku", 0), 1)

    def test_main_xlfg_entrypoints_are_autonomous_and_permission_reduced(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        skill_md = (repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg" / "SKILL.md").read_text(encoding="utf-8")
        command_md = (repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md").read_text(encoding="utf-8")
        self.assertIn("allowed-tools:", skill_md)
        self.assertIn("effort: high", skill_md)
        self.assertIn("ExitPlanMode", skill_md)
        self.assertIn("one autonomous run", skill_md.lower())
        self.assertIn("do **not** ask the user to run phase subcommands", command_md.lower())
        self.assertIn("single source of truth", command_md.lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
