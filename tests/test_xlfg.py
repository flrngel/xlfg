from __future__ import annotations

import json
import re
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path



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
    def test_versions_are_synced_across_plugin_manifests(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        claude_plugin = json.loads(
            (repo_root / "plugins" / "xlfg-engineering" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        cursor_plugin = json.loads(
            (repo_root / "plugins" / "xlfg-engineering" / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        codex_plugin = json.loads(
            (repo_root / "plugins" / "xlfg-engineering" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        claude_version = claude_plugin["version"]
        cursor_version = cursor_plugin["version"]
        codex_version = codex_plugin["version"]
        # All manifests must agree on the same version string
        self.assertEqual(claude_version, cursor_version)
        self.assertEqual(claude_version, codex_version)
        # Version must be a semver string (major.minor.patch)
        semver_pattern = re.compile(r'^\d+\.\d+\.\d+$')
        self.assertRegex(claude_version, semver_pattern, f"plugin.json version {claude_version!r} is not a semver string")

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
        self.assertIn("Sync scaffold if missing or stale", command_md)
        self.assertIn("Sync scaffold if missing or stale", standalone_md)
        self.assertIn("write the lean core run directories", command_md)
        self.assertIn("write the lean core run directories", standalone_md)
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
        # Reject the stale standalone `Task` tool name (replaced by `Agent` or
        # `Skill`). `TaskCreate` / `TaskUpdate` / `TaskList` (v3.1.0 task bridge)
        # are legitimate and MUST NOT be rejected here.
        for stale in (", Task,", ", Task\n", ", Task ", " Task(", " Task "):
            self.assertNotIn(stale, command_md, f"stale `Task` tool name in command: {stale!r}")
            self.assertNotIn(stale, standalone_md, f"stale `Task` tool name in standalone: {stale!r}")

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
            if "_shared" in agent_path.parts:
                continue
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
                if "_shared" in agent_path.parts:
                    continue
                text = agent_path.read_text(encoding="utf-8")
                tools = _frontmatter_value(text, "tools") or ""
                max_turns = _frontmatter_value(text, "maxTurns")
                self.assertIsNotNone(max_turns, f"Missing maxTurns in {agent_path}")
                self.assertLessEqual(int(max_turns), 150, f"Turn budget too large in {agent_path}")
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
            # v3.1.0+ canonical: status lives inside YAML frontmatter.
            self.assertIn("status: DONE | BLOCKED | FAILED", text)

    def test_plan_phase_and_spec_support_atomic_task_packets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        plan_phase = (repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-plan-phase" / "SKILL.md").read_text(encoding="utf-8")
        implement_phase = (repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-implement-phase" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("xlfg-task-divider", plan_phase)
        self.assertIn("task-brief.md", plan_phase)
        self.assertIn("atomic task packet", implement_phase.lower())
        self.assertIn("primary_artifact", plan_phase)
        self.assertIn("done_check", plan_phase)

    def test_all_agents_have_completion_barrier_and_resume_rule(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        agent_root = repo_root / "plugins" / "xlfg-engineering" / "agents"
        for agent_path in sorted(agent_root.rglob("*.md")):
            # _shared is a reference doc, not an agent.
            if "_shared" in agent_path.parts:
                continue
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("## Completion barrier", text)
            self.assertIn("Do not return a progress update", text)
            self.assertIn("If the parent resumes you", text)
            self.assertIn("status: IN_PROGRESS", text)
            self.assertIn("## Final response contract", text)
            self.assertIn("DONE <artifact-path>", text)

    def test_all_agents_have_turn_budget_rule(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        agent_root = repo_root / "plugins" / "xlfg-engineering" / "agents"
        for agent_path in sorted(agent_root.rglob("*.md")):
            if "_shared" in agent_path.parts:
                continue
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("## Turn budget rule", text, f"Missing turn budget rule in {agent_path.name}")
            self.assertIn(
                "Write the YAML frontmatter skeleton",
                text,
                f"Missing write-first instruction in {agent_path.name}",
            )

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
            self.assertIn("status: IN_PROGRESS", text, f"Missing artifact preseed rule in {path}")

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
