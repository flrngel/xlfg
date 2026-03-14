from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


def repo_root(start: Path | None = None) -> Path:
    """Return the repository root.

    Strategy:
    - Walk upwards from start (default: cwd) until we find a .git directory.
    - If not found, return the start directory.
    """

    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / ".git").exists():
            return p
    return cur


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_write(path: Path, content: str) -> bool:
    """Write a file only if it does not exist.

    Returns True if created, False if already existed.
    """
    if path.exists():
        return False
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def write_text_if_changed(path: Path, content: str) -> bool:
    """Write content when the path is missing or the content changed.

    Returns True when a write happened.
    """
    ensure_dir(path.parent)
    try:
        existing = path.read_text(encoding="utf-8")
    except Exception:
        existing = None
    if existing == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def append_unique_line(file_path: Path, line: str) -> bool:
    """Append a line to a file if it is not already present.

    Returns True if appended, False if already present.
    """
    existing = ""
    if file_path.exists():
        existing = file_path.read_text(encoding="utf-8")
    if line.strip() in {l.strip() for l in existing.splitlines()}:
        return False
    ensure_dir(file_path.parent)
    with file_path.open("a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(line.rstrip("\n") + "\n")
    return True


_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_len: int = 32) -> str:
    s = text.strip().lower()
    s = _slug_re.sub("-", s)
    s = s.strip("-")
    if not s:
        s = "run"
    return s[:max_len]
