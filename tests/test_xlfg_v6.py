"""Test suite for xlfg v6.5.

v6.5 shape: the /xlfg conductor dispatches 4 phase skills + 4 phase agents;
/xlfg-debug dispatches 2 skills + 2 agents. Exploration-heavy phases (recall,
context, verify, review) live as plugin-shipped agents under
`plugins/xlfg-engineering/agents/` so their tool-call logs stay in their own
sub-contexts and the conductor receives only each phase's distilled synthesis
via an explicit Return-format section. Decision-heavy phases (intent, plan,
implement, compound) stay as skills in the conductor's own context. The debug
phase stays as a skill.

This is a narrow carve-out to the v6.3.0 agents ban: the 4 whitelisted
phase-agents in SANCTIONED_AGENTS are the only agents that may exist. The
v6.3.0 durable lesson still holds for specialists — 27 specialist lens skills
remain *skills*, not agents, because they sit on shared context with their
parent and agent serialization would be wasteful. Agents are only warranted
where the phase generates its own context from scratch and the conductor
needs only the conclusion.

These tests guard the architecture against drift in either direction:
- Toward v5: agents beyond the whitelist, dispatch headers, coordination
  files, Codex surface, nested delegation.
- Toward v6.0 monolith: collapsing skills/agents back into command bodies.
- Toward v6.4 pre-agents: re-skill-ifying the 4 phases whose logs motivated
  the v6.5 split.
"""
from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "xlfg-engineering"

# Phase skills that stay in the conductor's context (decision-heavy, low
# log volume). The conductor loads these via Skill(xlfg-engineering:...).
EXPECTED_PHASE_SKILLS = (
    "xlfg-intent-phase",
    "xlfg-plan-phase",
    "xlfg-implement-phase",
    "xlfg-compound-phase",
    "xlfg-debug-phase",
)

# v6.3 restored the v5 specialists as hidden on-demand lens skills. v6.5
# keeps that decision: specialist expertise stays as skills, not agents.
# Phase skills AND agents load specialists via the Skill tool on-demand.
EXPECTED_SPECIALIST_SKILLS = (
    "xlfg-brainstorm",
    "xlfg-context-adjacent-investigator",
    "xlfg-context-constraints-investigator",
    "xlfg-context-unknowns-investigator",
    "xlfg-env-doctor",
    "xlfg-harness-profiler",
    "xlfg-query-refiner",
    "xlfg-repo-mapper",
    "xlfg-researcher",
    "xlfg-risk-assessor",
    "xlfg-root-cause-analyst",
    "xlfg-solution-architect",
    "xlfg-spec-author",
    "xlfg-task-divider",
    "xlfg-test-readiness-checker",
    "xlfg-test-strategist",
    "xlfg-ui-designer",
    "xlfg-why-analyst",
    "xlfg-task-implementer",
    "xlfg-test-implementer",
    "xlfg-task-checker",
    "xlfg-verify-runner",
    "xlfg-verify-reducer",
    "xlfg-architecture-reviewer",
    "xlfg-security-reviewer",
    "xlfg-performance-reviewer",
    "xlfg-ux-reviewer",
)

EXPECTED_SKILLS = EXPECTED_PHASE_SKILLS + EXPECTED_SPECIALIST_SKILLS

# v6.5 re-admits sub-agents for exploration-heavy phases only. Each agent
# carries its phase body plus an explicit "## Return format" section so the
# conductor receives a distilled synthesis, not the phase's tool-call log.
# Any new agent requires adding the name here with a justification naming
# the token-discipline win that motivates it. Specialists remain skills.
SANCTIONED_AGENTS = (
    "xlfg-recall",
    "xlfg-context",
    "xlfg-verify",
    "xlfg-review",
)

# The /xlfg pipeline in dispatch order. Each entry is (mechanism, name).
# "skill" → dispatched via Skill(xlfg-engineering:<name> ...).
# "agent" → dispatched via Agent(subagent_type: "<name>", ...).
XLFG_PIPELINE = (
    ("agent", "xlfg-recall"),
    ("skill", "xlfg-intent-phase"),
    ("agent", "xlfg-context"),
    ("skill", "xlfg-plan-phase"),
    ("skill", "xlfg-implement-phase"),
    ("agent", "xlfg-verify"),
    ("agent", "xlfg-review"),
    ("skill", "xlfg-compound-phase"),
)

