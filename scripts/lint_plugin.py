#!/usr/bin/env python3
"""Lightweight linter for Claude Code plugin markdown frontmatter.

Goals:
- Catch missing/invalid frontmatter fields
- Keep description fields short to avoid Claude Code context-budget drops

This intentionally avoids external dependencies.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "xlfg-engineering"

FRONTMATTER_RE = re.compile(r"^---\s*$")
KV_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")


@dataclass
class LintIssue:
    path: Path
    message: str


def parse_frontmatter(text: str) -> Optional[Dict[str, str]]:
    """Parse simple YAML frontmatter with scalar key: value lines.

    Returns None if no frontmatter.
    """
    lines = text.splitlines()
    if not lines or not FRONTMATTER_RE.match(lines[0]):
        return None

    fm: Dict[str, str] = {}
    # find closing ---
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
            # ignore non scalar YAML constructs in this minimal linter
            continue
        key, raw_val = m.group(1), m.group(2).strip()
        # strip quotes
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

    name = fm.get("name", "").strip()
    desc = fm.get("description", "").strip()

    if not name:
        issues.append(LintIssue(path, f"Frontmatter missing 'name' for {kind}"))
    if not desc:
        issues.append(LintIssue(path, f"Frontmatter missing 'description' for {kind}"))

    # description length gate (soft but helpful)
    max_len = 220
    if desc and len(desc) > max_len:
        issues.append(
            LintIssue(
                path,
                f"description too long ({len(desc)} chars > {max_len}). Keep it short to avoid context-budget drops.",
            )
        )

    return issues


def main() -> int:
    if not PLUGIN_ROOT.exists():
        print(f"ERROR: plugin root not found: {PLUGIN_ROOT}")
        return 2

    issues: List[LintIssue] = []

    # commands
    for p in sorted((PLUGIN_ROOT / "commands").glob("*.md")):
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        issues.extend(lint_frontmatter(p, fm, "command"))

    # agents
    for p in sorted((PLUGIN_ROOT / "agents").rglob("*.md")):
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        issues.extend(lint_frontmatter(p, fm, "agent"))

    # skills
    for skill_dir in sorted((PLUGIN_ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            issues.append(LintIssue(skill_dir, "Missing SKILL.md"))
            continue
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        issues.extend(lint_frontmatter(skill_md, fm, "skill"))

        # skill name should match directory name
        if fm and fm.get("name") and fm.get("name") != skill_dir.name:
            issues.append(
                LintIssue(
                    skill_md,
                    f"Skill name '{fm.get('name')}' does not match directory '{skill_dir.name}'",
                )
            )

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
