from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from .util import ensure_dir, slugify, write_text_if_changed


def _run_git(root: Path, *args: str) -> Optional[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _resolve_path(root: Path, value: Optional[str]) -> Optional[Path]:
    if not value:
        return None
    p = Path(value)
    if p.is_absolute():
        return p.resolve()
    return (root / p).resolve()


def _default_branch(root: Path) -> Optional[str]:
    origin_head = _run_git(root, "symbolic-ref", "refs/remotes/origin/HEAD")
    if origin_head and "/" in origin_head:
        return origin_head.rsplit("/", 1)[-1]
    for candidate in ("main", "master", "trunk", "develop"):
        if _run_git(root, "show-ref", "--verify", f"refs/heads/{candidate}") is not None:
            return candidate
        if _run_git(root, "show-ref", "--verify", f"refs/remotes/origin/{candidate}") is not None:
            return candidate
    return None


def detect_git_context(root: Path) -> Dict[str, Any]:
    top = _run_git(root, "rev-parse", "--show-toplevel")
    branch = _run_git(root, "symbolic-ref", "--quiet", "--short", "HEAD") or _run_git(root, "rev-parse", "--abbrev-ref", "HEAD")
    git_dir_raw = _run_git(root, "rev-parse", "--git-dir")
    common_dir_raw = _run_git(root, "rev-parse", "--git-common-dir")
    head_sha = _run_git(root, "rev-parse", "--short", "HEAD")

    git_dir = _resolve_path(root, git_dir_raw)
    common_dir = _resolve_path(root, common_dir_raw)

    worktree_name = None
    if git_dir and common_dir:
        try:
            rel = git_dir.relative_to(common_dir)
            parts = rel.parts
            if len(parts) >= 2 and parts[0] == "worktrees":
                worktree_name = parts[1]
        except Exception:
            worktree_name = None
    if not worktree_name:
        worktree_name = "main-worktree"

    attached_head = branch not in {None, "HEAD"}
    default_branch = _default_branch(root)
    branch_name = branch if attached_head else None
    branch_slug = slugify(branch_name or worktree_name or "detached", max_len=48)
    worktree_id = slugify(worktree_name or branch_slug or "main-worktree", max_len=48)

    return {
        "repo_root": str(Path(top).resolve()) if top else str(root.resolve()),
        "git_dir": str(git_dir) if git_dir else None,
        "git_common_dir": str(common_dir) if common_dir else None,
        "branch": branch_name,
        "branch_slug": branch_slug,
        "default_branch": default_branch,
        "default_branch_slug": slugify(default_branch, max_len=48) if default_branch else None,
        "is_default_branch": bool(branch_name and default_branch and branch_name == default_branch),
        "attached_head": attached_head,
        "head_sha": head_sha,
        "worktree_name": worktree_name,
        "worktree_id": worktree_id,
        "knowledge_write_namespace": branch_slug,
        "knowledge_write_mode": "branch-safe-cards",
        "knowledge_read_mode": "local-views",
    }


def write_worktree_context(root: Path) -> Dict[str, Any]:
    data = detect_git_context(root)
    path = root / ".xlfg" / "worktree.json"
    changed = write_text_if_changed(path, json.dumps(data, indent=2) + "\n")
    return {"path": str(path.relative_to(root)), "changed": changed, "data": data}
