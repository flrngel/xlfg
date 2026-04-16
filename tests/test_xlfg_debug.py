from __future__ import annotations

import unittest
from pathlib import Path


class TestXLFGDebug(unittest.TestCase):
    def test_xlfg_debug_entrypoints_are_diagnosis_only_and_self_contained(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        command_path = repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-debug.md"
        standalone_path = repo_root / "standalone" / ".claude" / "skills" / "xlfg-debug" / "SKILL.md"
        plugin_phase_path = repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-debug-phase" / "SKILL.md"
        standalone_phase_path = repo_root / "standalone" / ".claude" / "skills" / "xlfg-debug-phase" / "SKILL.md"
        plugin_public_skill_path = repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-debug" / "SKILL.md"

        self.assertTrue(command_path.exists())
        self.assertTrue(standalone_path.exists())
        self.assertTrue(plugin_phase_path.exists())
        self.assertTrue(standalone_phase_path.exists())
        self.assertFalse(plugin_public_skill_path.exists())

        command_md = command_path.read_text(encoding="utf-8")
        standalone_md = standalone_path.read_text(encoding="utf-8")

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
        self.assertIn("deep root problem", command_md.lower())
        self.assertIn("deep root problem", standalone_md.lower())
        self.assertIn("do **not** change original source code", command_md)
        self.assertIn("do **not** change original source code", standalone_md)
        self.assertIn("gimmicks and shallow wins", command_md.lower())
        self.assertIn("gimmicks and shallow wins", standalone_md.lower())
        self.assertIn("phase-state.json", command_md)
        self.assertIn("phase-state.json", standalone_md)
        self.assertIn("phase-state tracking", command_md.lower())
        self.assertIn("phase-state tracking", standalone_md.lower())
        self.assertIn('"phases": ["recall","intent","context","debug"]', command_md)
        self.assertIn('"phases": ["recall","intent","context","debug"]', standalone_md)
        self.assertIn("loopback_count", command_md)
        self.assertIn("loopback_count", standalone_md)
        self.assertIn("Sync scaffold if missing or stale", command_md)
        self.assertIn("Sync scaffold if missing or stale", standalone_md)
        self.assertIn("write the lean core run directories", command_md)
        self.assertIn("write the lean core run directories", standalone_md)
        # v3.2.2 regression guard: repeat runs must not error on the first
        # phase-state Write because a stale file exists from a prior run.
        self.assertIn("rm -f .xlfg/phase-state.json", command_md)
        self.assertIn("rm -f .xlfg/phase-state.json", standalone_md)
        self.assertIn("xlfg-engineering:xlfg-debug-phase", command_md)
        self.assertIn("xlfg-debug-phase", standalone_md)
        self.assertIn("Stop:", standalone_md)
        self.assertIn("phase-gate.mjs", standalone_md)
        self.assertIn("\nname: xlfg-debug", command_md)
        self.assertNotIn("\nname:", standalone_md)

    def test_xlfg_debug_phase_requires_scientific_debugging_and_forbids_edits(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for path in [
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-debug-phase" / "SKILL.md",
            repo_root / "standalone" / ".claude" / "skills" / "xlfg-debug-phase" / "SKILL.md",
        ]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("user-invocable: false", text)
            self.assertIn("PRIMARY_ARTIFACT:", text)
            self.assertIn("DONE_CHECK:", text)
            self.assertIn("RETURN_CONTRACT:", text)
            self.assertIn("status: IN_PROGRESS", text)
            self.assertIn("Only the phase conductor may delegate.", text)
            self.assertIn("SendMessage", text)
            self.assertIn("smallest honest reproducer", text.lower())
            self.assertIn("expected correct behavior", text.lower())
            self.assertIn("compare failing vs passing", text.lower())
            self.assertIn("falsifiable hypotheses", text.lower())
            self.assertIn("first wrong state", text.lower())
            self.assertIn("git bisect", text.lower())
            self.assertIn('ask "why"', text.lower())
            self.assertIn("anti_monkey_probe", text)
            self.assertIn("debug-report.md", text)
            self.assertIn("Do not edit product source", text)
            self.assertIn("A green command without a stable explanation is not a diagnosis.", text)
            self.assertIn("Likely repair surface (no edits made)", text)

    def test_xlfg_debug_design_note_captures_external_inspirations(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        design_note = (repo_root / "docs" / "xlfg-debug-design-notes.md").read_text(encoding="utf-8")
        for needle in [
            "openclaw",
            "everything-claude-code",
            "awesome-claude-skills",
            "obsidian-skills",
            "symphony",
            "humanlayer",
            "OpenHarness",
            "serena",
            "graphify",
            "Understand-Anything",
            "cherry-studio",
            "AionUi",
            "CLIProxyAPI",
            "sub2api",
            "alphaclaw",
            "desloppify",
        ]:
            self.assertIn(needle, design_note)
        self.assertIn("smallest honest reproducer", design_note.lower())
        self.assertIn("falsifiable hypotheses", design_note.lower())
        self.assertIn("trace the first wrong state", design_note.lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
