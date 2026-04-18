"""Test suite for xlfg v6.

v6.0.0 is a philosophy release: two command bodies, one audit script, one
hooks.json, two manifests. No sub-agents, no phase skills, no Codex surface,
no file-based state, no ledger. The tests that follow exist to catch drift
*back* toward that surface, not to reconstruct it.
"""
from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "xlfg-engineering"


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end < 0:
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


class TestPluginShape(unittest.TestCase):
    """The v6 plugin tree must be minimal and self-contained."""

    def test_plugin_tree_is_small(self) -> None:
        files = sorted(
            str(p.relative_to(PLUGIN))
            for p in PLUGIN.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        )
        # Allow no surprise directories. Any new file must be deliberate.
        allowed_prefixes = (
            ".claude-plugin/",
            ".cursor-plugin/",
            "commands/",
            "hooks/",
            "scripts/",
            "CHANGELOG.md",
            "CLAUDE.md",
            "README.md",
        )
        for f in files:
            self.assertTrue(
                f.startswith(allowed_prefixes),
                f"unexpected file in v6 plugin tree: {f}",
            )

    def test_no_agents_or_skills_or_codex(self) -> None:
        for banned in ("agents", "skills", "codex", ".codex-plugin"):
            self.assertFalse(
                (PLUGIN / banned).exists(),
                f"{banned}/ must not exist in v6 (subagent / phase-skill / codex surface removed)",
            )

    def test_scripts_are_single_audit_harness(self) -> None:
        scripts = sorted(p.name for p in (PLUGIN / "scripts").iterdir() if p.is_file())
        self.assertEqual(scripts, ["audit_harness.py"])

    def test_no_mjs_files_anywhere_in_plugin(self) -> None:
        mjs = list(PLUGIN.rglob("*.mjs"))
        self.assertEqual(mjs, [], f".mjs files leaked back in: {mjs}")


class TestManifests(unittest.TestCase):
    """Both manifests ship the same version string."""

    def test_version_sync(self) -> None:
        paths = [
            PLUGIN / ".claude-plugin" / "plugin.json",
            PLUGIN / ".cursor-plugin" / "plugin.json",
        ]
        versions = {p.parent.name: json.loads(p.read_text(encoding="utf-8"))["version"] for p in paths}
        self.assertEqual(len(set(versions.values())), 1, f"version drift: {versions}")
        (only,) = set(versions.values())
        self.assertRegex(only, r"^\d+\.\d+\.\d+$")

    def test_codex_manifest_does_not_exist(self) -> None:
        self.assertFalse((PLUGIN / ".codex-plugin").exists())
        self.assertFalse((REPO / ".agents").exists())


