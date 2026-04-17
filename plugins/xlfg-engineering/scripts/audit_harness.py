#!/usr/bin/env python3
"""xlfg audit-harness — deterministic self-check of the xlfg plugin.

Replaces the previous /xlfg-audit slash command body. Every check
here is a file read, regex match, JSON parse, or word count — none
of it needed an LLM, and none of it should pretend it did.

Maintainer tool. Wire into pre-push, npm scripts, or CI. The
/xlfg-audit slash command is now reserved for the per-run user
post-mortem (see post_mortem.py).

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

PUBLIC_COMMANDS = ("xlfg.md", "xlfg-debug.md")

CODEX_PUBLIC_SKILLS = ("xlfg/SKILL.md", "xlfg-debug/SKILL.md")

CODEX_FORBIDDEN_TOKENS = (
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
)

_FRONTMATTER_KV_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
_EXIT_PLAN_MODE_RE = re.compile(
    r"PermissionRequest:\s*\n[\s\S]*?matcher:\s*\"ExitPlanMode\"[\s\S]*?behavior\":\s*\"allow\""
)
_STALE_TASK_RE = re.compile(r"^Task(\s*\(|$)")


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


def _read_json(p: Path) -> object:
    return json.loads(p.read_text(encoding="utf-8"))


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict[str, object]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {"raw": "", "fields": {}}
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end < 0:
        return {"raw": "", "fields": {}}
    raw = "\n".join(lines[1:end])
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        m = _FRONTMATTER_KV_RE.match(line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return {"raw": raw, "fields": fields}


def _word_count(p: Path) -> int:
    try:
        text = _read_text(p)
    except OSError:
        return 0
    return len(re.findall(r"\S+", text))


def _list_agent_files(plugin_root: Path) -> list[Path]:
    root = plugin_root / "agents"
    if not root.exists():
        return []
    out: list[Path] = []
    for entry in root.iterdir():
        if entry.is_dir() and entry.name == "_shared":
            continue
        if entry.is_dir():
            for sub in entry.rglob("*.md"):
                out.append(sub)
        elif entry.is_file() and entry.name.endswith(".md"):
            out.append(entry)
    return out


def _list_runtime_markdown(plugin_root: Path) -> list[Path]:
    out: list[Path] = []
    for sub in ("commands", "skills", "agents"):
        root = plugin_root / sub
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and (path.name.endswith(".md") or path.name == "SKILL.md"):
                out.append(path)
    return out


def _check_version_sync(plugin_root: Path) -> dict[str, object]:
    manifests = (
        ".claude-plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        ".codex-plugin/plugin.json",
    )
    versions: dict[str, str | None] = {}
    for m in manifests:
        p = plugin_root / m
        try:
            versions[m] = _read_json(p).get("version")  # type: ignore[union-attr]
        except (OSError, json.JSONDecodeError, AttributeError):
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


def _check_sdlc_coverage(plugin_root: Path) -> dict[str, object]:
    present: list[str] = []
    missing: list[str] = []
    for phase in EXPECTED_PHASE_SKILLS:
        skill_path = plugin_root / "skills" / phase / "SKILL.md"
        (present if skill_path.exists() else missing).append(phase)
    score = len(present) / len(EXPECTED_PHASE_SKILLS)
    note = (
        f"missing: {', '.join(missing)}"
        if missing
        else f"{len(present)}/{len(EXPECTED_PHASE_SKILLS)} phases present"
    )
    return {
        "id": 2,
        "name": "SDLC coverage",
        "pass": not missing,
        "score": score,
        "note": note,
        "detail": {"present": present, "missing": missing},
    }


def _check_workflow_load(plugin_root: Path) -> dict[str, object]:
    counts: dict[str, int] = {}
    for cmd in PUBLIC_COMMANDS:
        counts[f"commands/{cmd}"] = _word_count(plugin_root / "commands" / cmd)
    for phase in EXPECTED_PHASE_SKILLS:
        counts[f"skills/{phase}/SKILL.md"] = _word_count(
            plugin_root / "skills" / phase / "SKILL.md"
        )
    total = sum(counts.values())
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    top3 = ranked[:3]
    top_label = f"{top3[0][0]} ({top3[0][1]})" if top3 else "(none)"
    return {
        "id": 3,
        "name": "workflow load",
        "pass": True,
        "score": total,
        "note": f"{total} total words; top driver: {top_label}",
        "detail": {"counts": counts, "total": total, "top3": top3},
    }


def _check_claude_code_compat(plugin_root: Path) -> dict[str, object]:
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
        fields: dict[str, str] = fm["fields"]  # type: ignore[assignment]
        checks = {
            "allowed-tools present": "allowed-tools" in fields,
            "effort=high": fields.get("effort") == "high",
            "disable-model-invocation=true": fields.get("disable-model-invocation") == "true",
            "PermissionRequest→ExitPlanMode auto-allow": bool(_EXIT_PLAN_MODE_RE.search(text)),
        }
        for label, ok in checks.items():
            assertions += 1
            if ok:
                passes += 1
            else:
                failures.append(f"commands/{cmd}: {label} missing")

    for phase in EXPECTED_PHASE_SKILLS:
        p = plugin_root / "skills" / phase / "SKILL.md"
        try:
            text = _read_text(p)
        except OSError:
            failures.append(f"skills/{phase}: missing")
            assertions += 2
            continue
        fm = _frontmatter(text)
        fields = fm["fields"]  # type: ignore[assignment]
        assertions += 1
        if fields.get("user-invocable") == "false":
            passes += 1
        else:
            failures.append(f"skills/{phase}: user-invocable!=false")
        assertions += 1
        if "name" not in fields:
            passes += 1
        else:
            failures.append(
                f"skills/{phase}: name field present (must be omitted for hidden skills)"
            )

    audit_cmd = (plugin_root / "commands" / "xlfg-audit.md").resolve()
    for file in _list_runtime_markdown(plugin_root):
        if file.resolve() == audit_cmd:
            continue
        text = _read_text(file)
        fm = _frontmatter(text)
        fields = fm["fields"]  # type: ignore[assignment]
        tools_field = fields.get("tools") or fields.get("allowed-tools") or ""
        tool_list = [s.strip() for s in tools_field.split(",")]
        has_stale_task = any(_STALE_TASK_RE.match(t) for t in tool_list)
        assertions += 1
        if not has_stale_task:
            passes += 1
        else:
            failures.append(
                f"{file.relative_to(plugin_root)}: stale bare 'Task' in tools field"
            )
        assertions += 1
        if "query-contract.md" not in text:
            passes += 1
        else:
            failures.append(
                f"{file.relative_to(plugin_root)}: forbidden 'query-contract.md' reference"
            )

    for agent_path in _list_agent_files(plugin_root):
        text = _read_text(agent_path)
        fm = _frontmatter(text)
        fields = fm["fields"]  # type: ignore[assignment]
        assertions += 1
        try:
            turns = int(fields.get("maxTurns", ""))
            turns_ok = turns <= 150
        except (TypeError, ValueError):
            turns_ok = False
        if turns_ok:
            passes += 1
        else:
            failures.append(
                f"{agent_path.relative_to(plugin_root)}: maxTurns missing or > 150 "
                f"(got {fields.get('maxTurns')})"
            )
        assertions += 1
        tools = fields.get("tools", "")
        if not re.search(r"\bAgent\b", tools) and not re.search(r"\bSendMessage\b", tools):
            passes += 1
        else:
            failures.append(
                f"{agent_path.relative_to(plugin_root)}: leaf-worker rule violated "
                "(Agent/SendMessage in tools)"
            )

    score = passes / assertions if assertions else 1
    note = (
        f"{passes}/{assertions} assertions pass; {len(failures)} failure(s)"
        if failures
        else f"{passes}/{assertions} assertions pass"
    )
    return {
        "id": 4,
        "name": "Claude Code compatibility",
        "pass": not failures,
        "score": score,
        "note": note,
        "detail": {"failures": failures, "assertions": assertions, "passes": passes},
    }


def _check_codex_surface(plugin_root: Path) -> dict[str, object]:
    failures: list[str] = []
    for rel in CODEX_PUBLIC_SKILLS:
        p = plugin_root / "codex" / "skills" / rel
        if not p.exists():
            failures.append(f"missing codex/skills/{rel}")
            continue
        text = _read_text(p)
        for tok in CODEX_FORBIDDEN_TOKENS:
            if tok in text:
                failures.append(f"codex/skills/{rel}: contains Claude-only token '{tok}'")
    return {
        "id": 5,
        "name": "Codex surface integrity",
        "pass": not failures,
        "score": 1 if not failures else 0,
        "note": f"{len(failures)} issue(s)" if failures else "2 codex skills clean",
        "detail": {"failures": failures},
    }


def _check_scaffold_consistency(plugin_root: Path, cwd: Path) -> dict[str, object]:
    meta_path = cwd / "docs/xlfg/meta.json"
    if not meta_path.exists():
        return {
            "id": 6,
            "name": "scaffold self-consistency",
            "pass": True,
            "score": 1,
            "note": "no scaffold in cwd (not an xlfg-initialized project)",
            "detail": {"metaPath": str(meta_path), "present": False},
        }
    try:
        tool_version = _read_json(meta_path).get("tool_version")  # type: ignore[union-attr]
    except (OSError, json.JSONDecodeError, AttributeError):
        tool_version = None
    try:
        claude_plugin_version = _read_json(plugin_root / ".claude-plugin/plugin.json").get(
            "version"
        )  # type: ignore[union-attr]
    except (OSError, json.JSONDecodeError, AttributeError):
        claude_plugin_version = None
    passed = tool_version == claude_plugin_version and tool_version is not None
    note = (
        f"meta.tool_version matches plugin ({claude_plugin_version})"
        if passed
        else f"drift: meta.tool_version={tool_version}, plugin={claude_plugin_version}"
    )
    return {
        "id": 6,
        "name": "scaffold self-consistency",
        "pass": passed,
        "score": 1 if passed else 0,
        "note": note,
        "detail": {"toolVersion": tool_version, "claudePluginVersion": claude_plugin_version},
    }


def _fmt_markdown(results: list[dict[str, object]], plugin_root: Path) -> str:
    lines: list[str] = []
    lines.append("# xlfg audit-harness")
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

    cwd = Path.cwd()
    results = [
        _check_version_sync(plugin_root),
        _check_sdlc_coverage(plugin_root),
        _check_workflow_load(plugin_root),
        _check_claude_code_compat(plugin_root),
        _check_codex_surface(plugin_root),
        _check_scaffold_consistency(plugin_root, cwd),
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
