#!/usr/bin/env python3
"""xlfg audit-harness (v6) — deterministic self-check of the xlfg plugin.

v6.0.0 removed sub-agents, phase skills, the Codex surface, and per-phase
file artifacts. The audit is correspondingly smaller: four checks, each a
simple file read / frontmatter parse / forbidden-token sweep.

Usage:
  audit_harness.py                 # auto-detects plugin root
  audit_harness.py --plugin <path> # explicit
  audit_harness.py --json          # machine-readable

Exit code: 0 = every check passed, 1 = any check failed.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PUBLIC_COMMANDS = ("xlfg.md", "xlfg-debug.md", "xlfg-init.md")

# The 9 phase skills the conductors dispatch. Shared ones (recall/intent/context)
# are consumed by both `/xlfg` and `/xlfg-debug`.
EXPECTED_PHASE_SKILLS = (
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

# v6.3 restored the v5 specialist expertise as hidden skills that phase skills
# can load on-demand. These are optional lenses — the phase skill decides
# whether a given specialist is worth loading for the work at hand. They stay
# hidden (user-invocable: false) and run in the conductor's own context.
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

# Tokens that indicate the v5 sub-agent dispatch contract is creeping back into
# the runtime prompt. v6.2 keeps phase skills (see EXPECTED_SKILLS) but does
# NOT have sub-agents, dispatch packets, or per-phase coordination files.
#
# Note: `xlfg-engineering:xlfg-` is now the intended pattern (the conductor
# frontmatter lists each skill this way), so it is NOT forbidden. The SubagentStop
# hook / subagent-stop-guard / ledger-append tokens are forbidden because those
# tools were deleted in v6.0.
FORBIDDEN_RUNTIME_TOKENS = (
    "PRIMARY_ARTIFACT",
    "OWNERSHIP_BOUNDARY",
    "CONTEXT_DIGEST",
    "PRIOR_SIBLINGS",
    "RETURN_CONTRACT:",
    "ARTIFACT_KIND:",
    "DONE_CHECK:",
    "SubagentStop",
    "subagent-stop-guard",
    "ledger-append",
)

_FRONTMATTER_KV_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
_EXIT_PLAN_MODE_RE = re.compile(
    r"PermissionRequest:\s*\n[\s\S]*?matcher:\s*\"ExitPlanMode\"[\s\S]*?behavior\":\s*\"allow\""
)


def _parse_args(argv: list[str]) -> dict[str, object]:
    out: dict[str, object] = {"json": False}
    i = 0
    while i < len(argv):
        k = argv[i]
        if k == "--plugin" and i + 1 < len(argv):
            out["plugin"] = argv[i + 1]
            i += 2
            continue
        if k == "--json":
            out["json"] = True
            i += 1
            continue
        if k in ("--help", "-h"):
            out["help"] = True
            i += 1
            continue
        raise ValueError(f"unexpected arg: {k}")
    return out


def _resolve_plugin(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    cwd_guess = (Path.cwd() / "plugins/xlfg-engineering").resolve()
    if (cwd_guess / ".claude-plugin/plugin.json").exists():
        return cwd_guess
    here = Path(__file__).resolve().parent
    for _ in range(6):
        if (here / ".claude-plugin/plugin.json").exists():
            return here
        here = here.parent
    raise ValueError("cannot locate plugin root; pass --plugin <path>")


def _read_json(p: Path) -> dict[str, object]:
    return json.loads(p.read_text(encoding="utf-8"))


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


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
        m = _FRONTMATTER_KV_RE.match(line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def _word_count(p: Path) -> int:
    try:
        text = _read_text(p)
    except OSError:
        return 0
    return len(re.findall(r"\S+", text))


def _check_version_sync(plugin_root: Path) -> dict[str, object]:
    manifests = (
        ".claude-plugin/plugin.json",
        ".cursor-plugin/plugin.json",
    )
    versions: dict[str, str | None] = {}
    for m in manifests:
        p = plugin_root / m
        try:
            versions[m] = _read_json(p).get("version")  # type: ignore[assignment]
        except (OSError, json.JSONDecodeError):
            versions[m] = None
    distinct = {v for v in versions.values() if v}
    all_present = all(v for v in versions.values())
    passed = all_present and len(distinct) == 1
    if passed:
        (only,) = distinct
        note = f"{len(distinct)} version across {len(versions)} manifests: {only}"
    else:
        note = f"versions: {json.dumps(versions)}"
    return {
        "id": 1,
        "name": "version sync",
        "pass": passed,
        "score": 1 if passed else 0,
        "note": note,
        "detail": {"versions": versions},
    }


def _check_command_surface(plugin_root: Path) -> dict[str, object]:
    failures: list[str] = []
    commands_dir = plugin_root / "commands"
    shipped = sorted(p.name for p in commands_dir.glob("*.md"))
    expected = set(PUBLIC_COMMANDS)
    unexpected = [c for c in shipped if c not in expected]
    missing = [c for c in expected if c not in shipped]
    for m in missing:
        failures.append(f"missing command: {m}")
    for u in unexpected:
        failures.append(f"unexpected command: {u} (v6 ships only {', '.join(sorted(expected))})")
    return {
        "id": 2,
        "name": "command surface",
        "pass": not failures,
        "score": 1 if not failures else 0,
        "note": (
            f"{len(shipped)} command(s) shipped: {', '.join(shipped) or 'none'}"
            if not failures
            else f"{len(failures)} issue(s)"
        ),
        "detail": {"failures": failures, "shipped": shipped},
    }


def _check_command_frontmatter(plugin_root: Path) -> dict[str, object]:
    failures: list[str] = []
    assertions = 0
    passes = 0
    for cmd in PUBLIC_COMMANDS:
        p = plugin_root / "commands" / cmd
        try:
            text = _read_text(p)
        except OSError:
            failures.append(f"{cmd}: missing")
            assertions += 4
            continue
        fm = _frontmatter(text)
        checks = {
            "name present": "name" in fm,
            "description present and <= 220 chars": bool(fm.get("description")) and len(fm.get("description", "")) <= 220,
            "effort=high": fm.get("effort") == "high",
            "disable-model-invocation=true": fm.get("disable-model-invocation") == "true",
            "allowed-tools present": "allowed-tools" in fm,
            "ExitPlanMode auto-allow present": bool(_EXIT_PLAN_MODE_RE.search(text)),
        }
        for label, ok in checks.items():
            assertions += 1
            if ok:
                passes += 1
            else:
                failures.append(f"commands/{cmd}: {label}")
    score = passes / assertions if assertions else 1
    return {
        "id": 3,
        "name": "command frontmatter",
        "pass": not failures,
        "score": score,
        "note": (
            f"{passes}/{assertions} assertions pass"
            if not failures
            else f"{passes}/{assertions} assertions pass; {len(failures)} failure(s)"
        ),
        "detail": {"failures": failures, "assertions": assertions, "passes": passes},
    }


def _check_forbidden_tokens(plugin_root: Path) -> dict[str, object]:
    """v6 runtime must not carry sub-agent dispatch contract or dead tool references.

    Any leak of old dispatch-packet tokens (PRIMARY_ARTIFACT, OWNERSHIP_BOUNDARY,
    etc.) or references to deleted v5 tooling (SubagentStop, subagent-stop-guard,
    ledger-append) into either a command body or a skill body means a regression
    is sneaking in.
    """
    failures: list[str] = []
    targets: list[tuple[str, Path]] = []
    for cmd in PUBLIC_COMMANDS:
        targets.append((f"commands/{cmd}", plugin_root / "commands" / cmd))
    for skill_name in EXPECTED_SKILLS:
        targets.append(
            (f"skills/{skill_name}/SKILL.md", plugin_root / "skills" / skill_name / "SKILL.md")
        )
    for label, path in targets:
        try:
            text = _read_text(path)
        except OSError:
            failures.append(f"{label}: missing")
            continue
        for tok in FORBIDDEN_RUNTIME_TOKENS:
            if tok in text:
                failures.append(f"{label}: forbidden v6 token present: {tok!r}")
    return {
        "id": 4,
        "name": "forbidden v5 dispatch tokens absent",
        "pass": not failures,
        "score": 1 if not failures else 0,
        "note": (
            "no v5 dispatch tokens leaked into runtime"
            if not failures
            else f"{len(failures)} leak(s)"
        ),
        "detail": {"failures": failures},
    }


def _check_skill_surface(plugin_root: Path) -> dict[str, object]:
    """v6.3 ships 9 phase skills + 27 specialist lens skills.

    Each skill must:
      - live at skills/<name>/SKILL.md
      - have frontmatter with `user-invocable: false` (hidden)
      - have a description (≤220 chars for context-budget discipline)
      - NOT grant `Agent` or `SendMessage` (no nested delegation in v6)
    """
    failures: list[str] = []
    assertions = 0
    passes = 0
    for skill_name in EXPECTED_SKILLS:
        skill_path = plugin_root / "skills" / skill_name / "SKILL.md"
        assertions += 1
        if not skill_path.exists():
            failures.append(f"missing skill: skills/{skill_name}/SKILL.md")
            continue
        passes += 1
        text = _read_text(skill_path)
        fm = _frontmatter(text)
        desc = fm.get("description", "")
        user_invocable = fm.get("user-invocable", "")
        tools = fm.get("allowed-tools", "")

        assertions += 1
        if user_invocable == "false":
            passes += 1
        else:
            failures.append(
                f"skills/{skill_name}: user-invocable must be 'false' (got {user_invocable!r})"
            )
        assertions += 1
        if desc and len(desc) <= 220:
            passes += 1
        else:
            failures.append(
                f"skills/{skill_name}: description missing or > 220 chars (len={len(desc)})"
            )
        assertions += 1
        tool_list = [t.strip() for t in tools.split(",")]
        has_agent = any(re.match(r"^Agent\b", t) for t in tool_list)
        has_send_message = any(re.match(r"^SendMessage\b", t) for t in tool_list)
        if not has_agent and not has_send_message:
            passes += 1
        else:
            failures.append(
                f"skills/{skill_name}: nested-delegation tool leaked (Agent/SendMessage in allowed-tools)"
            )

    # Bonus: catch unexpected skill directories (drift toward v5 specialist sprawl).
    skills_dir = plugin_root / "skills"
    if skills_dir.exists():
        shipped = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
        for name in shipped:
            if name not in EXPECTED_SKILLS:
                failures.append(f"unexpected skill directory: skills/{name}")
                assertions += 1
    score = passes / assertions if assertions else 1
    return {
        "id": 5,
        "name": "phase skill surface",
        "pass": not failures,
        "score": score,
        "note": (
            f"{passes}/{assertions} assertions pass"
            if not failures
            else f"{passes}/{assertions} assertions pass; {len(failures)} failure(s)"
        ),
        "detail": {
            "failures": failures,
            "expected": list(EXPECTED_SKILLS),
            "assertions": assertions,
            "passes": passes,
        },
    }


def _fmt_markdown(results: list[dict[str, object]], plugin_root: Path) -> str:
    lines: list[str] = []
    lines.append("# xlfg audit-harness (v6)")
    lines.append("")
    lines.append(f"Plugin: `{plugin_root}`")
    lines.append("")
    lines.append("| # | Check | Status | Score | Note |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        status = "pass" if r["pass"] else "fail"
        score_val = r["score"]
        if isinstance(score_val, (int, float)) and 0 <= score_val <= 1:
            score = f"{float(score_val):.2f}"
        else:
            score = str(score_val)
        lines.append(f"| {r['id']} | {r['name']} | {status} | {score} | {r['note']} |")
    lines.append("")
    failed = [r for r in results if not r["pass"]]
    if failed:
        lines.append("## Failures")
        lines.append("")
        for r in failed:
            lines.append(f"### {r['id']}. {r['name']}")
            lines.append("")
            detail_failures = (r.get("detail") or {}).get("failures", [])  # type: ignore[union-attr]
            if detail_failures:
                for f in detail_failures:
                    lines.append(f"- {f}")
            else:
                lines.append(f"- {r['note']}")
            lines.append("")
    else:
        lines.append("All checks passed.")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    try:
        args = _parse_args(argv)
    except ValueError as err:
        sys.stderr.write(f"audit-harness: {err}\n")
        return 2
    if args.get("help"):
        sys.stdout.write("Usage: audit_harness.py [--plugin <path>] [--json]\n")
        return 0

    try:
        plugin_root = _resolve_plugin(args.get("plugin"))  # type: ignore[arg-type]
    except ValueError as err:
        sys.stderr.write(f"audit-harness: {err}\n")
        return 2

    results = [
        _check_version_sync(plugin_root),
        _check_command_surface(plugin_root),
        _check_command_frontmatter(plugin_root),
        _check_forbidden_tokens(plugin_root),
        _check_skill_surface(plugin_root),
    ]

    if args.get("json"):
        sys.stdout.write(
            json.dumps({"plugin": str(plugin_root), "results": results}, indent=2) + "\n"
        )
    else:
        sys.stdout.write(_fmt_markdown(results, plugin_root))
    any_fail = any(not r["pass"] for r in results)
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
