from __future__ import annotations

import json
import re
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
from xlfg.intent_eval import grade_intent_artifacts, evaluate_intent_suite, parse_spec_artifact
from xlfg.scaffold import ensure_scaffold, scaffold_status
from xlfg.verify import verify


def _frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


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
            self.assertIn("## Intent contract", spec)
            self.assertIn("## Objective groups", spec)
            self.assertIn("resolution:", spec)
            self.assertIn("primary_artifact:", spec)
            self.assertIn("done_check:", spec)
            self.assertIn("intent: TODO", workboard)
            self.assertIn("Objective ledger", workboard)
            self.assertIn("do not mark a specialist lane done from chat alone", workboard)

    def test_repo_audit_reports_stop_guard_and_packet_headers(self) -> None:
        report = audit_repo(Path(__file__).resolve().parents[1])
        self.assertTrue(report["metrics"]["features"]["subagent_stop_guard"])
        self.assertTrue(report["metrics"]["features"]["conductor_stop_gate"])
        self.assertTrue(report["metrics"]["features"]["packet_header_discipline"])
        self.assertTrue(report["metrics"]["features"]["sequential_artifact_planning"])
        self.assertTrue(report["metrics"]["features"]["short_lived_specialists"])
        self.assertTrue(report["metrics"]["features"]["leaf_specialists"])

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
        self.assertTrue(report["metrics"]["features"]["single_main_entrypoint"])
        self.assertTrue(report["metrics"]["features"]["batch_phase_skills"])
        self.assertTrue(report["metrics"]["features"]["intent_ssot"])
        self.assertTrue(report["metrics"]["features"]["mandatory_intent_gate"])
        self.assertTrue(report["metrics"]["features"]["intent_eval_suite"])
        self.assertTrue(report["metrics"]["features"]["multi_objective_splitter"])
        self.assertTrue(report["metrics"]["features"]["just_in_time_phase_loading"])
        self.assertTrue(report["metrics"]["features"]["no_legacy_task_tool"])
        self.assertTrue(report["metrics"]["features"]["no_repo_relative_plugin_refs"])
        self.assertTrue(report["metrics"]["features"]["plugin_name_frontmatter_avoided"])
        self.assertGreaterEqual(report["metrics"]["models"]["counts"].get("haiku", 0), 1)
        self.assertEqual(report["metrics"]["runtime_legacy_query_contract_refs"]["count"], 0)

    def test_main_xlfg_entrypoints_are_self_contained_and_batch_phase_driven(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        command_path = repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md"
        standalone_path = repo_root / "standalone" / ".claude" / "skills" / "xlfg" / "SKILL.md"
        plugin_skill_path = repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg" / "SKILL.md"

        self.assertTrue(command_path.exists())
        self.assertTrue(standalone_path.exists())
        self.assertFalse(plugin_skill_path.exists())

        command_md = command_path.read_text(encoding="utf-8")
        standalone_md = standalone_path.read_text(encoding="utf-8")

        plugin_phase_names = [
            "xlfg-engineering:xlfg-recall-phase",
            "xlfg-engineering:xlfg-intent-phase",
            "xlfg-engineering:xlfg-context-phase",
            "xlfg-engineering:xlfg-plan-phase",
            "xlfg-engineering:xlfg-implement-phase",
            "xlfg-engineering:xlfg-verify-phase",
            "xlfg-engineering:xlfg-review-phase",
            "xlfg-engineering:xlfg-compound-phase",
        ]
        standalone_phase_names = [name.replace("xlfg-engineering:", "") for name in plugin_phase_names]

        self.assertIn("allowed-tools:", command_md)
        self.assertIn("allowed-tools:", standalone_md)
        self.assertIn("effort: high", command_md)
        self.assertIn("effort: high", standalone_md)
        self.assertIn("ExitPlanMode", command_md)
        self.assertIn("ExitPlanMode", standalone_md)
        self.assertIn("one autonomous run", command_md.lower())
        self.assertIn("one autonomous run", standalone_md.lower())
        self.assertIn("batch of hidden phase skills", command_md.lower())
        self.assertIn("batch of hidden phase skills", standalone_md.lower())
        self.assertIn("do not ask the user to run internal skills", command_md.lower())
        self.assertIn("do not ask the user to run internal skills", standalone_md.lower())
        self.assertIn("single source of truth", command_md.lower())
        self.assertIn("single source of truth", standalone_md.lower())
        self.assertIn("atomic packet", command_md.lower())
        self.assertIn("atomic packet", standalone_md.lower())
        self.assertIn("resume the **same specialist**", command_md.lower())
        self.assertIn("resume the **same specialist**", standalone_md.lower())
        self.assertIn("xlfg start", command_md)
        self.assertIn("xlfg start", standalone_md)
        self.assertNotIn("plugins/xlfg-engineering/skills/xlfg/SKILL.md", command_md)
        self.assertNotIn("plugins/xlfg-engineering/skills/xlfg/SKILL.md", standalone_md)
        self.assertIn("\nname: xlfg", command_md)
        self.assertNotIn("\nname:", standalone_md)

        for phase_name in plugin_phase_names:
            self.assertIn(phase_name, command_md)
        for phase_name in standalone_phase_names:
            self.assertIn(phase_name, standalone_md)

        self.assertIn("Skill(xlfg-engineering:xlfg-intent-phase *)", command_md)
        self.assertIn("Skill(xlfg-intent-phase *)", standalone_md)
        self.assertNotIn(" Task", command_md)
        self.assertNotIn(" Task", standalone_md)

        # Phase-state tracking and loopback cap (v2.8.0)
        self.assertIn("phase-state.json", command_md)
        self.assertIn("phase-state.json", standalone_md)
        self.assertIn("phase-state tracking", command_md.lower())
        self.assertIn("phase-state tracking", standalone_md.lower())
        # Stop hook: standalone has it in SKILL.md frontmatter; plugin has it in hooks.json only
        self.assertIn("Stop:", standalone_md)
        self.assertIn("phase-gate.mjs", standalone_md)
        self.assertIn("max 2 loopbacks", command_md.lower())
        self.assertIn("max 2 loopbacks", standalone_md.lower())
        self.assertIn("loopback_count", command_md)
        self.assertIn("loopback_count", standalone_md)


    def test_runtime_prompts_do_not_depend_on_query_contract_file(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_paths = [
            repo_root / "plugins" / "xlfg-engineering" / "commands",
            repo_root / "plugins" / "xlfg-engineering" / "skills",
            repo_root / "plugins" / "xlfg-engineering" / "agents",
            repo_root / "standalone" / ".claude" / "skills",
        ]
        for target in runtime_paths:
            for path in sorted(target.rglob("*.md")):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("query-contract.md", text, msg=str(path.relative_to(repo_root)))

    def test_intent_eval_scores_multi_objective_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root_dir = Path(td)
            fixture = {
                "id": "messy-bundle",
                "query": "fix the login redirect, keep SSO working, and improve the invalid-password error copy",
                "expected": {
                    "work_kind": "multi",
                    "direct_asks": ["fix the login redirect", "improve the invalid-password error copy"],
                    "implied_asks": ["keep SSO working"],
                    "acceptance_criteria": ["successful login lands on dashboard", "invalid password shows the new error copy"],
                    "objectives": [
                        "Fix login redirect after successful auth",
                        "Improve invalid-password error copy without breaking SSO",
                    ],
                    "blocking_ambiguities": [],
                    "forbidden_claims": ["replace the auth provider"],
                    "max_blocking_questions": 1,
                },
            }
            spec = root_dir / "spec.md"
            test_contract = root_dir / "test-contract.md"
            workboard = root_dir / "workboard.md"
            spec.write_text(
                """# Spec

## Intent contract
- resolution: `proceed-with-assumptions`
- work kind: `multi`
- raw request: fix the login redirect, keep SSO working, and improve the invalid-password error copy
- direct asks:
  - `Q1`: fix the login redirect
  - `Q2`: improve the invalid-password error copy
- implied asks:
  - `I1`: keep SSO working
- acceptance criteria:
  - `A1`: successful login lands on dashboard
  - `A2`: invalid password shows the new error copy
- non-goals:
  - replace auth provider
- constraints actually requested:
  - preserve current auth stack
- assumptions to proceed:
  - SSO callback path should remain unchanged
- blocking ambiguities:
  - none
- carry-forward anchor: preserve SSO while fixing redirect and error copy

## Objective groups
- `O1` — Fix login redirect after successful auth; covers: `Q1 I1 A1`; depends_on: `none`; completion: successful auth always lands on dashboard
- `O2` — Improve invalid-password error copy without breaking SSO; covers: `Q2 I1 A2`; depends_on: `O1`; completion: new copy appears and SSO still works

## Task map
- `T1` — patch auth redirect handler; objectives: `O1`; scenarios: `P0-1`; owner: `agent`
- `T2` — update invalid-password copy and tests; objectives: `O2`; scenarios: `P0-2`; owner: `agent`
""",
                encoding="utf-8",
            )
            test_contract.write_text(
                """# Test contract

## Required scenario contracts

### P0-1 — login redirect
- objective: `O1`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q1 I1 A1`
- practical_steps:
  1. log in with valid credentials
- fast_check: python -c "print('redirect ok')"
- ship_phase: `fast`
- ship_check: python -c "print('redirect ship ok')"
- regression_check: python -c "print('redirect guard ok')"
- manual_smoke: NONE
- anti_monkey_probe: patching only one callback still leaves SSO broken
- notes:

### P0-2 — invalid-password copy
- objective: `O2`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q2 I1 A2`
- practical_steps:
  1. log in with invalid password
- fast_check: python -c "print('copy ok')"
- ship_phase: `fast`
- ship_check: python -c "print('copy ship ok')"
- regression_check: python -c "print('copy guard ok')"
- manual_smoke: NONE
- anti_monkey_probe: copy updates but SSO path regresses
- notes:
""",
                encoding="utf-8",
            )
            workboard.write_text(
                """# Workboard

## Objective ledger
| Objective | Status | Covers asks | Depends on | Scenarios | Notes |
|---|---|---|---|---|---|
| O1 | DONE | Q1 I1 A1 | none | P0-1 |  |
| O2 | IN_PROGRESS | Q2 I1 A2 | O1 | P0-2 |  |

## Tasks
| Task | Status | Objectives | Query IDs | Scenario IDs | Owner | Checks | Notes |
|---|---|---|---|---|---|---|---|
| T1 | DONE | O1 | Q1 I1 A1 | P0-1 | agent |  |  |
| T2 | IN_PROGRESS | O2 | Q2 I1 A2 | P0-2 | agent |  |  |
""",
                encoding="utf-8",
            )
            report = grade_intent_artifacts(
                fixture=fixture,
                spec_path=spec,
                test_contract_path=test_contract,
                workboard_path=workboard,
            )
            self.assertGreaterEqual(report["metrics"]["direct_ask_recall"], 1.0)
            self.assertGreaterEqual(report["metrics"]["implied_ask_recall"], 1.0)
            self.assertGreaterEqual(report["metrics"]["objective_split_recall"], 1.0)
            self.assertGreaterEqual(report["metrics"]["objective_scenario_coverage"], 1.0)
            self.assertGreaterEqual(report["metrics"]["objective_task_coverage"], 1.0)
            self.assertEqual(report["metrics"]["false_assumption_rate"], 0.0)


    def test_bundled_intent_eval_suite_scores_fixture_artifacts(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        report = evaluate_intent_suite(
            suite_dir=repo_root / "evals" / "intent",
            artifacts_root=repo_root / "evals" / "intent" / "artifacts",
        )
        self.assertEqual(report["case_count"], 4)
        self.assertGreaterEqual(report["overall"], 0.95)



    def test_plugin_support_skills_are_hidden_background_helpers(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for skill_path in sorted((repo_root / "plugins" / "xlfg-engineering" / "skills").rglob("SKILL.md")):
            text = skill_path.read_text(encoding="utf-8")
            self.assertNotIn("\nname:", text)
            self.assertIn("user-invocable: false", text)


    def test_standalone_agent_pack_matches_plugin_agents(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        plugin_agents = sorted((repo_root / "plugins" / "xlfg-engineering" / "agents").rglob("*.md"))
        standalone_agents = sorted((repo_root / "standalone" / ".claude" / "agents").rglob("*.md"))
        self.assertGreater(len(plugin_agents), 0)
        self.assertEqual(len(plugin_agents), len(standalone_agents))

    def test_all_agents_have_proactive_descriptions_tools_and_foreground(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for agent_path in sorted((repo_root / "plugins" / "xlfg-engineering" / "agents").rglob("*.md")):
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("use proactively", text.lower())
            self.assertIn("tools:", text)
            self.assertIn("background: false", text)
            self.assertIn("## Specialist identity", text)
            self.assertIn("## Execution contract", text)

    def test_all_specialist_agents_are_leaf_workers_with_short_turn_budgets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for root in [
            repo_root / "plugins" / "xlfg-engineering" / "agents",
            repo_root / "standalone" / ".claude" / "agents",
        ]:
            for agent_path in sorted(root.rglob("*.md")):
                text = agent_path.read_text(encoding="utf-8")
                tools = _frontmatter_value(text, "tools") or ""
                max_turns = _frontmatter_value(text, "maxTurns")
                self.assertIsNotNone(max_turns, f"Missing maxTurns in {agent_path}")
                self.assertLessEqual(int(max_turns), 12, f"Turn budget too large in {agent_path}")
                self.assertNotIn("Agent", tools, f"Nested delegation tool leaked into {agent_path}")
                self.assertNotIn("SendMessage", tools, f"Resume tool leaked into {agent_path}")

    def test_review_agents_write_artifacts_under_reviews_dir(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        expected = {
            "xlfg-architecture-reviewer.md": "DOCS_RUN_DIR/reviews/architecture-review.md",
            "xlfg-security-reviewer.md": "DOCS_RUN_DIR/reviews/security-review.md",
            "xlfg-performance-reviewer.md": "DOCS_RUN_DIR/reviews/performance-review.md",
            "xlfg-ux-reviewer.md": "DOCS_RUN_DIR/reviews/ux-review.md",
        }
        review_root = repo_root / "plugins" / "xlfg-engineering" / "agents" / "review"
        for filename, artifact in expected.items():
            text = (review_root / filename).read_text(encoding="utf-8")
            self.assertIn(artifact, text)
            self.assertIn("Status: DONE | BLOCKED | FAILED", text)

    def test_audit_reports_subagent_hardening_features(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        report = audit_repo(repo_root)
        hardening = report["metrics"]["subagent_hardening"]
        features = report["metrics"]["features"]
        self.assertEqual(hardening["plugin_agent_count"], 27)
        self.assertTrue(hardening["standalone_agent_pack"])
        self.assertEqual(hardening["agents_with_tools_allowlist"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_background_false"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_short_turn_budgets"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_leaf_worker_tools"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_proactive_description"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_completion_barrier"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_resume_rule"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_artifact_bootstrap"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["agents_with_final_response_contract"], hardening["plugin_agent_count"])
        self.assertEqual(hardening["review_agents_with_report_artifacts"], hardening["review_agent_count"])
        self.assertTrue(features["explicit_subagent_tools"])
        self.assertTrue(features["foreground_specialists"])
        self.assertTrue(features["short_lived_specialists"])
        self.assertTrue(features["leaf_specialists"])
        self.assertTrue(features["proactive_delegation_descriptions"])
        self.assertTrue(features["review_artifact_lane"])
        self.assertTrue(features["completion_barrier_contracts"])
        self.assertTrue(features["resume_ready_specialists"])
        self.assertTrue(features["artifact_bootstrap_specialists"])
        self.assertTrue(features["final_response_contracts"])
        self.assertTrue(features["phase_sendmessage_resume"])
        self.assertTrue(features["review_packet_splitting"])
        self.assertTrue(features["atomic_task_packets"])
        self.assertTrue(features["task_divider_agent"])
        self.assertTrue(features["standalone_agent_pack"])

    def test_plan_phase_and_spec_support_atomic_task_packets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        plan_phase = (repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-plan-phase" / "SKILL.md").read_text(encoding="utf-8")
        implement_phase = (repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-implement-phase" / "SKILL.md").read_text(encoding="utf-8")
        spec_template = (repo_root / "xlfg" / "runs.py").read_text(encoding="utf-8")
        self.assertIn("xlfg-task-divider", plan_phase)
        self.assertIn("task-brief.md", plan_phase)
        self.assertIn("atomic task packet", implement_phase.lower())
        self.assertIn("primary_artifact", spec_template)
        self.assertIn("done_check", spec_template)

    def test_all_agents_have_completion_barrier_and_resume_rule(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for agent_path in sorted((repo_root / "plugins" / "xlfg-engineering" / "agents").rglob("*.md")):
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("## Completion barrier", text)
            self.assertIn("Do not return a progress update", text)
            self.assertIn("If the parent resumes you", text)
            self.assertIn("Status: IN_PROGRESS", text)
            self.assertIn("## Final response contract", text)
            self.assertIn("DONE <artifact-path>", text)

    def test_all_agents_have_turn_budget_rule(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for agent_path in sorted((repo_root / "plugins" / "xlfg-engineering" / "agents").rglob("*.md")):
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("## Turn budget rule", text, f"Missing turn budget rule in {agent_path.name}")
            self.assertIn("Write your artifact skeleton", text, f"Missing write-first instruction in {agent_path.name}")

    def test_all_delegating_entrypoints_repeat_atomic_packet_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        targets = [
            repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md",
            repo_root / "standalone" / ".claude" / "skills" / "xlfg" / "SKILL.md",
        ]
        targets.extend(sorted((repo_root / "plugins" / "xlfg-engineering" / "skills").glob("xlfg-*-phase/SKILL.md")))
        targets.extend(sorted((repo_root / "standalone" / ".claude" / "skills").glob("xlfg-*-phase/SKILL.md")))
        for path in targets:
            text = path.read_text(encoding="utf-8")
            is_main_entry = path.name == "xlfg.md" or path.parent.name == "xlfg"
            if not is_main_entry and "Agent" not in text and "SendMessage" not in text:
                continue
            self.assertIn("PRIMARY_ARTIFACT:", text, f"Missing PRIMARY_ARTIFACT in {path}")
            self.assertIn("DONE_CHECK:", text, f"Missing DONE_CHECK in {path}")
            self.assertIn("RETURN_CONTRACT:", text, f"Missing RETURN_CONTRACT in {path}")
            self.assertIn("Status: IN_PROGRESS", text, f"Missing artifact preseed rule in {path}")

    def test_delegating_phase_skills_forbid_nested_subagents(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        phase_names = [
            "xlfg-intent-phase",
            "xlfg-context-phase",
            "xlfg-plan-phase",
            "xlfg-implement-phase",
            "xlfg-verify-phase",
            "xlfg-review-phase",
        ]
        for base in [
            repo_root / "plugins" / "xlfg-engineering" / "skills",
            repo_root / "standalone" / ".claude" / "skills",
        ]:
            for phase_name in phase_names:
                text = (base / phase_name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("Only the phase conductor may delegate.", text)

    def test_review_phase_keeps_small_fanout(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for base in [
            repo_root / "plugins" / "xlfg-engineering" / "skills",
            repo_root / "standalone" / ".claude" / "skills",
        ]:
            text = (base / "xlfg-review-phase" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("standard: 1 lens", text)
            self.assertIn("up to 2 lenses", text)

    def test_review_agents_have_lean_context_sources(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for agent_path in sorted((repo_root / "plugins" / "xlfg-engineering" / "agents" / "review").glob("*.md")):
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("## Context sources", text, f"Missing context sources in {agent_path.name}")
            self.assertNotIn("Read first (if present):", text, f"Legacy Read first block still in {agent_path.name}")

    def test_review_phase_includes_context_digest(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        review_phase = (repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-review-phase" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("CONTEXT_DIGEST", review_phase)

    def test_phase_skills_can_resume_specialists_with_sendmessage(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        phase_names = [
            "xlfg-intent-phase",
            "xlfg-context-phase",
            "xlfg-plan-phase",
            "xlfg-implement-phase",
            "xlfg-verify-phase",
            "xlfg-review-phase",
        ]
        for phase_name in phase_names:
            text = (repo_root / "plugins" / "xlfg-engineering" / "skills" / phase_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("SendMessage", text)

    def test_review_phase_splits_broad_review_packets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        review_phase = (repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-review-phase" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("one change cluster plus one review lens", review_phase)
        self.assertIn("architecture-R1.md", review_phase)

    def test_intent_eval_parses_extended_task_packet_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / "spec.md"
            spec.write_text(
                """# Spec

## Intent contract
- resolution: `proceed`
- work kind: `build`
- raw request: ship login fix
- direct asks:
  - `Q1`: ship login fix
- implied asks:
  - `I1`: keep auth stable
- acceptance criteria:
  - `A1`: login succeeds
- non-goals:
  - none
- constraints actually requested:
  - preserve auth stack
- assumptions to proceed:
  - none
- blocking ambiguities:
  - none
- carry-forward anchor: keep auth stable while fixing login

## Objective groups
- `O1` — Fix login; covers: `Q1 I1 A1`; depends_on: `none`; completion: login succeeds

## Task map
- `T1` — Fix redirect logic; objectives: `O1`; scenarios: `P0-1`; owner: `xlfg-task-implementer`; scope: `app/login.ts tests/login.spec.ts`; primary_artifact: `tasks/T1/implementer-report.md`; done_check: `pytest tests/login -q`
""",
                encoding="utf-8",
            )
            parsed = parse_spec_artifact(spec)
            self.assertEqual(parsed["task_map"][0]["scope"], "app/login.ts tests/login.spec.ts")
            self.assertEqual(parsed["task_map"][0]["primary_artifact"], "tasks/T1/implementer-report.md")
            self.assertEqual(parsed["task_map"][0]["done_check"], "pytest tests/login -q")

    def test_ui_designer_agent_exists_in_both_packs_with_dual_mode(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        standalone = repo_root / "standalone" / ".claude" / "agents" / "planning" / "xlfg-ui-designer.md"
        plugin = repo_root / "plugins" / "xlfg-engineering" / "agents" / "planning" / "xlfg-ui-designer.md"
        self.assertTrue(standalone.exists(), f"missing {standalone}")
        self.assertTrue(plugin.exists(), f"missing {plugin}")
        self.assertEqual(
            standalone.read_text(encoding="utf-8"),
            plugin.read_text(encoding="utf-8"),
            "xlfg-ui-designer must stay byte-identical across packs",
        )
        text = standalone.read_text(encoding="utf-8")
        self.assertIn("DOCS_RUN_DIR/ui-design.md", text)
        self.assertIn("DOCS_RUN_DIR/ui-verification.md", text)
        self.assertIn("## Specialist identity", text)
        self.assertIn("## Execution contract", text)

    def test_ui_designer_is_wired_into_plan_phase_with_conditional_trigger(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for path in [
            repo_root / "standalone" / ".claude" / "skills" / "xlfg-plan-phase" / "SKILL.md",
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-plan-phase" / "SKILL.md",
        ]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("xlfg-ui-designer", text, f"plan-phase must reference xlfg-ui-designer: {path}")
            self.assertIn("UI-related", text, f"plan-phase must describe conditional trigger: {path}")
            self.assertIn("DOCS_RUN_DIR/ui-design.md", text, f"plan-phase must pass artifact path: {path}")

    def test_ui_designer_is_wired_into_verify_phase_with_conditional_trigger(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for path in [
            repo_root / "standalone" / ".claude" / "skills" / "xlfg-verify-phase" / "SKILL.md",
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-verify-phase" / "SKILL.md",
        ]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("xlfg-ui-designer", text, f"verify-phase must reference xlfg-ui-designer: {path}")
            self.assertIn("UI-related", text, f"verify-phase must describe conditional trigger: {path}")
            self.assertIn("DOCS_RUN_DIR/ui-verification.md", text, f"verify-phase must pass artifact path: {path}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
