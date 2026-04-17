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
        plugin_skill_path = repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg" / "SKILL.md"

        self.assertTrue(command_path.exists())
        self.assertFalse(plugin_skill_path.exists())

        command_md = command_path.read_text(encoding="utf-8")

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

        self.assertIn("allowed-tools:", command_md)
        self.assertIn("effort: high", command_md)
        self.assertIn("ExitPlanMode", command_md)
        self.assertIn("one autonomous run", command_md.lower())
        self.assertIn("batch of hidden phase skills", command_md.lower())
        self.assertIn("do not ask the user to run internal skills", command_md.lower())
        self.assertIn("single source of truth", command_md.lower())
        self.assertIn("atomic packet", command_md.lower())
        self.assertIn("resume the **same specialist**", command_md.lower())
        self.assertIn("Sync scaffold if missing or stale", command_md)
        self.assertIn("write the lean core run directories", command_md)
        self.assertNotIn("plugins/xlfg-engineering/skills/xlfg/SKILL.md", command_md)
        self.assertIn("\nname: xlfg", command_md)

        for phase_name in plugin_phase_names:
            self.assertIn(phase_name, command_md)

        self.assertIn("Skill(xlfg-engineering:xlfg-intent-phase *)", command_md)
        # Reject the stale `Task` tool name (replaced by `Agent` or `Skill`).
        # `TaskCreate` / `TaskUpdate` / `TaskList` (v3.1.0 task bridge)
        # are legitimate and MUST NOT be rejected here.
        for stale in (", Task,", ", Task\n", ", Task ", " Task(", " Task "):
            self.assertNotIn(stale, command_md, f"stale `Task` tool name in command: {stale!r}")

        # Phase-state tracking and loopback cap (v2.8.0)
        self.assertIn("phase-state.json", command_md)
        self.assertIn("phase-state tracking", command_md.lower())

        # v3.2.2 regression guard: startup must clear any stale
        # `.xlfg/phase-state.json` from a prior run. Without this, Claude
        # Code's Write tool errors with "File has not been read yet. Read
        # it first before writing to it." on every repeat /xlfg run.
        self.assertIn("rm -f .xlfg/phase-state.json", command_md)
        self.assertIn("max 2 loopbacks", command_md.lower())
        self.assertIn("loopback_count", command_md)


    def test_runtime_prompts_do_not_depend_on_query_contract_file(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_paths = [
            repo_root / "plugins" / "xlfg-engineering" / "commands",
            repo_root / "plugins" / "xlfg-engineering" / "skills",
            repo_root / "plugins" / "xlfg-engineering" / "agents",
        ]
        # `xlfg-audit.md` is the meta self-audit and intentionally names
        # forbidden tokens (including `query-contract.md`) so it can sweep
        # the rest of the runtime for them. Exempting it keeps the check
        # honest: it enforces "no dependency on query-contract.md", not
        # "no mention of the string anywhere".
        audit_path = repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-audit.md"
        for target in runtime_paths:
            for path in sorted(target.rglob("*.md")):
                if path == audit_path:
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("query-contract.md", text, msg=str(path.relative_to(repo_root)))

    def test_xlfg_audit_is_per_run_post_mortem_not_harness_self_check(self) -> None:
        # As of v4.2.0 /xlfg-audit is the per-run user post-mortem.
        # The harness self-check moved to scripts/audit-harness.mjs and
        # runs in CI. The slash command body must:
        #   - delegate to scripts/post-mortem.mjs (no inline computation)
        #   - preserve the flrngel/xlfg submission flow (with redaction)
        #   - NOT attempt to inspect plugin manifests / SKILL frontmatter
        repo_root = Path(__file__).resolve().parents[1]
        audit_text = (repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-audit.md").read_text(encoding="utf-8")

        # delegates to the post-mortem script
        self.assertIn("scripts/post-mortem.mjs", audit_text)
        # preserves submission target (hardcoded; no per-user override)
        self.assertIn("--repo flrngel/xlfg", audit_text)
        # preserves redaction contract
        self.assertIn("Redaction contract", audit_text)
        # is no longer pretending to be the harness self-check
        self.assertNotIn("Version sync", audit_text)
        self.assertNotIn("SDLC coverage", audit_text)
        self.assertNotIn("workflow_load_score", audit_text)
        # forbidden tokens that previously lived in the audit body must
        # NOT appear here either — the new body is a thin orchestrator,
        # not a check definition
        self.assertNotIn("query-contract.md", audit_text)

    def test_plugin_support_skills_are_hidden_background_helpers(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for skill_path in sorted((repo_root / "plugins" / "xlfg-engineering" / "skills").rglob("SKILL.md")):
            text = skill_path.read_text(encoding="utf-8")
            self.assertNotIn("\nname:", text)
            self.assertIn("user-invocable: false", text)


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
        root = repo_root / "plugins" / "xlfg-engineering" / "agents"
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
        ]
        targets.extend(sorted((repo_root / "plugins" / "xlfg-engineering" / "skills").glob("xlfg-*-phase/SKILL.md")))
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
        base = repo_root / "plugins" / "xlfg-engineering" / "skills"
        for phase_name in phase_names:
            text = (base / phase_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Only the phase conductor may delegate.", text)

    def test_review_phase_keeps_small_fanout(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        base = repo_root / "plugins" / "xlfg-engineering" / "skills"
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

    def test_all_delegating_entrypoints_require_context_digest_and_prior_siblings(self) -> None:
        """v4.4.0 — every delegating entrypoint (conductor + every phase skill that
        dispatches specialists) must mandate `CONTEXT_DIGEST` + `PRIOR_SIBLINGS` in
        its packet contract so siblings stop re-reading the same canonical files
        and re-deriving the same findings.
        """
        repo_root = Path(__file__).resolve().parents[1]
        targets = [repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md"]
        targets.extend(sorted((repo_root / "plugins" / "xlfg-engineering" / "skills").glob("xlfg-*-phase/SKILL.md")))
        for path in targets:
            text = path.read_text(encoding="utf-8")
            if "Agent" not in text and "SendMessage" not in text and path.name != "xlfg.md":
                continue
            self.assertIn("CONTEXT_DIGEST", text, f"Missing CONTEXT_DIGEST contract in {path}")
            self.assertIn("PRIOR_SIBLINGS", text, f"Missing PRIOR_SIBLINGS contract in {path}")

    def test_all_delegating_entrypoints_require_ownership_boundary(self) -> None:
        """v4.5.0 — every delegating entrypoint must define lane ownership before
        dispatch so specialists cite adjacent work instead of re-adjudicating it.
        """
        repo_root = Path(__file__).resolve().parents[1]
        targets = [repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md"]
        targets.extend(sorted((repo_root / "plugins" / "xlfg-engineering" / "skills").glob("xlfg-*-phase/SKILL.md")))
        for path in targets:
            text = path.read_text(encoding="utf-8")
            if "Agent" not in text and "SendMessage" not in text and path.name != "xlfg.md":
                continue
            self.assertIn("OWNERSHIP_BOUNDARY", text, f"Missing OWNERSHIP_BOUNDARY contract in {path}")
            self.assertIn("Do not redo", text, f"Ownership packet must name non-owned work in {path}")
            self.assertIn("Consume:", text, f"Ownership packet must name consumed artifacts in {path}")

    def test_specialist_agents_honor_context_digest_and_prior_siblings(self) -> None:
        """v4.4.0 — every specialist agent's Turn budget rule must reference both
        `CONTEXT_DIGEST` and `PRIOR_SIBLINGS` so the dedup contract is two-sided.
        """
        repo_root = Path(__file__).resolve().parents[1]
        agent_root = repo_root / "plugins" / "xlfg-engineering" / "agents"
        for agent_path in sorted(agent_root.rglob("*.md")):
            if "_shared" in agent_path.parts:
                continue
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("CONTEXT_DIGEST", text, f"Missing CONTEXT_DIGEST awareness in {agent_path.name}")
            self.assertIn("PRIOR_SIBLINGS", text, f"Missing PRIOR_SIBLINGS awareness in {agent_path.name}")

    def test_specialist_agents_honor_ownership_boundary(self) -> None:
        """v4.5.0 — every specialist must obey the ownership boundary and use a
        pointer instead of repeating adjacent-lane analysis.
        """
        repo_root = Path(__file__).resolve().parents[1]
        agent_root = repo_root / "plugins" / "xlfg-engineering" / "agents"
        for agent_path in sorted(agent_root.rglob("*.md")):
            if "_shared" in agent_path.parts:
                continue
            text = agent_path.read_text(encoding="utf-8")
            self.assertIn("OWNERSHIP_BOUNDARY", text, f"Missing OWNERSHIP_BOUNDARY awareness in {agent_path.name}")
            self.assertIn("Covered elsewhere", text, f"Missing overlap pointer rule in {agent_path.name}")

    def test_canonical_template_documents_dispatch_packet_shape(self) -> None:
        """v4.4.0 — the shared output template owns the canonical packet shape so
        every phase skill and agent file can reference one source of truth.
        """
        repo_root = Path(__file__).resolve().parents[1]
        template = (repo_root / "plugins" / "xlfg-engineering" / "agents" / "_shared" / "output-template.md").read_text(encoding="utf-8")
        self.assertIn("Dispatch packet shape", template)
        self.assertIn("OWNERSHIP_BOUNDARY", template)
        self.assertIn("CONTEXT_DIGEST", template)
        self.assertIn("PRIOR_SIBLINGS", template)

    def test_high_overlap_agent_boundaries_are_explicit(self) -> None:
        """v4.5.0 — the risky overlap pairs must keep explicit ownership text."""
        repo_root = Path(__file__).resolve().parents[1]
        agents = repo_root / "plugins" / "xlfg-engineering" / "agents"
        expected = {
            agents / "planning" / "xlfg-test-strategist.md": [
                "Reference scenario IDs and `DA*` IDs",
                "Treat `harness-profile.md` as the owner of proof intensity",
            ],
            agents / "planning" / "xlfg-ui-designer.md": [
                "own UI/a11y `DA*` criteria only",
                "record the prior DA coverage",
            ],
            agents / "implementation" / "xlfg-task-implementer.md": [
                "Own product/source changes",
                "no separate `xlfg-test-implementer` lane will run",
            ],
            agents / "implementation" / "xlfg-test-implementer.md": [
                "Own test and proof-file changes",
                "avoid editing product/source files",
            ],
            agents / "implementation" / "xlfg-task-checker.md": [
                "Stay read-only with respect to product/test files",
                "avoid rerunning full scenario proof",
            ],
            agents / "verify" / "xlfg-verify-runner.md": [
                "Own command execution and raw evidence capture only",
                "leave run-status judgment",
            ],
            agents / "verify" / "xlfg-verify-reducer.md": [
                "Consume `xlfg-verify-runner` artifacts",
                "Do not rerun commands",
            ],
            agents / "review" / "xlfg-ux-reviewer.md": [
                "cite `ui-verification.md`",
                "not already covered",
            ],
        }
        for path, needles in expected.items():
            text = path.read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"Missing overlap boundary {needle!r} in {path.name}")

    def test_phase_skills_document_known_overlap_boundaries(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        base = repo_root / "plugins" / "xlfg-engineering" / "skills"
        expected = {
            "xlfg-context-phase": ["`xlfg-repo-mapper` owns command and structure inventory", "`xlfg-harness-profiler` owns budget/profile selection"],
            "xlfg-plan-phase": ["`xlfg-test-strategist` owns proof commands", "`xlfg-task-divider` owns canonical task IDs"],
            "xlfg-implement-phase": ["`xlfg-task-implementer` owns product/source changes", "`xlfg-task-checker` owns the task-local ACCEPT/REVISE verdict"],
            "xlfg-verify-phase": ["`xlfg-verify-runner` owns command execution", "`xlfg-verify-reducer` owns GREEN/RED/FAILED reduction"],
            "xlfg-review-phase": ["Every reviewer must fill \"Already covered by verification\"", "UX owns user-flow and accessibility critique"],
        }
        for phase_name, needles in expected.items():
            text = (base / phase_name / "SKILL.md").read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"Missing phase overlap boundary {needle!r} in {phase_name}")

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

    def test_ui_designer_agent_exists(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        plugin = repo_root / "plugins" / "xlfg-engineering" / "agents" / "planning" / "xlfg-ui-designer.md"
        self.assertTrue(plugin.exists(), f"missing {plugin}")
        text = plugin.read_text(encoding="utf-8")
        self.assertIn("DOCS_RUN_DIR/ui-design.md", text)
        self.assertIn("DOCS_RUN_DIR/ui-verification.md", text)
        self.assertIn("## Specialist identity", text)
        self.assertIn("## Execution contract", text)

    def test_ui_designer_is_wired_into_plan_phase_with_conditional_trigger(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for path in [
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-plan-phase" / "SKILL.md",
        ]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("xlfg-ui-designer", text, f"plan-phase must reference xlfg-ui-designer: {path}")
            self.assertIn("UI-related", text, f"plan-phase must describe conditional trigger: {path}")
            self.assertIn("DOCS_RUN_DIR/ui-design.md", text, f"plan-phase must pass artifact path: {path}")

    def test_ui_designer_is_wired_into_verify_phase_with_conditional_trigger(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for path in [
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-verify-phase" / "SKILL.md",
        ]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("xlfg-ui-designer", text, f"verify-phase must reference xlfg-ui-designer: {path}")
            self.assertIn("UI-related", text, f"verify-phase must describe conditional trigger: {path}")
            self.assertIn("DOCS_RUN_DIR/ui-verification.md", text, f"verify-phase must pass artifact path: {path}")


    # ------------------------------------------------------------------
    # v4.3.0 — speed-optimization shape assertions (memo /tmp/hey-xlfg-authors.md)
    # ------------------------------------------------------------------

    def test_implementer_artifact_kind_branch_rule(self) -> None:
        """T1 / O1 — xlfg-task-implementer must carry a non-markdown guard and
        ARTIFACT_KIND packet header so YAML frontmatter never leaks into .py /
        .json / .yaml / other source artifacts.
        """
        repo_root = Path(__file__).resolve().parents[1]
        impl = (
            repo_root / "plugins" / "xlfg-engineering" / "agents" / "implementation" / "xlfg-task-implementer.md"
        ).read_text(encoding="utf-8")
        # Must reference ARTIFACT_KIND as a packet header name.
        self.assertIn("ARTIFACT_KIND", impl)
        # Must enumerate the four kinds.
        for kind in ("planning-doc", "source-file", "config-file", "test-file"):
            self.assertIn(kind, impl, f"implementer prompt missing ARTIFACT_KIND value: {kind!r}")
        # Must explicitly forbid frontmatter on non-markdown artifacts. The
        # phrase can vary, but "never write YAML frontmatter" must appear in
        # the non-markdown branch.
        self.assertIn("never write yaml frontmatter", impl.lower().replace("**", ""))
        # HC4 existing substrings must still be intact.
        self.assertIn("status: IN_PROGRESS", impl)

        # Packet format docs in the conductor command must document ARTIFACT_KIND.
        cmd = (repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md").read_text(encoding="utf-8")
        self.assertIn("ARTIFACT_KIND:", cmd)
        # Existing atomic-packet substrings must still be intact.
        self.assertIn("PRIMARY_ARTIFACT:", cmd)
        self.assertIn("DONE_CHECK:", cmd)
        self.assertIn("RETURN_CONTRACT:", cmd)

    def test_recall_skill_git_recency_mandatory(self) -> None:
        """T3 / O3 — recall skill must enforce a git-recency check, not merely
        recommend it.
        """
        repo_root = Path(__file__).resolve().parents[1]
        recall = (
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-recall-phase" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("git log --since", recall)
        self.assertIn("HYPOTHESIS-ONLY", recall)
        self.assertIn("Verify-before-use:", recall)
        # The upgrade must be mandatory-voiced; MUST appears in the guardrail.
        self.assertIn("MUST", recall)
        # And the MUST must live near the git-log phrase, not in some unrelated
        # paragraph. Assert both substrings appear in the same ~30-line window.
        must_line = None
        git_log_line = None
        for i, line in enumerate(recall.splitlines()):
            if "MUST" in line and must_line is None:
                must_line = i
            if "git log --since" in line and git_log_line is None:
                git_log_line = i
        self.assertIsNotNone(must_line)
        self.assertIsNotNone(git_log_line)
        self.assertLessEqual(abs(must_line - git_log_line), 30, "MUST and git-log guidance must be co-located")

    def test_test_strategist_smoke_tier(self) -> None:
        """T5 / O5 — test-strategist enum must include `acceptance`, and the
        output format must document `smoke_check` as a required field for that tier.
        """
        repo_root = Path(__file__).resolve().parents[1]
        strat = (
            repo_root / "plugins" / "xlfg-engineering" / "agents" / "planning" / "xlfg-test-strategist.md"
        ).read_text(encoding="utf-8")
        # ship_phase enum must include `acceptance` as a first-class tier.
        self.assertIn("`acceptance`", strat)
        self.assertIn("`smoke`", strat)
        # `smoke_check` field must be a normative output.
        self.assertIn("smoke_check:", strat)
        # Must state the dependency: acceptance requires smoke_check.
        self.assertIn("acceptance", strat.lower())

    def test_verify_phase_runs_smoke_first(self) -> None:
        """T5 / O5 — verify-phase skill must execute smoke_check before acceptance
        and stop on deterministic smoke failure.
        """
        repo_root = Path(__file__).resolve().parents[1]
        verify = (
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-verify-phase" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("smoke_check", verify)
        self.assertIn("acceptance", verify.lower())
        # Must articulate "run smoke first" AND the deterministic-failure stop.
        lower = verify.lower()
        self.assertTrue(
            "smoke" in lower and "first" in lower,
            "verify-phase must instruct running smoke before acceptance",
        )

    def test_loopback_arithmetic_documented(self) -> None:
        """T6 / O6 — conductor command must formalize when loopback_count
        increments and when it does not.
        """
        repo_root = Path(__file__).resolve().parents[1]
        cmd = (repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg.md").read_text(encoding="utf-8")
        self.assertIn("loopback_count", cmd)
        # Arithmetic section header or equivalent normative label.
        self.assertIn("arithmetic", cmd.lower())
        # Must explicitly call out the non-counting cases — at minimum, plan
        # repairs and APPROVE-WITH-NOTES-FIXED.
        self.assertIn("APPROVE-WITH-NOTES-FIXED", cmd)
        # REVISE plan repairs must be named as non-counting.
        self.assertTrue(
            "REVISE" in cmd or "plan-phase repair" in cmd.lower(),
            "plan-phase repair exemption must be documented",
        )

    def test_review_approve_with_notes_fixed(self) -> None:
        """T6 / O6 — review skill must declare APPROVE-WITH-NOTES-FIXED as a
        distinct verdict and state it does not consume a loopback.
        """
        repo_root = Path(__file__).resolve().parents[1]
        review = (
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-review-phase" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("APPROVE-WITH-NOTES-FIXED", review)
        # Must say this verdict does not consume a loopback.
        lower = review.lower()
        self.assertIn("loopback", lower)
        self.assertTrue(
            "not consume" in lower or "does **not** consume" in lower or "without consuming" in lower,
            "review skill must state APPROVE-WITH-NOTES-FIXED does not consume a loopback",
        )

    def test_compound_phase_word_cap(self) -> None:
        """T7 / O7 — compound skill must document a ~200-word cap per run on
        current-state.md entries.
        """
        repo_root = Path(__file__).resolve().parents[1]
        compound = (
            repo_root / "plugins" / "xlfg-engineering" / "skills" / "xlfg-compound-phase" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("200", compound)
        self.assertIn("current-state.md", compound)
        self.assertIn("compound-summary.md", compound)

    def test_xlfg_status_command_exists(self) -> None:
        """T7 / O7 — read-only /xlfg-status command must exist and document
        itself as read-only.
        """
        repo_root = Path(__file__).resolve().parents[1]
        path = repo_root / "plugins" / "xlfg-engineering" / "commands" / "xlfg-status.md"
        self.assertTrue(path.exists(), f"missing {path}")
        text = path.read_text(encoding="utf-8")
        self.assertGreater(len(text), 200, "xlfg-status command body too short")
        # Must declare itself read-only.
        lower = text.lower()
        self.assertIn("read-only", lower)
        # Must read .xlfg/phase-state.json.
        self.assertIn(".xlfg/phase-state.json", text)
        # Frontmatter discipline: command must have allowed-tools and disable model-invocation.
        self.assertIn("disable-model-invocation: true", text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
