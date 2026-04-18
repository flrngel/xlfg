"""Test suite for xlfg v6.2.

v6.2 shape: conductor + 9 phase skills. No sub-agents, no per-phase coordination
files, no Codex surface, no ledger. The durable archive (docs/xlfg/current-state.md,
runs/<RUN_ID>/run-summary.md, runs/<RUN_ID>/diagnosis.md) stays.

These tests guard the architecture against drift in either direction:
- Toward v5: re-adding sub-agents, dispatch headers, coordination files, Codex.
- Toward v6.0 monolith: collapsing skills back into command bodies.
"""
from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "xlfg-engineering"

EXPECTED_SKILLS = (
    "xlfg-recall-phase",
    "xlfg-intent-phase",
    "xlfg-context-phase",
    "xlfg-plan-phase",
    "xlfg-implement-phase",
    "xlfg-verify-phase",
    "xlfg-review-phase",
    "xlfg-compound-phase",
    "xlfg-debug-phase",
)

XLFG_PIPELINE = (
    "xlfg-recall-phase",
    "xlfg-intent-phase",
    "xlfg-context-phase",
    "xlfg-plan-phase",
    "xlfg-implement-phase",
    "xlfg-verify-phase",
    "xlfg-review-phase",
    "xlfg-compound-phase",
)

XLFG_DEBUG_PIPELINE = (
    "xlfg-recall-phase",
    "xlfg-intent-phase",
    "xlfg-context-phase",
    "xlfg-debug-phase",
)


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


# ---------------------------------------------------------------------------
# Plugin tree shape
# ---------------------------------------------------------------------------


class TestPluginShape(unittest.TestCase):
    """The v6.2 plugin tree has 2 commands, 9 skills, 1 audit script, plus meta."""

    def test_plugin_tree_is_bounded(self) -> None:
        files = sorted(
            str(p.relative_to(PLUGIN))
            for p in PLUGIN.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        )
        allowed_prefixes = (
            ".claude-plugin/",
            ".cursor-plugin/",
            "commands/",
            "hooks/",
            "scripts/",
            "skills/",
            "CHANGELOG.md",
            "CLAUDE.md",
            "README.md",
        )
        for f in files:
            self.assertTrue(
                f.startswith(allowed_prefixes),
                f"unexpected file in v6.2 plugin tree: {f}",
            )

    def test_no_agents_or_codex(self) -> None:
        """Sub-agents and the Codex surface are gone. Phase skills stay."""
        for banned in ("agents", "codex", ".codex-plugin"):
            self.assertFalse(
                (PLUGIN / banned).exists(),
                f"{banned}/ must not exist in v6 (sub-agent / Codex surface removed)",
            )

    def test_only_audit_harness_and_compat_shims_under_scripts(self) -> None:
        scripts = sorted(p.name for p in (PLUGIN / "scripts").iterdir() if p.is_file())
        self.assertEqual(
            scripts,
            ["audit_harness.py", "phase-gate.mjs", "subagent-stop-guard.mjs"],
        )

    def test_mjs_shims_are_no_ops(self) -> None:
        for name in ("phase-gate.mjs", "subagent-stop-guard.mjs"):
            path = PLUGIN / "scripts" / name
            self.assertTrue(path.exists(), f"missing compat shim: {name}")
            self.assertLess(
                path.stat().st_size,
                1024,
                f"{name} grew past the no-op shim budget; it must stay trivial",
            )


# ---------------------------------------------------------------------------
# Manifests
# ---------------------------------------------------------------------------


class TestManifests(unittest.TestCase):
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


# ---------------------------------------------------------------------------
# Commands (conductors)
# ---------------------------------------------------------------------------