class TestCommands(unittest.TestCase):
    """Exactly two public commands: xlfg and xlfg-debug."""

    def test_exactly_two_commands(self) -> None:
        cmds = sorted(p.name for p in (PLUGIN / "commands").glob("*.md"))
        self.assertEqual(cmds, ["xlfg-debug.md", "xlfg.md"])

    def test_xlfg_frontmatter(self) -> None:
        fm = _frontmatter((PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8"))
        self.assertEqual(fm.get("name"), "xlfg")
        self.assertEqual(fm.get("effort"), "high")
        self.assertEqual(fm.get("disable-model-invocation"), "true")
        self.assertLessEqual(len(fm.get("description", "")), 220)
        self.assertIn("allowed-tools", fm)

    def test_xlfg_debug_frontmatter(self) -> None:
        fm = _frontmatter((PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8"))
        self.assertEqual(fm.get("name"), "xlfg-debug")
        self.assertEqual(fm.get("effort"), "high")
        self.assertEqual(fm.get("disable-model-invocation"), "true")
        self.assertLessEqual(len(fm.get("description", "")), 220)
        self.assertIn("allowed-tools", fm)

    def test_xlfg_debug_has_no_edit_tools(self) -> None:
        """Diagnosis-only means the debug command cannot ship source edits."""
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")
        for banned in ("Edit", "MultiEdit", "Write"):
            self.assertNotIn(
                banned, tools, f"xlfg-debug must not grant {banned}: diagnosis-only contract"
            )

    def test_both_commands_cover_their_phases(self) -> None:
        xlfg = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8").lower()
        debug = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8").lower()
        for phase in ("recall", "intent", "context", "plan", "implement", "verify", "review", "compound"):
            self.assertIn(phase, xlfg, f"/xlfg body missing {phase} phase")
        for phase in ("recall", "intent", "context", "debug"):
            self.assertIn(phase, debug, f"/xlfg-debug body missing {phase} phase")

    def test_commands_do_not_reintroduce_dispatch_contract(self) -> None:
        """v6 is inline philosophy, not dispatch headers."""
        forbidden = (
            "PRIMARY_ARTIFACT",
            "OWNERSHIP_BOUNDARY",
            "CONTEXT_DIGEST",
            "PRIOR_SIBLINGS",
            "RETURN_CONTRACT:",
            "DONE_CHECK:",
            "xlfg-engineering:xlfg-",
        )
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            for tok in forbidden:
                self.assertNotIn(tok, text, f"{cmd}: reintroduced dispatch token {tok!r}")

    def test_xlfg_is_not_a_dispatch_graph(self) -> None:
        """The v6 /xlfg body must not spawn sub-skills or specialist agents."""
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")
        self.assertNotIn("Skill(", tools)
        self.assertNotIn("Agent", tools.split(","))
        self.assertNotIn("SendMessage", tools)


class TestHooks(unittest.TestCase):
    """v6 hooks.json ships only the ExitPlanMode auto-allow."""

    def test_hooks_json_is_minimal(self) -> None:
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        names = sorted(hooks.get("hooks", {}).keys())
        self.assertEqual(names, ["PermissionRequest"])

    def test_no_stop_or_subagent_stop_hook(self) -> None:
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        names = set(hooks.get("hooks", {}).keys())
        self.assertNotIn("Stop", names)
        self.assertNotIn("SubagentStop", names)


class TestAuditHarness(unittest.TestCase):
    """The audit harness must pass against its own repo."""

    def _run(self, args: list[str] | None = None) -> tuple[int, str, str]:
        proc = subprocess.run(
            ["python3", str(PLUGIN / "scripts" / "audit_harness.py"), *(args or [])],
            cwd=str(REPO),
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_passes_against_own_repo(self) -> None:
        code, out, err = self._run()
        self.assertEqual(code, 0, msg=f"audit failed:\n{out}\n---\n{err}")

    def test_json_shape(self) -> None:
        code, out, _ = self._run(["--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn("plugin", data)
        self.assertIn("results", data)
        ids = [r["id"] for r in data["results"]]
        self.assertEqual(ids, [1, 2, 3, 4])
        for r in data["results"]:
            for key in ("name", "pass", "score", "note"):
                self.assertIn(key, r)


class TestPhilosophyStaysIntact(unittest.TestCase):
    """Load-bearing philosophy tokens must remain in the v6 command bodies.

    These assertions are the canary for anyone tempted to prune the guide down
    to a one-liner: the specific discipline names (proof before claim,
    completion barrier, scope discipline, no broken-window fixes, human-only
    blockers) are what separate /xlfg from "just do the task."
    """

    def test_xlfg_keeps_load_bearing_philosophy(self) -> None:
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8").lower()
        for needle in (
            "proof before claim",
            "completion barrier",
            "scope discipline",
            "human-only blocker",
            "repo truth first",
            "one autonomous run",
            "smallest honest",
            "residual risk",
            "falsifiable",
        ):
            self.assertIn(needle, text, f"/xlfg dropped load-bearing concept: {needle}")

    def test_xlfg_debug_keeps_diagnosis_philosophy(self) -> None:
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8").lower()
        for needle in (
            "no source edits",
            "root",
            "reproduction",
            "hypothesis",
            "mechanism",
            "fake fixes rejected",
            "residual unknowns",
        ):
            self.assertIn(needle, text, f"/xlfg-debug dropped load-bearing concept: {needle}")

    def test_xlfg_phase_loopback_cap(self) -> None:
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        self.assertIn("2", text)
        self.assertIn("loopback", text.lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
