#!/usr/bin/env python3
"""Lightweight linter for Claude Code plugin markdown frontmatter.

Goals:
- Catch missing/invalid frontmatter fields
- Keep description fields short to avoid Claude Code context-budget drops
- Prevent main-entrypoint command/skill collisions
- Catch plugin-path references that break after install
- Avoid plugin `name:` frontmatter until upstream namespace quirks settle
- Keep `/xlfg` wired to hidden phase skills and current Claude Code tool names

This intentionally avoids external dependencies.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "xlfg-engineering"

FRONTMATTER_RE = re.compile(r"^---\s*$")
KV_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")
BROKEN_PLUGIN_PATH_RE = re.compile(r"plugins/xlfg-engineering/")
LEGACY_TASK_RE = re.compile(r"\bTask\b")
PHASE_SKILLS = [
    "xlfg-recall-phase",
    "xlfg-context-phase",
    "xlfg-plan-phase",
    "xlfg-implement-phase",
    "xlfg-verify-phase",
    "xlfg-review-phase",
    "xlfg-compound-phase",
]


@dataclass
class LintIssue:
    path: Path
    message: str


def parse_frontmatter(text: str) -> Optional[Dict[str, str]]:
    lines = text.splitlines()
    if not lines or not FRONTMATTER_RE.match(lines[0]):
        return None

    fm: Dict[str, str] = {}
    end = None
    for i in range(1, len(lines)):
        if FRONTMATTER_RE.match(lines[i]):
            end = i
            break

    if end is None:
        return None

    for line in lines[1:end]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = KV_RE.match(line)
        if not m:
            continue
        key, raw_val = m.group(1), m.group(2).strip()
        if (raw_val.startswith('"') and raw_val.endswith('"')) or (
            raw_val.startswith("'") and raw_val.endswith("'")
        ):
            raw_val = raw_val[1:-1]
        fm[key] = raw_val

    return fm


def lint_frontmatter(path: Path, fm: Optional[Dict[str, str]], kind: str) -> List[LintIssue]:
    issues: List[LintIssue] = []
    if fm is None:
        issues.append(LintIssue(path, f"Missing YAML frontmatter for {kind}"))
        return issues

    desc = fm.get("description", "").strip()
    if not desc:
        issues.append(LintIssue(path, f"Frontmatter missing 'description' for {kind}"))

    max_len = 220
    if desc and len(desc) > max_len:
        issues.append(
            LintIssue(
                path,
                f"description too long ({len(desc)} chars > {max_len}). Keep it short to avoid context-budget drops.",
            )
        )

    if fm.get("name"):
        issues.append(
            LintIssue(
                path,
                "Avoid `name:` frontmatter in plugin commands/skills; file or directory names are safer for current Claude Code namespacing.",
            )
        )

    return issues


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    if not PLUGIN_ROOT.exists():
        print(f"ERROR: plugin root not found: {PLUGIN_ROOT}")
        return 2

    issues: List[LintIssue] = []

    command_names = {p.stem for p in sorted((PLUGIN_ROOT / "commands").glob("*.md"))}
    skill_names = {p.parent.name for p in sorted((PLUGIN_ROOT / "skills").rglob("SKILL.md"))}
    collisions = sorted(command_names & skill_names)
    for name in collisions:
        issues.append(
            LintIssue(
                PLUGIN_ROOT,
                f"Main slash-name collision detected for '{name}'. Do not ship both commands/{name}.md and skills/{name}/SKILL.md in the plugin.",
            )
        )

    for p in sorted((PLUGIN_ROOT / "commands").glob("*.md")):
        text = _load_text(p)
        fm = parse_frontmatter(text)
        issues.extend(lint_frontmatter(p, fm, "command"))
        if BROKEN_PLUGIN_PATH_RE.search(text):
            issues.append(LintIssue(p, "Do not reference repo-relative plugin paths from a command; installed plugins are not laid out like the source repo."))
        if LEGACY_TASK_RE.search(text) and "Skill(" not in text and p.name == "xlfg.md":
            issues.append(LintIssue(p, "Main /xlfg entrypoint should batch hidden skills via the modern Skill tool, not rely on stale Task wording."))

    main_entry = _load_text(PLUGIN_ROOT / "commands" / "xlfg.md")
    for phase in PHASE_SKILLS:
        if phase not in main_entry:
            issues.append(LintIssue(PLUGIN_ROOT / "commands" / "xlfg.md", f"Main /xlfg entrypoint must reference hidden phase skill '{phase}'."))

    for phase in PHASE_SKILLS:
        phase_skill = PLUGIN_ROOT / "skills" / phase / "SKILL.md"
        if not phase_skill.exists():
            issues.append(LintIssue(phase_skill, "Missing hidden phase skill."))

    for p in sorted((PLUGIN_ROOT / "agents").rglob("*.md")):
        fm = parse_frontmatter(_load_text(p))
        # agent descriptions still matter, but `name` is fine here and often useful
        if fm is None:
            issues.append(LintIssue(p, "Missing YAML frontmatter for agent"))
            continue
        desc = fm.get("description", "").strip()
        if not desc:
            issues.append(LintIssue(p, "Frontmatter missing 'description' for agent"))
        if desc and len(desc) > 220:
            issues.append(LintIssue(p, f"description too long ({len(desc)} chars > 220)."))

    for skill_dir in sorted((PLUGIN_ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            issues.append(LintIssue(skill_dir, "Missing SKILL.md"))
            continue
        text = _load_text(skill_md)
        fm = parse_frontmatter(text)
        issues.extend(lint_frontmatter(skill_md, fm, "skill"))
        if BROKEN_PLUGIN_PATH_RE.search(text):
            issues.append(LintIssue(skill_md, "Do not reference repo-relative plugin paths from a skill; installed plugins are not laid out like the source repo."))
        if fm and fm.get("user-invocable") != "false" and skill_dir.name.startswith("xlfg-"):
            issues.append(LintIssue(skill_md, "Support and phase skills should usually be `user-invocable: false` so the main /xlfg entrypoint stays clear."))

    if issues:
        print("xlfg plugin lint failed:\n")
        for iss in issues:
            rel = iss.path.relative_to(Path.cwd()) if iss.path.is_absolute() else iss.path
            print(f"- {rel}: {iss.message}")
        return 1

    print("xlfg plugin lint OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
