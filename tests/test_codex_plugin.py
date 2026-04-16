from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


def _frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
    if end is None:
        return None
    result: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.+)$", line.strip())
        if match:
            result[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return result


class TestCodexPlugin(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.plugin_root = self.repo_root / "plugins" / "xlfg-engineering"
        self.codex_root = self.plugin_root / "codex"

    def test_codex_manifest_exists_with_valid_relative_paths(self) -> None:
        manifest_path = self.plugin_root / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "xlfg-engineering")
        self.assertEqual(manifest["version"], "3.2.0")
        self.assertEqual(manifest["skills"], "./codex/skills/")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
        for key in ("skills", "mcpServers"):
            self.assertTrue(manifest[key].startswith("./"), key)
        self.assertIn("interface", manifest)
        self.assertEqual(manifest["interface"]["displayName"], "xlfg Engineering")

    def test_all_plugin_manifests_share_codex_release_version(self) -> None:
        manifest_paths = [
            self.plugin_root / ".claude-plugin" / "plugin.json",
            self.plugin_root / ".cursor-plugin" / "plugin.json",
            self.plugin_root / ".codex-plugin" / "plugin.json",
        ]
        versions = {
            path.parent.name: json.loads(path.read_text(encoding="utf-8"))["version"]
            for path in manifest_paths
        }
        self.assertEqual(set(versions.values()), {"3.2.0"})

    def test_repo_codex_marketplace_exposes_local_plugin(self) -> None:
        marketplace_path = self.repo_root / ".agents" / "plugins" / "marketplace.json"
        self.assertTrue(marketplace_path.exists())
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        plugins = marketplace["plugins"]
        self.assertEqual(len(plugins), 1)
        entry = plugins[0]
        self.assertEqual(entry["name"], "xlfg-engineering")
        self.assertEqual(entry["source"]["source"], "local")
        self.assertEqual(entry["source"]["path"], "./plugins/xlfg-engineering")
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(entry["category"], "Productivity")

    def test_exactly_two_public_codex_skills_are_exposed(self) -> None:
        skill_paths = sorted((self.codex_root / "skills").glob("*/SKILL.md"))
        skill_names = {path.parent.name for path in skill_paths}
        self.assertEqual(skill_names, {"xlfg", "xlfg-debug"})

    def test_codex_skills_have_required_frontmatter(self) -> None:
        for skill_path in sorted((self.codex_root / "skills").glob("*/SKILL.md")):
            text = skill_path.read_text(encoding="utf-8")
            frontmatter = _frontmatter(text)
            self.assertIsNotNone(frontmatter, str(skill_path))
            self.assertEqual(frontmatter.get("name"), skill_path.parent.name)
            self.assertTrue(frontmatter.get("description"), str(skill_path))

    def test_codex_text_preserves_core_xlfg_contracts(self) -> None:
        texts = []
        for path in sorted(self.codex_root.rglob("*.md")):
            texts.append(path.read_text(encoding="utf-8"))
        combined = "\n".join(texts)
        for needle in [
            "deterministic recall first",
            "intent before broad fan-out",
            "single `spec.md`",
            "`test-readiness.md = READY`",
            "scenario proof",
            "verification evidence",
            "explicit request to use bounded Codex subagents",
            "if subagents are unavailable",
            "active Codex session model and reasoning effort",
            "Do not translate Claude specialist `model` or `effort` frontmatter",
        ]:
            self.assertIn(needle, combined)

    def test_codex_surface_has_explicit_model_policy(self) -> None:
        model_policy = self.codex_root / "references" / "model-policy.md"
        self.assertTrue(model_policy.exists())
        text = model_policy.read_text(encoding="utf-8")
        self.assertIn("Do not load `plugins/xlfg-engineering/agents/**` as Codex agent configuration", text)
        self.assertIn("Use the active Codex session model and reasoning effort", text)
        self.assertIn("Do not translate Claude model labels into OpenAI model names", text)
        for role in ("`explorer`", "`worker`", "`default`"):
            self.assertIn(role, text)

    def test_codex_files_do_not_contain_claude_only_runtime_tokens(self) -> None:
        forbidden = [
            "allowed-tools",
            "Skill(",
            "TaskCreate",
            "TaskUpdate",
            "TaskList",
            "ExitPlanMode",
            "PermissionRequest",
            "CLAUDE_PLUGIN_ROOT",
            "user-invocable",
            "model:",
            "effort:",
            "sonnet",
            "haiku",
            "opus",
        ]
        for path in sorted(self.codex_root.rglob("*")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{token!r} leaked into {path}")

    def test_codex_v1_does_not_ship_project_hook_pack(self) -> None:
        self.assertFalse((self.repo_root / ".codex" / "hooks.json").exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