XLFG_DEBUG_PIPELINE = (
    ("agent", "xlfg-recall"),
    ("skill", "xlfg-intent-phase"),
    ("agent", "xlfg-context"),
    ("skill", "xlfg-debug-phase"),
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


def _body(text: str) -> str:
    """Return body after frontmatter. Agent names can be substrings of
    specialist skill names (xlfg-verify ⊂ xlfg-verify-runner), so body-order
    assertions must skip the allowed-tools block in the frontmatter.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:])
    return text


# ---------------------------------------------------------------------------
# Plugin tree shape
# ---------------------------------------------------------------------------


class TestPluginShape(unittest.TestCase):
    """The v6.5 plugin tree has 3 commands, 5 phase skills + 27 specialist
    skills, 4 sanctioned agents, 1 audit script, plus meta."""

    def test_plugin_tree_is_bounded(self) -> None:
        files = sorted(
            str(p.relative_to(PLUGIN))
            for p in PLUGIN.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        )
        allowed_prefixes = (
            ".claude-plugin/",
            ".cursor-plugin/",
            "agents/",
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
                f"unexpected file in v6.5 plugin tree: {f}",
            )

    def test_no_unsanctioned_agents_or_codex(self) -> None:
        """v6.5 permits exactly 4 whitelisted phase-agents under `agents/`.

        The v6.3.0 durable lesson ("specialist expertise belongs in skills
        that load on-demand, not sub-agents") still holds for specialists.
        v6.5 carves out 4 phase-agents because their exploration logs have a
        clean signal/noise boundary that agent delegation preserves. Any
        agent beyond the whitelist is a regression. Codex stays banned.
        """
        agents_dir = PLUGIN / "agents"
        if agents_dir.exists():
            extras = sorted(
                p.name for p in agents_dir.iterdir()
                if p.is_file() and p.suffix == ".md" and p.stem not in SANCTIONED_AGENTS
            )
            self.assertFalse(
                extras,
                f"unsanctioned agent file(s): {extras} — "
                "expand SANCTIONED_AGENTS with justification if intentional",
            )
            # No subdirectories — v5 had agents/_shared/, agents/planning/, etc.
            for child in agents_dir.iterdir():
                self.assertFalse(
                    child.is_dir(),
                    f"agents/{child.name}/ subdirectory — v5-style layout regression",
                )
        for banned in ("codex", ".codex-plugin"):
            self.assertFalse(
                (PLUGIN / banned).exists(),
                f"{banned}/ must not exist (Codex surface removed in v6.0)",
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
    def test_exactly_three_commands(self) -> None:
        cmds = sorted(p.name for p in (PLUGIN / "commands").glob("*.md"))
        self.assertEqual(cmds, ["xlfg-debug.md", "xlfg-init.md", "xlfg.md"])

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

    def test_xlfg_init_frontmatter(self) -> None:
        fm = _frontmatter((PLUGIN / "commands" / "xlfg-init.md").read_text(encoding="utf-8"))
        self.assertEqual(fm.get("name"), "xlfg-init")
        self.assertEqual(fm.get("effort"), "high")
        self.assertEqual(fm.get("disable-model-invocation"), "true")
        self.assertLessEqual(len(fm.get("description", "")), 220)
        self.assertIn("allowed-tools", fm)

    def test_xlfg_init_is_project_scaffolding(self) -> None:
        """`/xlfg-init` is a small, idempotent project scaffold, not a conductor.

        It must (a) target the user's CWD rather than the xlfg plugin repo,
        (b) patch `.gitignore` with the canonical v6 runs block, (c) create
        `docs/xlfg/runs/.gitkeep` and `docs/xlfg/runs/README.md`, and
        (d) not dispatch any phase skills or attempt to author `current-state.md`.
        """
        text = (PLUGIN / "commands" / "xlfg-init.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")

        # Not a conductor: must not grant any Skill(xlfg-engineering:...) pipeline entries.
        self.assertNotIn(
            "Skill(xlfg-engineering:",
            tools,
            "xlfg-init must not grant phase or specialist Skill entries — it is not a conductor",
        )

        # Targets the user's project, not this plugin.
        self.assertIn("current working directory", text.lower())

        # Patches .gitignore with the canonical v6 runs block.
        self.assertIn(".gitignore", text)
        self.assertIn("docs/xlfg/runs/*", text)
        self.assertIn("!docs/xlfg/runs/.gitkeep", text)
        self.assertIn("!docs/xlfg/runs/README.md", text)

        # Creates the tracked pieces (.gitkeep + README.md).
        self.assertIn("docs/xlfg/runs/.gitkeep", text)
        self.assertIn("docs/xlfg/runs/README.md", text)

        # Does NOT author current-state.md — that is content, not scaffold.
        self.assertIn(
            "Does not create `docs/xlfg/current-state.md`",
            text,
            "xlfg-init must explicitly refuse to scaffold current-state.md",
        )

        # Must not reintroduce the v5 `.xlfg/` directory.
        self.assertNotIn(
            "mkdir -p .xlfg",
            text,
            "xlfg-init must not recreate the v5 `.xlfg/` directory",
        )

    def test_xlfg_dispatches_four_skills_and_four_agents(self) -> None:
        """The /xlfg command must grant the 4 skill-backed phases, must
        include `Agent` in its allowed-tools (for the 4 agent-backed phases),
        and must reference every pipeline step in canonical order in its body.
        """
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")

        # Skill grants for the 4 skill-backed phases must exist.
        for mechanism, name in XLFG_PIPELINE:
            if mechanism == "skill":
                self.assertIn(
                    f"Skill(xlfg-engineering:{name}",
                    tools,
                    f"xlfg command must grant Skill(xlfg-engineering:{name} ...)",
                )

        # Agent tool must be granted (for the 4 phase-agent dispatches).
        tool_names = [t.strip() for t in tools.split(",")]
        self.assertTrue(
            any(re.match(r"^Agent\b", t) for t in tool_names),
            "xlfg command must grant Agent in allowed-tools "
            "for the 4 phase-agent dispatches",
        )

        # Body must reference each pipeline step. Skills by namespaced name
        # (distinct), agents by backtick-delimited name (to avoid matching
        # substrings of specialist names like xlfg-verify-runner in grants).
        # First occurrence in the body (post-frontmatter) defines order.
        body = _body(text)
        positions: list[int] = []
        for mechanism, name in XLFG_PIPELINE:
            needle = f"xlfg-engineering:{name}" if mechanism == "skill" else f"`{name}`"
            pos = body.find(needle)
            self.assertNotEqual(
                pos, -1,
                f"xlfg command body must reference {needle} ({mechanism})",
            )
            positions.append(pos)
        self.assertEqual(
            positions,
            sorted(positions),
            "xlfg command pipeline order drift: expected "
            "recall→intent→context→plan→implement→verify→review→compound",
        )

    def test_xlfg_does_not_grant_debug_skill(self) -> None:
        """The debug phase is for /xlfg-debug only."""
        fm = _frontmatter((PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8"))
        tools = fm.get("allowed-tools", "")
        self.assertNotIn("xlfg-engineering:xlfg-debug-phase", tools)

    def test_conductor_does_not_grant_specialists_directly(self) -> None:
        """Conductors dispatch phase skills and phase agents; specialists
        load from those loaders' own grants, not from the conductor's.
        Granting specialists on the conductor is dead weight that regrew
        the frontmatter by ~30 lines pre-v6.5.1.
        """
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            fm = _frontmatter((PLUGIN / "commands" / cmd).read_text(encoding="utf-8"))
            tools = fm.get("allowed-tools", "")
            for specialist in EXPECTED_SPECIALIST_SKILLS:
                self.assertNotIn(
                    f"Skill(xlfg-engineering:{specialist}",
                    tools,
                    f"{cmd}: conductor must not grant specialist "
                    f"{specialist!r} — specialists load from phase skills/agents",
                )

    def test_xlfg_debug_dispatches_two_skills_and_two_agents(self) -> None:
        """The /xlfg-debug command dispatches 2 skills (intent, debug) and
        2 agents (recall, context) in canonical diagnosis order.
        """
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")

        for mechanism, name in XLFG_DEBUG_PIPELINE:
            if mechanism == "skill":
                self.assertIn(
                    f"Skill(xlfg-engineering:{name}",
                    tools,
                    f"xlfg-debug command must grant Skill(xlfg-engineering:{name} ...)",
                )

        tool_names = [t.strip() for t in tools.split(",")]
        self.assertTrue(
            any(re.match(r"^Agent\b", t) for t in tool_names),
            "xlfg-debug command must grant Agent for recall+context phase agents",
        )

        # No SDLC-only skills on debug — check full text since these are
        # distinct enough that substring collisions aren't a concern.
        for forbidden in (
            "xlfg-plan-phase",
            "xlfg-implement-phase",
            "xlfg-compound-phase",
        ):
            self.assertNotIn(
                forbidden,
                text,
                f"xlfg-debug must not reference {forbidden} — SDLC-only",
            )
        # For SDLC-only agents, use backtick-delimited needles so specialist
        # grants like xlfg-verify-runner in frontmatter don't cause false hits.
        for forbidden_agent in ("`xlfg-verify`", "`xlfg-review`"):
            self.assertNotIn(
                forbidden_agent,
                text,
                f"xlfg-debug must not dispatch {forbidden_agent} — SDLC-only agent",
            )

        # Body order: recall → intent → context → debug
        body = _body(text)
        positions: list[int] = []
        for mechanism, name in XLFG_DEBUG_PIPELINE:
            needle = f"xlfg-engineering:{name}" if mechanism == "skill" else f"`{name}`"
            pos = body.find(needle)
            self.assertNotEqual(
                pos, -1,
                f"xlfg-debug body must reference {needle} ({mechanism})",
            )
            positions.append(pos)
        self.assertEqual(
            positions,
            sorted(positions),
            "xlfg-debug pipeline order drift: expected recall→intent→context→debug",
        )

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
        """v6 is conductor+skills/agents, not v5 sub-agent dispatch packets."""
        forbidden = (
            "PRIMARY_ARTIFACT",
            "OWNERSHIP_BOUNDARY",
            "CONTEXT_DIGEST",
            "PRIOR_SIBLINGS",
            "RETURN_CONTRACT:",
            "DONE_CHECK:",
        )
        for cmd in ("xlfg.md", "xlfg-debug.md", "xlfg-init.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            for tok in forbidden:
                self.assertNotIn(tok, text, f"{cmd}: reintroduced dispatch token {tok!r}")

    def test_xlfg_init_does_not_grant_agent(self) -> None:
        """/xlfg-init is a scaffold, not a conductor. v6.5 permits Agent in
        the two conductors (/xlfg, /xlfg-debug) for the 4 sanctioned phase-
        agents; /xlfg-init must not dispatch anything.
        """
        text = (PLUGIN / "commands" / "xlfg-init.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        tools = fm.get("allowed-tools", "")
        tool_names = [t.strip() for t in tools.split(",")]
        for banned in ("Agent", "SendMessage"):
            self.assertFalse(
                any(re.match(rf"^{banned}\b", t) for t in tool_names),
                f"xlfg-init.md: {banned} granted — scaffold must not dispatch",
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

        v6.5 permits Agent in the conductors for the 4 sanctioned phase-
        agents, but skills stay in-context: they must not re-dispatch agents.
        One level of delegation only (conductor → phase-agent). If this test
        fails, the sub-agent architecture is creeping back into skills.
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

    def test_skill_bodies_cover_their_load_bearing_philosophy(self) -> None:
        """Each remaining phase skill must carry its own core concept(s).

        Phase agents (recall/context/verify/review) are guarded by the
        analogous test in TestAgents; this test covers the 5 phase skills
        that stay in-context.
        """
        expectations = {
            "xlfg-intent-phase": ("falsifiable", "three", "blocker"),
            "xlfg-plan-phase": ("fast_check", "smoke_check", "ship_check", "readiness"),
            "xlfg-implement-phase": ("Edit", "failure-mode", "out-of-scope"),
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

    def test_specialist_skills_carry_five_section_shape(self) -> None:
        """v6.3 specialist skills follow the same 5-section template as phase
        skills (Purpose, Lens, How to work it, Done signal, Stop-traps).
        """
        required_sections = ("## Purpose", "## Lens", "## How to work it", "## Done signal", "## Stop-traps")
        for name in EXPECTED_SPECIALIST_SKILLS:
            text = (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            for section in required_sections:
                self.assertIn(
                    section,
                    text,
                    f"skills/{name}: missing section {section!r}",
                )

    def test_phase_skills_advertise_specialists(self) -> None:
        """The 4 non-trivial phase skills must name which specialists are
        loadable from them. Compound is terminal and does not need specialists;
        context/verify/review moved to agents with their own advertise-section
        guards.
        """
        phase_to_specialists = {
            "xlfg-intent-phase": ("xlfg-why-analyst",),
            "xlfg-plan-phase": ("xlfg-solution-architect",),
            "xlfg-implement-phase": ("xlfg-task-implementer",),
            "xlfg-debug-phase": ("xlfg-root-cause-analyst",),
        }
        for phase, expected_mentions in phase_to_specialists.items():
            text = (PLUGIN / "skills" / phase / "SKILL.md").read_text(encoding="utf-8")
            for mention in expected_mentions:
                self.assertIn(
                    mention,
                    text,
                    f"skills/{phase}: must advertise specialist {mention!r}",
                )

    def test_phase_skills_body_and_allowed_tools_stay_in_sync(self) -> None:
        """Drift lint: the specialists named in a phase skill's "Optional
        specialist skills" body section must match the specialists granted in
        its `allowed-tools` frontmatter exactly. The analogous test for agents
        lives in TestAgents.
        """
        phases_with_specialists = (
            "xlfg-intent-phase",
            "xlfg-plan-phase",
            "xlfg-implement-phase",
            "xlfg-debug-phase",
        )
        specialist_name_re = re.compile(r"xlfg-engineering:(xlfg-[\w-]+)")
        for phase in phases_with_specialists:
            text = (PLUGIN / "skills" / phase / "SKILL.md").read_text(encoding="utf-8")
            fm = _frontmatter(text)
            tools = fm.get("allowed-tools", "")
            granted = {
                name for name in specialist_name_re.findall(tools)
                if name in EXPECTED_SPECIALIST_SKILLS
            }
            body_start = text.find("## Optional specialist skills")
            self.assertGreater(
                body_start, -1,
                f"skills/{phase}: missing '## Optional specialist skills' section",
            )
            next_section = text.find("\n## ", body_start + 1)
            body_section = text[body_start:next_section] if next_section != -1 else text[body_start:]
            advertised = {
                name for name in specialist_name_re.findall(body_section)
                if name in EXPECTED_SPECIALIST_SKILLS
            }
            self.assertEqual(
                granted, advertised,
                f"skills/{phase}: drift between allowed-tools Skill grants and "
                f"'Optional specialist skills' body.\n"
                f"  in allowed-tools only: {sorted(granted - advertised)}\n"
                f"  in body only: {sorted(advertised - granted)}",
            )

    def test_specialist_skill_bodies_stay_concise(self) -> None:
        """Specialist bodies follow the lean 5-section template — under 400
        words, excluding frontmatter. Ceiling is ~33% above the current max
        (~302 words) so no existing specialist needs a rewrite; bloat gets
        caught early.
        """
        word_ceiling = 400
        for name in EXPECTED_SPECIALIST_SKILLS:
            text = (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            lines = text.split("\n")
            if lines and lines[0].strip() == "---":
                end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), -1)
                body = "\n".join(lines[end + 1:]) if end > 0 else text
            else:
                body = text
            words = len(re.findall(r"\S+", body))
            self.assertLessEqual(
                words, word_ceiling,
                f"skills/{name}: body is {words} words, ceiling is {word_ceiling}. "
                "Tighten the 5 sections before adding more prose.",
            )


# ---------------------------------------------------------------------------
# Phase agents (v6.5 carve-out)
# ---------------------------------------------------------------------------


class TestAgents(unittest.TestCase):
    """v6.5 sanctioned-agent surface.

    The 4 whitelisted phase-agents live under `plugins/xlfg-engineering/
    agents/` and carry the phase body + explicit Return-format section. The
    conductor dispatches them via the Agent tool; they themselves may load
    specialist skills via the Skill tool but never re-dispatch agents.
    """

    def _agent_path(self, name: str) -> Path:
        return PLUGIN / "agents" / f"{name}.md"

    def test_sanctioned_agents_exist(self) -> None:
        agents_dir = PLUGIN / "agents"
        self.assertTrue(
            agents_dir.exists(),
            "plugins/xlfg-engineering/agents/ missing — v6.5 requires it",
        )
        shipped = sorted(
            p.stem for p in agents_dir.iterdir()
            if p.is_file() and p.suffix == ".md"
        )
        self.assertEqual(
            shipped, sorted(SANCTIONED_AGENTS),
            f"agent surface drift: shipped={shipped} expected={sorted(SANCTIONED_AGENTS)}",
        )

    def test_agent_frontmatter(self) -> None:
        for name in SANCTIONED_AGENTS:
            text = self._agent_path(name).read_text(encoding="utf-8")
            fm = _frontmatter(text)
            self.assertEqual(
                fm.get("name"), name,
                f"agents/{name}.md: frontmatter `name:` must equal file stem",
            )
            desc = fm.get("description", "")
            self.assertTrue(desc, f"agents/{name}.md: missing description")
            self.assertLessEqual(
                len(desc), 220,
                f"agents/{name}.md: description {len(desc)} chars > 220 "
                "(context-budget discipline)",
            )
            tools = fm.get("tools", "")
            self.assertTrue(
                tools, f"agents/{name}.md: missing `tools:` frontmatter",
            )

    def test_agents_do_not_grant_nested_agents(self) -> None:
        """One level of delegation only. Agents never re-dispatch agents."""
        for name in SANCTIONED_AGENTS:
            fm = _frontmatter(self._agent_path(name).read_text(encoding="utf-8"))
            tools = fm.get("tools", "")
            tool_names = [t.strip() for t in tools.split(",")]
            for banned in ("Agent", "SendMessage"):
                self.assertFalse(
                    any(re.match(rf"^{banned}\b", t) for t in tool_names),
                    f"agents/{name}.md: {banned} must not appear in tools "
                    "(one level of delegation only)",
                )

    def test_agents_do_not_reintroduce_dispatch_contract(self) -> None:
        """v6.5 agents carry plain prose Return-format templates, not v5
        dispatch packets. The forbidden-token sweep covers agent bodies too.
        """
        forbidden = (
            "PRIMARY_ARTIFACT",
            "OWNERSHIP_BOUNDARY",
            "CONTEXT_DIGEST",
            "PRIOR_SIBLINGS",
            "RETURN_CONTRACT:",
            "DONE_CHECK:",
            "SubagentStop",
        )
        for name in SANCTIONED_AGENTS:
            text = self._agent_path(name).read_text(encoding="utf-8")
            for tok in forbidden:
                self.assertNotIn(
                    tok, text,
                    f"agents/{name}.md: v5 dispatch token {tok!r} leaked",
                )

    def test_every_agent_carries_return_format(self) -> None:
        """Each phase-agent must carry an explicit `## Return format` section.

        The whole reason a phase is an agent is that the conductor receives a
        distilled synthesis instead of the phase's tool-call log. The Return
        format is the contract between agent and conductor — if it's missing,
        the conductor has no structured output to parse.
        """
        for name in SANCTIONED_AGENTS:
            text = self._agent_path(name).read_text(encoding="utf-8")
            self.assertIn(
                "## Return format", text,
                f"agents/{name}.md: missing `## Return format` section",
            )

    def test_agent_bodies_cover_their_load_bearing_philosophy(self) -> None:
        """Each agent carries its phase's core concept(s).

        Drift detection: if someone strips an agent body down to a one-liner,
        the phase philosophy is lost. Same shape as the phase-skills
        philosophy test in TestSkills.
        """
        expectations = {
            "xlfg-recall": ("librarian", "prior", "git log"),
            "xlfg-context": ("cartographer", "harness", "whole repo"),
            "xlfg-verify": ("GREEN", "RED", "FAILED"),
            "xlfg-review": ("Architecture", "Security", "Performance", "UX", "APPROVE"),
        }
        for agent, needles in expectations.items():
            text = self._agent_path(agent).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(
                    needle, text,
                    f"agents/{agent}.md: missing load-bearing concept {needle!r}",
                )

    def test_recall_agent_reads_durable_archive(self) -> None:
        """The recall agent prescribes reading the xlfg durable archive."""
        text = self._agent_path("xlfg-recall").read_text(encoding="utf-8")
        self.assertIn("docs/xlfg/current-state.md", text)
        self.assertIn("docs/xlfg/runs/", text)

    def test_agent_body_and_tools_stay_in_sync(self) -> None:
        """Drift lint: specialists advertised in an agent's "Optional specialist
        skills" body section must match the specialists granted in the agent's
        `tools:` frontmatter. Mirrors the same check for phase skills.

        recall is intentionally excluded — it has no specialists to advertise.
        """
        agents_with_specialists = ("xlfg-context", "xlfg-verify", "xlfg-review")
        specialist_name_re = re.compile(r"xlfg-engineering:(xlfg-[\w-]+)")
        for agent in agents_with_specialists:
            text = self._agent_path(agent).read_text(encoding="utf-8")
            fm = _frontmatter(text)
            tools = fm.get("tools", "")
            granted = {
                name for name in specialist_name_re.findall(tools)
                if name in EXPECTED_SPECIALIST_SKILLS
            }
            body_start = text.find("## Optional specialist skills")
            self.assertGreater(
                body_start, -1,
                f"agents/{agent}.md: missing '## Optional specialist skills' section",
            )
            next_section = text.find("\n## ", body_start + 1)
            body_section = text[body_start:next_section] if next_section != -1 else text[body_start:]
            advertised = {
                name for name in specialist_name_re.findall(body_section)
                if name in EXPECTED_SPECIALIST_SKILLS
            }
            self.assertEqual(
                granted, advertised,
                f"agents/{agent}.md: drift between tools and body.\n"
                f"  in tools only: {sorted(granted - advertised)}\n"
                f"  in body only: {sorted(advertised - granted)}",
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
        self.assertEqual(ids, [1, 2, 3, 4, 5, 6])
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

    def test_xlfg_conductor_prescribes_end_of_run_commit(self) -> None:
        """`/xlfg` runs must commit tracked product changes at end-of-run.

        The commit step is a mandatory section in the conductor body, between
        compound returning and the user-facing summary. Introduced in v6.3.2
        and unchanged in v6.5.
        """
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        lower = text.lower()

        self.assertIn(
            "end-of-run commit",
            lower,
            "xlfg.md: missing `End-of-run commit` section",
        )
        self.assertIn(
            "git status --porcelain",
            text,
            "xlfg.md: commit step must read `git status --porcelain`",
        )
        self.assertIn(
            "`git add -A`",
            text,
            "xlfg.md: commit step must explicitly forbid `git add -A`",
        )
        self.assertIn("docs/xlfg/runs/", text)
        self.assertIn(".xlfg/", text)
        self.assertIn(
            "conventional commits",
            lower,
            "xlfg.md: commit step must prescribe Conventional Commits style",
        )
        self.assertIn(
            "| Commit ",
            text,
            "xlfg.md: Completion summary table must carry a `| Commit |` "
            "row that surfaces the commit SHA + subject.",
        )

    def test_xlfg_debug_conductor_does_not_prescribe_commit(self) -> None:
        """`/xlfg-debug` is product-frozen and must not prescribe a commit.

        v6.5.3 narrows this guard: reading `git status --porcelain` is now
        required (see `test_xlfg_debug_conductor_verifies_no_source_edits`),
        so the ban collapses to the two substrings that still name a commit
        action — `end-of-run commit` and `conventional commits`.
        """
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        lower = text.lower()
        self.assertNotIn("end-of-run commit", lower)
        self.assertNotIn("conventional commits", lower)

    def test_conductors_forbid_mid_run_turn_endings(self) -> None:
        """v6.5.2 regression guard. Both conductors must explicitly forbid
        ending the turn between phases.

        v4 had a `Stop` hook that enforced this from the harness. v6.0 removed
        the hook; v6.5.2 replaces it with prose discipline — the conductor
        carries a `## Between phases` section, the `one run, one conductor
        turn` rule, an explicit `do not end your turn` prohibition, and a
        named `Proceeding` anti-pattern call-out.
        """
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            lower = text.lower()
            self.assertIn(
                "## between phases",
                lower,
                f"{cmd}: missing `## Between phases` section",
            )
            self.assertIn(
                "one run, one conductor turn",
                lower,
                f"{cmd}: missing `One run, one conductor turn` rule",
            )
            self.assertIn(
                "do not end your turn",
                lower,
                f"{cmd}: must explicitly forbid ending the conductor turn "
                "between phases",
            )
            self.assertIn(
                "proceeding",
                lower,
                f"{cmd}: must call out the `Proceeding to ...` anti-pattern "
                "by name",
            )

    def test_phase_bodies_carry_handoff_cue(self) -> None:
        """v6.5.4 regression guard. Every phase body — the 5 phase skills and
        the 4 phase agents — must carry the `handoff cue, not an end-of-run
        marker` reminder inline at its return point.

        v6.5.2 planted this reminder on 3 of 5 phase skills (intent, plan,
        implement) and deliberately skipped the 4 phase agents and the 2
        terminal skills (compound, debug-phase) on the rationale that the
        conductor's `## Between phases` section was sufficient. v6.5.4
        falsifies that rationale: the conductor's between-phases section is
        read *before* a phase dispatches, but the decision whether to end
        the turn happens *after* the phase returns, inside the phase body
        whose terminal block (fenced Return format for agents, bullet-list
        Stop-traps or Optional-specialists for terminal skills) reads as a
        natural end-of-turn milestone. Extending the reminder symmetrically
        to all 9 phase bodies lands the cue at the exact decision point;
        this test pins that symmetry so the next drift is loud.
        """
        phase_bodies = [
            PLUGIN / "skills" / "xlfg-intent-phase" / "SKILL.md",
            PLUGIN / "skills" / "xlfg-plan-phase" / "SKILL.md",
            PLUGIN / "skills" / "xlfg-implement-phase" / "SKILL.md",
            PLUGIN / "skills" / "xlfg-compound-phase" / "SKILL.md",
            PLUGIN / "skills" / "xlfg-debug-phase" / "SKILL.md",
            PLUGIN / "agents" / "xlfg-recall.md",
            PLUGIN / "agents" / "xlfg-context.md",
            PLUGIN / "agents" / "xlfg-verify.md",
            PLUGIN / "agents" / "xlfg-review.md",
        ]
        for path in phase_bodies:
            lower = path.read_text(encoding="utf-8").lower()
            rel = path.relative_to(PLUGIN)
            self.assertIn(
                "handoff cue",
                lower,
                f"{rel}: must carry the `handoff cue` reminder inline at its "
                "return point so the reinforcement is visible at the exact "
                "moment the conductor decides whether to end the turn.",
            )
            self.assertIn(
                "not an end-of-run marker",
                lower,
                f"{rel}: must spell out `not an end-of-run marker` so the "
                "phase-return block is not read as a turn-close milestone.",
            )

    def test_conductors_prescribe_real_clock_for_run_id(self) -> None:
        """RUN_ID must come from the system clock via `date`, not model guesswork."""
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            self.assertIn(
                "date +%Y%m%d-%H%M%S",
                text,
                f"{cmd}: must prescribe `date +%Y%m%d-%H%M%S` for RUN_ID",
            )
            lower = text.lower()
            self.assertIn(
                "do not invent",
                lower,
                f"{cmd}: startup body must forbid inventing the timestamp",
            )

    def _count_summary_table_rows(self, cmd: str) -> int:
        """Count `| Label | placeholder |` rows inside a command's
        `## Completion summary` section. Header / separator rows
        (the ones that are all dashes or all empty cells) are skipped.
        """
        text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
        m = re.search(
            r"## Completion summary.*?(?=\n## |\Z)",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(
            m, f"{cmd}: ## Completion summary section missing"
        )
        section = m.group(0)
        rows = 0
        for line in section.split("\n"):
            stripped = line.strip()
            if not stripped.startswith("|") or not stripped.endswith("|"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 2:
                continue
            # Skip header separator (all dashes) and empty header rows.
            if all(set(c) <= set("-:") for c in cells):
                continue
            if all(c == "" for c in cells):
                continue
            label = cells[0]
            # Real data rows have a non-empty, non-dash label cell.
            if label and not set(label) <= set("-:"):
                rows += 1
        return rows

    def test_xlfg_debug_completion_summary_item_count_matches_budget(self) -> None:
        """`/xlfg-debug` summary must be a markdown table within budget.

        v6.5.6 switched the template from `**Label:** value` lines to an
        actual markdown table (`| Label | value |`) and added a hard
        ≤80-char-per-cell rule. The budget for `/xlfg-debug` stays at 6
        mandatory rows — Mechanism, Evidence, Repair, Unknowns, Verified,
        Archive — each load-bearing.
        """
        rows = self._count_summary_table_rows("xlfg-debug.md")
        self.assertGreater(
            rows,
            0,
            "xlfg-debug.md: Completion summary must contain a markdown "
            "table (`| Label | value |` rows).",
        )
        self.assertLessEqual(
            rows,
            6,
            f"xlfg-debug.md: Completion summary table has {rows} data "
            "rows but the budget is 6.",
        )

    def test_xlfg_completion_summary_item_count_matches_budget(self) -> None:
        """`/xlfg`'s summary must be a markdown table within budget.

        Sibling guard. v6.5.6 caps the `/xlfg` summary at 6 rows max
        (4 mandatory: Shipped, Proof, Commit, Archive; 2 optional: Risk,
        Next — included in the template definition but omitted at runtime
        when there is nothing concrete to say). The `Files` row was
        dropped entirely as redundant with `git show <sha>`.
        """
        rows = self._count_summary_table_rows("xlfg.md")
        self.assertGreater(
            rows,
            0,
            "xlfg.md: Completion summary must contain a markdown table "
            "(`| Label | value |` rows).",
        )
        self.assertLessEqual(
            rows,
            6,
            f"xlfg.md: Completion summary table has {rows} data rows "
            "but the budget is 6 (4 mandatory + 2 optional).",
        )

    def test_xlfg_completion_summary_drops_durable_lesson(self) -> None:
        """The `/xlfg` terminal summary must NOT carry a durable-lesson row.

        Pre-v6.5.5 the terminal summary repeated the compound skill's
        durable lesson. The lesson is already archived in `run-summary.md`;
        repeating it in the terminal duplicated content the user can read on
        demand. v6.5.5 drops the row from the terminal template (the lesson
        still gets written to `run-summary.md` by the compound skill, which
        is unchanged). Guard against re-adding it.
        """
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        # Extract the Completion summary section only.
        m = re.search(
            r"## Completion summary.*?(?=\n## |\Z)",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(m, "xlfg.md: ## Completion summary section missing")
        section = m.group(0).lower()
        self.assertNotIn(
            "durable lesson",
            section,
            "xlfg.md: Completion summary must not carry a `durable lesson` "
            "row — the lesson is in run-summary.md, repeating it bloats the "
            "terminal output.",
        )

    def test_conductors_carry_question_template(self) -> None:
        """Both conductors must carry a strict §Question template.

        Prior to v6.5.5 the intent-halt instruction was a one-liner with
        no shape. v6.5.5 added the §Question template; v6.5.6 trimmed its
        lead from `Need <n> answers before proceeding:` to `Need <n>
        answers:` and renamed the footer from `Blocking because:` to
        `Blocking:` to drop filler.
        """
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            self.assertIn(
                "## Question template",
                text,
                f"{cmd}: must carry a `## Question template` section so "
                "intent-halt questions follow a strict shape.",
            )
            self.assertIn(
                "Need <n> answers:",
                text,
                f"{cmd}: question template must use the `Need <n> "
                "answers:` lead (no `before proceeding` filler).",
            )
            self.assertIn(
                "Blocking:",
                text,
                f"{cmd}: question template must use the `Blocking:` "
                "footer (one line, covering all questions).",
            )
            self.assertIn(
                "≤80",
                text,
                f"{cmd}: question template must declare the 80-char cap.",
            )

    def test_completion_summary_uses_table_format(self) -> None:
        """Both conductor summaries must be markdown tables, not bullet lines.

        v6.5.5 used `**Label:** value` lines. v6.5.6 switches to actual
        markdown tables (`| Label | value |`) so terminal output renders
        in a tight grid.
        """
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            rows = self._count_summary_table_rows(cmd)
            self.assertGreater(
                rows,
                0,
                f"{cmd}: Completion summary must use a markdown table "
                "(`| Label | value |` rows).",
            )

    def test_completion_summary_declares_cell_length_cap(self) -> None:
        """Both conductor summaries must declare the per-cell length cap.

        The 80-char rule is the load-bearing concision constraint. If the
        template does not name it, the model falls back to 2–3-sentence
        cells and the table bloats again.
        """
        for cmd in ("xlfg.md", "xlfg-debug.md"):
            text = (PLUGIN / "commands" / cmd).read_text(encoding="utf-8")
            m = re.search(
                r"## Completion summary.*?(?=\n## |\Z)",
                text,
                re.DOTALL,
            )
            self.assertIsNotNone(m)
            section = m.group(0)
            self.assertIn(
                "≤80",
                section,
                f"{cmd}: Completion summary must declare the ≤80-char "
                "per-cell cap.",
            )

    def test_xlfg_completion_summary_drops_files_row(self) -> None:
        """`/xlfg` summary template must NOT carry a `Files` row.

        v6.5.5 included `**Files:**` listing changed paths. v6.5.6 drops
        it entirely — `git show <sha>` and `run-summary.md` already list
        files, and a real-world example showed the row routinely
        producing 3-line directory dumps that bloated the terminal.
        """
        text = (PLUGIN / "commands" / "xlfg.md").read_text(encoding="utf-8")
        m = re.search(
            r"## Completion summary.*?(?=\n## |\Z)",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(m)
        section = m.group(0)
        self.assertNotRegex(
            section,
            r"\|\s*Files\s*\|",
            "xlfg.md: Completion summary must not carry a `| Files |` "
            "row — git show + run-summary.md already list files.",
        )
        self.assertNotIn(
            "**Files:**",
            section,
            "xlfg.md: Completion summary must not carry a `**Files:**` "
            "row either.",
        )

    def test_xlfg_debug_conductor_verifies_no_source_edits(self) -> None:
        """`/xlfg-debug` must verify the no-source-edits contract via command.

        v6.5.3 added the mandatory `git status --porcelain` step plus a
        `verified via` citation in the summary. v6.5.6 tightened the
        summary to a markdown table and the citation collapsed to a cell
        value (`git status --porcelain clean`). The contract assertion
        remains: the conductor reads the command and the summary table
        carries the command literally in its Verified row.
        """
        text = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        # The conductor body must read git status --porcelain.
        self.assertIn(
            "git status --porcelain",
            text,
            "xlfg-debug.md: conductor must read `git status --porcelain` to "
            "verify the no-source-edits contract before writing the summary.",
        )
        # The completion-summary table must carry the verifying command in
        # its Verified row so the contract is visible at the user surface.
        m = re.search(
            r"## Completion summary.*?(?=\n## |\Z)",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(m)
        section = m.group(0)
        self.assertIn(
            "git status --porcelain",
            section,
            "xlfg-debug.md: Completion summary must literally cite "
            "`git status --porcelain` (in the Verified row) so the "
            "contract is visible at the user surface, not just in prose.",
        )

    def test_xlfg_debug_names_sanctioned_write_path(self) -> None:
        """The single sanctioned `Write` path must be explicit in both bodies.

        `allowed-tools` grants `Write` at the tool layer; v6.5.2 declared
        "only sanctioned use" in prose but the restriction appeared only in
        the skill body and the conductor's opener. v6.5.3 promotes the
        restriction into the conductor's Operating contract and the debug
        skill's How-to-work-it opener, so both surfaces the model re-reads
        under pressure carry the path explicitly.
        """
        conductor = (PLUGIN / "commands" / "xlfg-debug.md").read_text(encoding="utf-8")
        skill = (PLUGIN / "skills" / "xlfg-debug-phase" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        path_literal = "docs/xlfg/runs/<RUN_ID>/diagnosis.md"
        for label, body in (("xlfg-debug.md", conductor), ("xlfg-debug-phase/SKILL.md", skill)):
            self.assertIn(
                path_literal,
                body,
                f"{label}: must name the single sanctioned Write path "
                f"`{path_literal}` so the model can re-read the restriction.",
            )
            lower = body.lower()
            self.assertIn(
                "sanctioned write path",
                lower,
                f"{label}: must frame the path as the sanctioned Write "
                "target (not just an archive location) so the restriction is "
                "visible in the operating-contract section.",
            )

    def test_xlfg_debug_design_notes_no_stale_artifacts(self) -> None:
        """Design notes must not promote artifacts that don't exist in v6.

        v6.5.3 retires the stale artifact names (`spec.md`, `debug-report.md`,
        `repro-notes.md`, `probe-log.md`, `history-findings.md`) from the
        design notes. They may appear once in the `v6.5.x update` banner at
        the top (as "earlier drafts referenced X") but nowhere else — a real
        bullet or prose mention would imply they exist.
        """
        notes = (REPO / "docs" / "xlfg-debug-design-notes.md").read_text(
            encoding="utf-8"
        )
        stale = (
            "spec.md",
            "debug-report.md",
            "repro-notes.md",
            "probe-log.md",
            "history-findings.md",
        )
        for name in stale:
            bad_lines = [
                line
                for line in notes.split("\n")
                if name in line and not line.lstrip().startswith(">")
            ]
            self.assertEqual(
                bad_lines,
                [],
                f"docs/xlfg-debug-design-notes.md: `{name}` must not appear "
                "outside the `v6.5.x update` banner (lines starting with `>`); "
                f"found: {bad_lines!r}",
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