class TestCommands(unittest.TestCase):
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

    def test_xlfg_dispatches_eight_phase_skills(self) -> None:
        """The /xlfg command must grant exactly the 8 SDLC phase skills and
        name each in the body in the expected order."""
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")
        for skill in XLFG_PIPELINE:
            self.assertIn(
                f"Skill(xlfg-engineering:{skill}",
                tools,
                f"xlfg command must grant Skill(xlfg-engineering:{skill} ...)",
            )
            self.assertIn(
                f"xlfg-engineering:{skill}",
                text,
                f"xlfg command body must reference {skill} in the pipeline",
            )
        # Pipeline order: each skill's body-position must be monotonic in the
        # expected order (no skipping, no reordering).
        positions = [text.find(f"xlfg-engineering:{s}") for s in XLFG_PIPELINE]
        self.assertEqual(
            positions,
            sorted(positions),
            "xlfg command pipeline order does not match recall→intent→context→plan→implement→verify→review→compound",
        )

    def test_xlfg_does_not_grant_debug_skill(self) -> None:
        """The debug phase is for /xlfg-debug only."""
        fm = _frontmatter((PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8"))
        tools = fm.get("allowed-tools", "")
        self.assertNotIn("xlfg-engineering:xlfg-debug-phase", tools)

    def test_xlfg_debug_dispatches_four_phase_skills(self) -> None:
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")
        for skill in XLFG_DEBUG_PIPELINE:
            self.assertIn(
                f"Skill(xlfg-engineering:{skill}",
                tools,
                f"xlfg-debug command must grant Skill(xlfg-engineering:{skill} ...)",
            )
            self.assertIn(
                f"xlfg-engineering:{skill}",
                text,
                f"xlfg-debug body must reference {skill} in the pipeline",
            )
        # No SDLC-only skills (plan/implement/verify/review/compound) allowed on debug.
        for skill in ("xlfg-plan-phase", "xlfg-implement-phase", "xlfg-verify-phase",
                      "xlfg-review-phase", "xlfg-compound-phase"):
            self.assertNotIn(skill, tools)

    def test_xlfg_debug_cannot_modify_existing_files(self) -> None:
        """Diagnosis-only: no Edit/MultiEdit; Write only for diagnosis.md."""
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")
        for banned in ("Edit", "MultiEdit"):
            self.assertNotIn(
                banned,
                tools,
                f"xlfg-debug must not grant {banned}: diagnosis-only contract",
            )
        self.assertIn("Write", tools, "xlfg-debug needs Write for diagnosis.md")
        self.assertIn(
            "docs/xlfg/runs/<RUN_ID>/diagnosis.md",
            text,
            "xlfg-debug body must name the sanctioned Write path",
        )

    def test_commands_do_not_reintroduce_dispatch_contract(self) -> None:
        """v6 is conductor+skills, not sub-agent dispatch."""
        forbidden = (
            "PRIMARY_ARTIFACT",
            "OWNERSHIP_BOUNDARY",
            "CONTEXT_DIGEST",
            "PRIOR_SIBLINGS",
            "RETURN_CONTRACT:",
            "DONE_CHECK:",
        )
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            for tok in forbidden:
                self.assertNotIn(tok, text, f"{cmd}: reintroduced dispatch token {tok!r}")

    def test_commands_do_not_spawn_nested_agents(self) -> None:
        """The conductor invokes skills, never sub-agents."""
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            fm = _frontmatter(text)
            tools = fm.get("allowed-tools", "")
            tool_names = [t.strip() for t in tools.split(",")]
            for banned in ("Agent", "SendMessage"):
                self.assertFalse(
                    any(re.match(rf"^{banned}\b", t) for t in tool_names),
                    f"{cmd}: {banned} granted — no nested delegation in v6",
                )

    def test_xlfg_body_disclaims_dotxlfg_directory(self) -> None:
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        self.assertIn("`.xlfg/` does not exist in v6", text)


# ---------------------------------------------------------------------------
# Phase skills
# ---------------------------------------------------------------------------


class TestSkills(unittest.TestCase):
    def test_all_expected_skills_exist(self) -> None:
        shipped = sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir())
        self.assertEqual(shipped, sorted(EXPECTED_SKILLS))

    def test_every_skill_has_skill_md(self) -> None:
        for name in EXPECTED_SKILLS:
            path = PLUGIN / "skills" / name / "SKILL.md"
            self.assertTrue(path.exists(), f"missing {path.relative_to(REPO)}")

    def test_every_skill_frontmatter_is_hidden_and_well_described(self) -> None:
        for name in EXPECTED_SKILLS:
            text = (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            fm = _frontmatter(text)
            self.assertEqual(
                fm.get("user-invocable"),
                "false",
                f"skills/{name}: must be user-invocable: false",
            )
            desc = fm.get("description", "")
            self.assertTrue(desc, f"skills/{name}: missing description")
            self.assertLessEqual(
                len(desc),
                220,
                f"skills/{name}: description {len(desc)} chars > 220 (context-budget discipline)",
            )
            # Skill file is a skill, not a command — no `name:` frontmatter.
            self.assertNotIn(
                "name",
                fm,
                f"skills/{name}: should not have `name:` frontmatter (skills are hidden)",
            )

    def test_no_skill_grants_nested_delegation(self) -> None:
        """No Agent or SendMessage in any skill's allowed-tools.

        v6 skills run in the conductor's own context. They do not spawn
        sub-agents. If this test fails, the sub-agent architecture is
        creeping back in.
        """
        for name in EXPECTED_SKILLS:
            text = (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            fm = _frontmatter(text)
            tools = fm.get("allowed-tools", "")
            tool_names = [t.strip() for t in tools.split(",")]
            for banned in ("Agent", "SendMessage"):
                self.assertFalse(
                    any(re.match(rf"^{banned}\b", t) for t in tool_names),
                    f"skills/{name}: {banned} must not appear in allowed-tools",
                )

    def test_no_skill_references_deleted_v5_dispatch(self) -> None:
        forbidden = (
            "PRIMARY_ARTIFACT",
            "OWNERSHIP_BOUNDARY",
            "CONTEXT_DIGEST",
            "PRIOR_SIBLINGS",
            "RETURN_CONTRACT:",
            "DONE_CHECK:",
            "SubagentStop",
        )
        for name in EXPECTED_SKILLS:
            text = (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            for tok in forbidden:
                self.assertNotIn(tok, text, f"skills/{name}: reintroduced v5 token {tok!r}")

    def test_debug_skill_grants_write_and_names_sanctioned_path(self) -> None:
        """The debug skill is the only skill that writes under docs/xlfg/runs/."""
        text = (PLUGIN / "skills" / "xlfg-debug-phase" / "SKILL.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        self.assertIn("Write", fm.get("allowed-tools", ""))
        self.assertNotIn("Edit", fm.get("allowed-tools", "").split(","))
        self.assertNotIn("MultiEdit", fm.get("allowed-tools", ""))
        self.assertIn("docs/xlfg/runs/<RUN_ID>/diagnosis.md", text)

    def test_compound_skill_writes_run_summary(self) -> None:
        text = (PLUGIN / "skills" / "xlfg-compound-phase" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("docs/xlfg/runs/<RUN_ID>/run-summary.md", text)
        self.assertIn("docs/xlfg/current-state.md", text)

    def test_recall_skill_reads_durable_archive(self) -> None:
        text = (PLUGIN / "skills" / "xlfg-recall-phase" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("docs/xlfg/current-state.md", text)
        self.assertIn("docs/xlfg/runs/", text)

    def test_skill_bodies_cover_their_load_bearing_philosophy(self) -> None:
        """Each skill must carry its own core concept(s).

        These substrings are what make a skill a *skill* rather than a pasted
        outline — drift detection against someone stripping bodies down to
        one-liners.
        """
        expectations = {
            "xlfg-recall-phase": ("librarian", "prior", "git log"),
            "xlfg-intent-phase": ("falsifiable", "three", "blocker"),
            "xlfg-context-phase": ("cartographer", "harness", "whole repo"),
            "xlfg-plan-phase": ("fast_check", "smoke_check", "ship_check", "readiness"),
            "xlfg-implement-phase": ("Edit", "failure-mode", "out-of-scope"),
            "xlfg-verify-phase": ("GREEN", "RED", "FAILED"),
            "xlfg-review-phase": ("Architecture", "Security", "Performance", "UX", "APPROVE"),
            "xlfg-compound-phase": ("run-summary.md", "current-state.md", "Durable lesson"),
            "xlfg-debug-phase": ("Reproduce", "hypothesis", "Mechanism", "fake fixes"),
        }
        for skill, needles in expectations.items():
            text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(
                    needle,
                    text,
                    f"skills/{skill}: missing load-bearing concept {needle!r}",
                )


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


class TestHooks(unittest.TestCase):
    def test_hooks_json_is_minimal(self) -> None:
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        names = sorted(hooks.get("hooks", {}).keys())
        self.assertEqual(names, ["PermissionRequest"])

    def test_no_stop_or_subagent_stop_hook(self) -> None:
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        names = set(hooks.get("hooks", {}).keys())
        self.assertNotIn("Stop", names)
        self.assertNotIn("SubagentStop", names)


# ---------------------------------------------------------------------------
# Audit harness
# ---------------------------------------------------------------------------


class TestAuditHarness(unittest.TestCase):
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
        self.assertEqual(ids, [1, 2, 3, 4, 5])
        for r in data["results"]:
            for key in ("name", "pass", "score", "note"):
                self.assertIn(key, r)


# ---------------------------------------------------------------------------
# Conductor-level discipline
# ---------------------------------------------------------------------------


class TestConductorDiscipline(unittest.TestCase):
    def test_xlfg_names_loopback_cap_and_rules(self) -> None:
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        self.assertIn("2", text)
        self.assertIn("loopback", text.lower())
        # The explicit rules for when loopbacks do and do not count.
        lower = text.lower()
        self.assertIn("verify red", lower)
        self.assertIn("review must-fix", lower)
        self.assertIn("approve-with-notes", lower)

    def test_xlfg_conductor_wires_durable_archive(self) -> None:
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        self.assertIn("docs/xlfg/current-state.md", text)
        self.assertIn("docs/xlfg/runs/<RUN_ID>/run-summary.md", text)
        self.assertIn("RUN_ID", text)

    def test_xlfg_debug_conductor_wires_diagnosis_archive(self) -> None:
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        self.assertIn("docs/xlfg/runs/<RUN_ID>/diagnosis.md", text)
        self.assertIn("RUN_ID", text)

    def test_conductors_prescribe_real_clock_for_run_id(self) -> None:
        """RUN_ID must come from the system clock via `date`, not model guesswork.

        Pre-v3.0.0 xlfg had a Python `datetime.now()` call for this. When the CLI
        was removed, the deterministic clock call went with it and v3–v6.2 all
        just told the model to "compute" the timestamp, which is model guesswork.
        The conductor MUST prescribe the shell call so RUN_ID reflects real time.
        """
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            self.assertIn(
                "date +%Y%m%d-%H%M%S",
                text,
                f"{cmd}: must prescribe `date +%Y%m%d-%H%M%S` for RUN_ID — "
                "the model cannot invent real timestamps reliably",
            )
            # And the body must name the source of truth explicitly — "do not invent".
            lower = text.lower()
            self.assertIn(
                "do not invent",
                lower,
                f"{cmd}: startup body must explicitly forbid inventing the timestamp",
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
